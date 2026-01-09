from fastmcp import FastMCP
from datetime import date
from new_pnr_status import (
    fetch_pnr_status,
    get_train_start_date as get_pnr_train_start_date,
    get_train_number,
    check_confirm_status,
    get_coach_and_berth,
    get_waitlist_position,
    get_journey_overview,
    get_passenger_summary,
    get_pnr_summary,
)
from new_train_status_functions import (
    fetch_new_train_status,
    get_expected_arrival_at_station,
    get_current_train_position,
    get_train_route,
    get_upcoming_stations,
    get_train_summary,
)
# Import older functions for station/train search (not available in new function set)
from train_status_functions import (
    get_station_codes_from_name,
    get_train_numbers_from_name,
)

mcp = FastMCP("Indian Railway Live Info (New)")


def calculate_start_day(train_source_date: date | None) -> int:
    """
    Calculate the start_day parameter for train status API.
    
    Args:
        train_source_date: The date when the train departed from its source station
        
    Returns:
        Number of days ago the train started (0 = today, 1 = yesterday, etc.)
    """
    if train_source_date is None:
        return 0  # Default to today if we can't determine
    
    today = date.today()
    delta = today - train_source_date
    return max(0, delta.days)  # Ensure non-negative


# ==================== PNR Status Tools ====================

@mcp.tool(annotations={"readOnlyHint": True})
def get_confirm_status(pnr_no: str) -> str:
    """
    Get Indian Railways ticket confirmation status of all passengers corresponding to a PNR Number.
    
    Args:
        pnr_no: 10-digit PNR code. (example: 8341223680)
    """
    response = fetch_pnr_status(pnr_no)
    if response is None:
        return "Error fetching PNR status. Please double check the PNR number provided."
    
    return check_confirm_status(response)


@mcp.tool(annotations={"readOnlyHint": True})
def get_coaches_and_berths(pnr_no: str) -> str:
    """
    Get the Coach IDs (or numbers) and the Seat/Berth Details of all passengers corresponding to a PNR Number.

    Args: 
        pnr_no: 10-digit PNR code.
    """
    response = fetch_pnr_status(pnr_no)
    if response is None:
        return "Error fetching PNR status. Please double check the PNR number provided."
    
    return get_coach_and_berth(response)


@mcp.tool(annotations={"readOnlyHint": True})
def get_pnr_waitlist_position(pnr_no: str) -> str:
    """
    Get the updated position of passengers in waiting list corresponding to a PNR Number.

    Args:
        pnr_no: 10-digit PNR Code.
    """
    response = fetch_pnr_status(pnr_no)
    if response is None:
        return "Error fetching PNR status. Please double check the PNR number provided."
    
    return get_waitlist_position(response)


@mcp.tool(annotations={"readOnlyHint": True})
def get_train_no_from_pnr_no(pnr_no: str) -> str:
    """
    Get the train number and name from a PNR Number.

    Args:
        pnr_no: 10-digit PNR Code.
    """
    response = fetch_pnr_status(pnr_no)
    if response is None:
        return "Error fetching PNR status. Please double check the PNR number provided."
    
    train_no = get_train_number(response)
    if train_no is None:
        return "Train number not available in PNR data."
    
    train_name = response.data.TrainName if response.data else "Unknown"
    return f"Train Number: {train_no}, Train Name: {train_name}"


@mcp.tool(annotations={"readOnlyHint": True})
def get_pnr_journey_overview(pnr_no: str) -> str:
    """
    Get basic journey information for a PNR - 
    source/destination stations, ticket fare, date/time of journey,
    journey-class, ticket booked on, no. of passengers.

    Args:
        pnr_no: 10-digit PNR Code.
    """
    response = fetch_pnr_status(pnr_no)
    if response is None:
        return "Error fetching PNR status. Please double check the PNR number provided."
    
    return get_journey_overview(response)


@mcp.tool(annotations={"readOnlyHint": True})
def get_pnr_passenger_summary(pnr_no: str) -> str:
    """
    Get a summary of all passengers with their current status, coach, and berth information.

    Args:
        pnr_no: 10-digit PNR Code.
    """
    response = fetch_pnr_status(pnr_no)
    if response is None:
        return "Error fetching PNR status. Please double check the PNR number provided."
    
    return get_passenger_summary(response)


@mcp.tool(annotations={"readOnlyHint": True})
def get_complete_pnr_summary(pnr_no: str) -> str:
    """
    Get a complete summary of the PNR including journey details and all passenger information.
    This is a comprehensive view of the entire PNR.

    Args:
        pnr_no: 10-digit PNR Code.
    """
    response = fetch_pnr_status(pnr_no)
    if response is None:
        return "Error fetching PNR status. Please double check the PNR number provided."
    
    return get_pnr_summary(response)


