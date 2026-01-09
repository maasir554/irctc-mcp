import httpx
from new_pnr_schema import PNRResponse, PassengerStatus
import os
from datetime import datetime, date
from dotenv import load_dotenv
from urllib.parse import unquote
from status_decoders import decode_ticket_status, decode_berth

load_dotenv()

PNR_API_PATH = os.getenv("NEW_PNR_API_PATH")
PNR_API_KEY_NAME = os.getenv("NEW_PNR_API_KEY_NAME")


def is_confirmed_or_rac(status: str) -> bool:
    """Check if a status indicates confirmed or RAC."""
    status_upper = status.upper().strip()
    return status_upper.startswith('CNF') or status_upper.startswith('RAC')

def fetch_pnr_status(pnr_no: str) -> PNRResponse | None:
    """
    Fetch PNR status from Live API.
    
    Args:
        pnr_no: The PNR number to check (must be 10 digits)
        
    Returns:
        PNRResponse object containing the PNR status data, or None if PNR is invalid
    """
    # Validate PNR length - must be exactly 10 digits
    if len(pnr_no) != 10 or not pnr_no.isdigit():
        return None
    
    assert PNR_API_PATH is not None
    assert PNR_API_KEY_NAME is not None
    url = PNR_API_PATH
    
    with httpx.Client() as client:
        initial_response = client.get(url)
        api_key = client.cookies.get(PNR_API_KEY_NAME)

        if not api_key:
            raise ValueError("Failed to retrieve XSRF-TOKEN from cookies", initial_response)
        
        decoded_token = unquote(api_key)
        headers = {
            f'X-{PNR_API_KEY_NAME}': decoded_token,
        }
        
        body = {"pnr": pnr_no}
        
        response = client.post(url, json=body, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if API returned an error (PNR not found)
        if data.get("status") is False:
            return None
        
        return PNRResponse(**data)


def get_train_start_date(pnr_status: PNRResponse | None) -> date | None:
    """
    Get the train start date (when the train departed from its source station) from PNR status.
    
    Args:
        pnr_status: The PNRResponse object from fetch_pnr_status
        
    Returns:
        A date object representing the source departure date, or None if not available
    """
    if pnr_status is None or pnr_status.data is None:
        return None
    
    try:
        return datetime.strptime(pnr_status.data.SourceDoj, "%d-%m-%Y").date()
    except (ValueError, AttributeError):
        return None


def get_train_number(pnr_status: PNRResponse | None) -> str | None:
    """
    Get the train number from PNR status.
    
    Args:
        pnr_status: The PNRResponse object from fetch_pnr_status
        
    Returns:
        The train number as a string, or None if not available
    """
    if pnr_status is None or pnr_status.data is None:
        return None
    
    return pnr_status.data.TrainNo


def check_confirm_status(pnr_status: PNRResponse | None) -> str:
    """
    Check the confirmation status of all passengers in the PNR.
    
    Args:
        pnr_status: The PNRResponse object from fetch_pnr_status
        
    Returns:
        A formatted string with each passenger's confirmation status
    """
    if pnr_status is None or pnr_status.data is None:
        return "PNR data not available."
    
    passengers = pnr_status.data.PassengerStatus
    if not passengers:
        return "No passenger information available."
    
    response = ""
    for p in passengers:
        # Use CurrentStatusNew which contains the full formatted status
        response += f"Passenger-{p.Number}: {p.CurrentStatusNew}\n"
    
    return response if response else "Confirm status not available."


def get_coach_and_berth(pnr_status: PNRResponse | None) -> str:
    """
    Get the coach and berth details for all passengers.
    
    Args:
        pnr_status: The PNRResponse object from fetch_pnr_status
        
    Returns:
        A formatted string with each passenger's coach and berth information
    """
    if pnr_status is None or pnr_status.data is None:
        return "PNR data not available."
    
    passengers = pnr_status.data.PassengerStatus
    if not passengers:
        return "No passenger information available."
    
    response = ""
    for p in passengers:
        if is_confirmed_or_rac(p.CurrentStatus):
            berth_desc = decode_berth(p.CurrentBerthCode) if p.CurrentBerthCode else ""
            coach_and_berth = f"Coach: {p.CurrentCoachId}, Berth: {p.CurrentBerthNo}"
            if berth_desc:
                coach_and_berth += f" ({berth_desc})"
        else:
            coach_and_berth = "Not Confirmed"
        
        response += f"Passenger-{p.Number}: {coach_and_berth}\n"
    
    return response if response else "Coach & Berth not available."


def get_waitlist_position(pnr_status: PNRResponse | None) -> str:
    """
    Get the waitlist position for passengers who are not confirmed or RAC.
    
    Args:
        pnr_status: The PNRResponse object from fetch_pnr_status
        
    Returns:
        A formatted string with each passenger's waitlist position
    """
    if pnr_status is None or pnr_status.data is None:
        return "PNR data not available."
    
    passengers = pnr_status.data.PassengerStatus
    if not passengers:
        return "No passenger information available."
    
    response = ""
    for p in passengers:
        if is_confirmed_or_rac(p.CurrentStatus):
            position = "Already Confirmed/RAC"
        else:
            # Parse booking status to get waitlist position
            # BookingStatusNew contains the formatted status like "WL/12" or "GNWL/5"
            booking_parts = p.BookingStatusNew.split('/') if p.BookingStatusNew else []
            if len(booking_parts) >= 2:
                status_type = booking_parts[0]
                position_num = booking_parts[1]
                position = f"Position {position_num} in {decode_ticket_status(status_type)} ({status_type})"
            else:
                position = p.BookingStatusNew or "Unknown"
        
        response += f"Passenger-{p.Number}: {position}\n"
    
    return response if response else "Unable to get waitlist position."


def get_journey_overview(pnr_status: PNRResponse | None) -> str:
    """
    Get basic info about the journey - source/destination stations, ticket fare, date/time of journey.
    
    Args:
        pnr_status: The PNRResponse object from fetch_pnr_status
        
    Returns:
        A formatted string with journey overview details
    """
    if pnr_status is None:
        return "Failed to receive API response."
    if pnr_status.data is None:
        return "PNR data not available."
    
    data = pnr_status.data
    
    response = f"Train: {data.TrainName} ({data.TrainNo})\n"
    response += f"Date of Journey: {data.Doj}\n"
    response += f"Source Station: {data.SourceName} ({data.From})\n"
    response += f"Destination Station: {data.DestinationName} ({data.To})\n"
    response += f"Boarding Point: {data.BoardingStationName} ({data.BoardingPoint})\n"
    response += f"Reservation Upto: {data.ReservationUptoName} ({data.ReservationUpto})\n"
    response += f"Departure Time: {data.DepartureTime}\n"
    response += f"Arrival Time: {data.ArrivalTime}\n"
    response += f"Duration: {data.Duration}\n"
    response += f"Booking Date: {data.BookingDate}\n"
    response += f"Ticket Fare: ₹{data.TicketFare}\n"
    response += f"Journey Class: {data.Class}\n"
    response += f"Quota: {data.Quota}\n"
    response += f"Number of Passengers: {data.PassengerCount}\n"
    response += f"Chart Prepared: {'Yes' if data.ChartPrepared else 'No'}"
    
    if data.HasPantry:
        response += f"\nPantry Available: Yes"
    
    if data.TrainCancelledFlag:
        response += f"\n⚠️ TRAIN CANCELLED"
    
    return response


def get_passenger_summary(pnr_status: PNRResponse | None) -> str:
    """
    Get a summary of all passengers with their current status, coach, and berth.
    
    Args:
        pnr_status: The PNRResponse object from fetch_pnr_status
        
    Returns:
        A formatted string summarizing all passenger details
    """
    if pnr_status is None or pnr_status.data is None:
        return "PNR data not available."
    
    passengers = pnr_status.data.PassengerStatus
    if not passengers:
        return "No passenger information available."
    
    response = f"Passengers ({len(passengers)}):\n\n"
    
    for p in passengers:
        response += f"Passenger {p.Number}:\n"
        response += f"  Booking Status: {p.BookingStatusNew}\n"
        response += f"  Current Status: {p.CurrentStatusNew}\n"
        
        if is_confirmed_or_rac(p.CurrentStatus):
            berth_desc = decode_berth(p.CurrentBerthCode) if p.CurrentBerthCode else ""
            coach_info = f"  Coach: {p.CurrentCoachId}, Berth: {p.CurrentBerthNo}"
            if berth_desc:
                coach_info += f" ({berth_desc})"
            response += coach_info + "\n"
        
        if p.Prediction and p.Prediction != 'CNF':
            response += f"  Prediction: {p.Prediction}"
            if p.PredictionPercentage:
                response += f" ({p.PredictionPercentage}%)"
            response += "\n"
        
        response += "\n"
    
    return response.strip()


def get_pnr_summary(pnr_status: PNRResponse | None) -> str:
    """
    Get a complete summary of the PNR including journey and passenger details.
    
    Args:
        pnr_status: The PNRResponse object from fetch_pnr_status
        
    Returns:
        A formatted string with complete PNR summary
    """
    if pnr_status is None or pnr_status.data is None:
        return "PNR data not available."
    
    data = pnr_status.data
    
    result = f"PNR: {data.Pnr}\n"
    result += f"{'=' * 40}\n\n"
    
    result += f"🚂 {data.TrainName} ({data.TrainNo})\n"
    result += f"📅 {data.Doj}\n"
    result += f"🚉 {data.SourceName} → {data.DestinationName}\n"
    result += f"⏰ {data.DepartureTime} - {data.ArrivalTime} ({data.Duration})\n"
    result += f"🎫 Class: {data.Class} | Quota: {data.Quota}\n"
    result += f"💰 Fare: ₹{data.TicketFare}\n\n"
    
    if data.ChartPrepared:
        result += "✅ Chart Prepared\n\n"
    else:
        result += "⏳ Chart Not Prepared\n\n"
    
    if data.TrainCancelledFlag:
        result += "⚠️ TRAIN CANCELLED\n\n"
    
    result += f"Passengers ({data.PassengerCount}):\n"
    for p in data.PassengerStatus:
        status_upper = p.CurrentStatus.upper().strip()
        if status_upper.startswith('CNF'):
            status_icon = "✅"
        elif status_upper.startswith('RAC'):
            status_icon = "🟡"
        else:
            status_icon = "⏳"
        result += f"  {status_icon} P{p.Number}: {p.CurrentStatusNew}"
        if is_confirmed_or_rac(p.CurrentStatus):
            berth_desc = decode_berth(p.CurrentBerthCode) if p.CurrentBerthCode else ""
            result += f" - {p.CurrentCoachId}/{p.CurrentBerthNo}"
            if berth_desc:
                result += f" ({berth_desc})"
        result += "\n"
    
    return result


