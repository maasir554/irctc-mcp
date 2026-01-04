import os
from dotenv import load_dotenv
import httpx
from pnr_schemas import Passenger, PNRData, RailwaysAPIResponse
from typing import List
from status_decoders import decode_ticket_status, decode_berth

load_dotenv()

IRCTC_PNR_API_BASE = os.getenv("IRCTC_PNR_API_BASE")
IRCTC_PNR_API_KEY = os.getenv("IRCTC_PNR_API_KEY")
IRCTC_PNR_API_HOST = os.getenv("IRCTC_PNR_API_HOST")
IRCTC_PNR_API_HEADER_HOST = os.getenv("IRCTC_PNR_API_HEADER_HOST")
IRCTC_PNR_API_HEADER_KEY = os.getenv("IRCTC_PNR_API_HEADER_KEY")



async def fetch_pnr_details(pnr_number: str) -> RailwaysAPIResponse | None:
    url = f"{IRCTC_PNR_API_BASE}/{pnr_number}"
    
    assert IRCTC_PNR_API_BASE is not None
    assert IRCTC_PNR_API_KEY is not None
    assert IRCTC_PNR_API_HOST is not None
    assert IRCTC_PNR_API_HEADER_HOST is not None
    assert IRCTC_PNR_API_HEADER_KEY is not None
    
    headers = {
        IRCTC_PNR_API_HEADER_KEY: IRCTC_PNR_API_KEY,
        IRCTC_PNR_API_HEADER_HOST: IRCTC_PNR_API_HOST
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return RailwaysAPIResponse(**response.json())
        except Exception:
            return None


def checkConfirmStatus(passengers:List[Passenger])->str:
    response = ""
    for p in passengers:        
        status = decode_ticket_status(p.currentStatus)
        response += f"Passenger-{p.passengerSerialNumber}: {status}\n"
    
    return response if response != "" else "Confirm status not available."

def getCoachAndBerth(passengers:List[Passenger])->str:
    response = ""
    for p in passengers:
        coach_and_birth = "Not Confirmed"

        if p.currentStatus in ['CNF', 'RAC']:
            coach_and_birth= f"Coach: {p.currentCoachId}, Berth: {p.currentBerthNo} - ({decode_berth(p.currentBerthCode)})" 
        
        response += f"Passenger-{p.passengerSerialNumber}: {coach_and_birth}\n"

    return response if response != "" else "Coach & Birth not available"

def getWaitListPosition(passengers:List[Passenger]) -> str:
    """
    If any passenger's current status is not onfirmed or RAC, then get 
    its waitlist position.
    
    :param passengers: Description
    :type passengers: List[Passenger]
    :return: Description
    :rtype: str
    """
    response = ""
    for p in passengers:
        position = str(p.bookingStatusDetails).split('/')
        if p.currentStatus in ['CNF', 'RAC']:
            position = "Already Confirmed"
        response += f"Passenger-{p.passengerSerialNumber}: {position[1]} in {decode_ticket_status(position[0])}({position[0]})\n"
    return response if response != "" else "Unable to get waitlist position."

def getJourneyOverview(pnr_info: RailwaysAPIResponse | None) -> str:
    """
    Get basic info about the journey - source/destination stations, ticket fare, date/time of journey
    
    :param pnr_info: Description
    :type pnr_info: RailwaysAPIResponse | None
    :return: Description
    :rtype: str
    """
    if not pnr_info:
        return "Failed to receive source API response"
    if not pnr_info.data:
        return "Problem in API."
    
    assert pnr_info and pnr_info.data is not None
    data = pnr_info.data
    response = ""
    response += f"Date of journey: {data.dateOfJourney}\n"
    response += f"Source station: {data.sourceStation}\n"
    response += f"Destination station: {data.destinationStation}\n"
    response += f"Booked on: {data.bookingDate}\n"
    response += f"Scheduled completion at: {data.arrivalDate}\n"
    response += f"Ticket fare: {data.ticketFare}\n"
    response += f"Journey class: {data.journeyClass}\n"
    response += f"Number of passengers: {data.numberOfpassenger}"

    return response

# example pnr no: 8641842491