# ==================== Train Status Tools ====================

@mcp.tool(annotations={"readOnlyHint": True})
async def get_live_train_status(train_number: str, start_day: int = 0) -> str:
    """
    Get the current live status and position of an Indian Railways train.
    
    Args:
        train_number: The train number (e.g., "12618")
        start_day: Days ago the train started from source (0 = today, 1 = yesterday, 2 = day before, etc.)
    """
    response = await fetch_new_train_status(train_number, start_day)
    if response is None:
        return "Error fetching train status. Please check the train number and start_day."
    
    return get_current_train_position(response)


@mcp.tool(annotations={"readOnlyHint": True})
async def get_train_status_using_pnr(pnr_no: str) -> str:
    """
    Get live train status using PNR number. This automatically calculates the correct
    start_day based on the train's source departure date from the PNR.
    
    This is the recommended way to check train status when you have a PNR,
    as it ensures the correct train run date is used.
    
    Args:
        pnr_no: 10-digit PNR code
    """
    # First fetch PNR status to get train number and source date
    pnr_response = fetch_pnr_status(pnr_no)
    if pnr_response is None:
        return "Error fetching PNR status. Please double check the PNR number provided."
    
    train_no = get_train_number(pnr_response)
    if train_no is None:
        return "Train number not available in PNR data."
    
    # Get train source date and calculate start_day
    train_source_date = get_pnr_train_start_date(pnr_response)
    start_day = calculate_start_day(train_source_date)
    
    # Fetch train status with calculated start_day
    train_response = await fetch_new_train_status(train_no, start_day)
    if train_response is None:
        return f"Error fetching train status for train {train_no}. The train may not be running today or the start_day ({start_day}) may be incorrect."
    
    # Build comprehensive response
    result = f"Train Status for PNR: {pnr_no}\n"
    result += f"Train Source Date: {train_source_date.strftime('%d-%m-%Y') if train_source_date else 'Unknown'}\n"
    result += f"Days since departure: {start_day}\n"
    result += "=" * 40 + "\n\n"
    result += get_current_train_position(train_response)
    
    return result


@mcp.tool(annotations={"readOnlyHint": True})
async def get_train_arrival_at_station(train_number: str, station_code: str, start_day: int = 0) -> str:
    """
    Get the expected arrival time of a train at a specific station.
    
    Args:
        train_number: The train number (e.g., "12618")
        station_code: The station code to check arrival for (e.g., "HWH", "NDLS")
        start_day: Days ago the train started from source (0 = today, 1 = yesterday, etc.)
    """
    response = await fetch_new_train_status(train_number, start_day)
    if response is None:
        return "Error fetching train status. Please check the train number and start_day."
    
    return get_expected_arrival_at_station(response, station_code)


@mcp.tool(annotations={"readOnlyHint": True})
async def get_train_arrival_using_pnr(pnr_no: str, station_code: str) -> str:
    """
    Get expected arrival time at a station using PNR number.
    This automatically calculates the correct start_day based on the train's source departure date.
    
    Args:
        pnr_no: 10-digit PNR code
        station_code: The station code to check arrival for (e.g., "HWH", "NDLS")
    """
    # Fetch PNR to get train number and source date
    pnr_response = fetch_pnr_status(pnr_no)
    if pnr_response is None:
        return "Error fetching PNR status. Please double check the PNR number provided."
    
    train_no = get_train_number(pnr_response)
    if train_no is None:
        return "Train number not available in PNR data."
    
    # Calculate start_day
    train_source_date = get_pnr_train_start_date(pnr_response)
    start_day = calculate_start_day(train_source_date)
    
    # Fetch train status
    train_response = await fetch_new_train_status(train_no, start_day)
    if train_response is None:
        return f"Error fetching train status for train {train_no}."
    
    return get_expected_arrival_at_station(train_response, station_code)


@mcp.tool(annotations={"readOnlyHint": True})
async def get_train_complete_route(train_number: str, start_day: int = 0, include_non_stops: bool = False) -> str:
    """
    Get the complete route of a train showing all stations in sequence.
    
    Args:
        train_number: The train number (e.g., "12618")
        start_day: Days ago the train started from source (0 = today, 1 = yesterday, etc.)
        include_non_stops: Whether to include non-stop stations in the route
    """
    response = await fetch_new_train_status(train_number, start_day)
    if response is None:
        return "Error fetching train status. Please check the train number and start_day."
    
    return get_train_route(response, include_non_stops)


@mcp.tool(annotations={"readOnlyHint": True})
async def get_next_stations(train_number: str, start_day: int = 0, limit: int = 5) -> str:
    """
    Get the next upcoming stations for a train with arrival times and delays.
    
    Args:
        train_number: The train number (e.g., "12618")
        start_day: Days ago the train started from source (0 = today, 1 = yesterday, etc.)
        limit: Maximum number of upcoming stations to show (default: 5)
    """
    response = await fetch_new_train_status(train_number, start_day)
    if response is None:
        return "Error fetching train status. Please check the train number and start_day."
    
    return get_upcoming_stations(response, limit)


@mcp.tool(annotations={"readOnlyHint": True})
async def get_brief_train_summary(train_number: str, start_day: int = 0) -> str:
    """
    Get a brief summary of the train's current status.
    
    Args:
        train_number: The train number (e.g., "12618")
        start_day: Days ago the train started from source (0 = today, 1 = yesterday, etc.)
    """
    response = await fetch_new_train_status(train_number, start_day)
    if response is None:
        return "Error fetching train status. Please check the train number and start_day."
    
    return get_train_summary(response)


# ==================== Search Tools ====================

@mcp.tool(annotations={"readOnlyHint": True})
async def search_station_codes(station_name: str) -> str:
    """
    Search for Indian Railways station codes by station name.
    
    Args:
        station_name: The station name to search for (e.g., "Howrah", "New Delhi", "Rani Kamlapati")
    """
    results = await get_station_codes_from_name(station_name)
    if not results:
        return f"No stations found matching '{station_name}'"
    
    response = f"Stations matching '{station_name}':\n"
    for station in results:
        response += f"  • {station.name} - Code: {station.code}\n"
    return response


@mcp.tool(annotations={"readOnlyHint": True})
async def search_train_numbers(train_name: str) -> str:
    """
    Search for Indian Railways train numbers by train name.
    
    Args:
        train_name: The train name to search for (e.g., "Rajdhani", "Punjab Mail", "Shatabdi")
    """
    results = await get_train_numbers_from_name(train_name)
    if not results:
        return f"No trains found matching '{train_name}'"
    
    response = f"Trains matching '{train_name}':\n"
    for train in results:
        response += f"  • {train.number} - {train.name} ({train.from_stn_code} → {train.to_stn_code})\n"
    return response


# ==================== Combined PNR + Train Status Tools ====================

@mcp.tool(annotations={"readOnlyHint": True})
async def get_full_journey_status(pnr_no: str) -> str:
    """
    Get complete journey status including PNR details and live train position.
    This is the most comprehensive tool that combines PNR information with 
    real-time train tracking, automatically calculating the correct train run date.
    
    Args:
        pnr_no: 10-digit PNR code
    """
    # Fetch PNR status
    pnr_response = fetch_pnr_status(pnr_no)
    if pnr_response is None:
        return "Error fetching PNR status. Please double check the PNR number provided."
    
    # Get PNR summary
    result = get_pnr_summary(pnr_response)
    result += "\n" + "=" * 40 + "\n"
    result += "LIVE TRAIN STATUS\n"
    result += "=" * 40 + "\n\n"
    
    # Get train status
    train_no = get_train_number(pnr_response)
    if train_no is None:
        result += "Train number not available in PNR data."
        return result
    
    # Calculate start_day
    train_source_date = get_pnr_train_start_date(pnr_response)
    start_day = calculate_start_day(train_source_date)
    
    # Check if the journey date is in the future
    if train_source_date and train_source_date > date.today():
        result += f"🚂 Train has not started yet.\n"
        result += f"📅 Scheduled departure from source: {train_source_date.strftime('%d-%m-%Y')}\n"
        result += f"⏳ Days until departure: {(train_source_date - date.today()).days}"
        return result
    
    # Fetch live train status
    train_response = await fetch_new_train_status(train_no, start_day)
    if train_response is None:
        result += f"Unable to fetch live status for train {train_no}.\n"
        result += f"Train source date: {train_source_date.strftime('%d-%m-%Y') if train_source_date else 'Unknown'}\n"
        result += f"The train may have completed its journey or live tracking is unavailable."
        return result
    
    result += get_current_train_position(train_response)
    
    # Add next stops info
    result += "\n\n" + "-" * 40 + "\n"
    result += get_upcoming_stations(train_response, limit=3)
    
    return result


def main():
    mcp.run()


if __name__ == "__main__":
    main()
