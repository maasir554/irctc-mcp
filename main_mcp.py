from fastmcp import FastMCP
from pnr_functions import *
from train_status_functions import (
    fetch_train_status,
    get_station_codes_from_name,
    get_train_numbers_from_name,
    get_expected_arrival_at_station,
    get_current_train_position,
)

mcp = FastMCP("PNR Status")

@mcp.tool
async def get_confirm_status(pnr_no:str)->str:
    """
    Get Indian Railways ticket confirmation Status of all passengers corresponding to a PNR Number.
    
    Args:
        pnr_no: 10-digit PNR code. (exapmple: 8341223680)
    """
    response = await fetch_pnr_details(pnr_no)
    if not response:
        return "Error in fetching API"
    if not response.success or not response.data:
        return f"user should double check the PNR number provided.\n{response.message}"
    
    assert response.data.passengerList is not None
    return checkConfirmStatus(response.data.passengerList)

@mcp.tool
async def get_coaches_and_berths(pnr_no:str)->str:
    """
    Get the Coach IDs (or mumbers) and the Seat/Birth Details of all passengers corresponding to a PNR Number.

    Args: 
        pnr_no: 10-digit PNR code.
    """
    response = await fetch_pnr_details(pnr_no)
    if not response:
        return "Error in fetching API"
    if not response.success or not response.data:
        return f"user should double check the PNR number provided.\n{response.message}"
    
    assert response.data.passengerList is not None
    return getCoachAndBerth(response.data.passengerList)

@mcp.tool
async def get_waitlist_position(pnr_no:str) -> str:
    """
    Get the updated position of passengers in waiting list corresponding to a PNR Number.

    Args:
        pnr_no: 10-digit PNR Code.
    """
    response = await fetch_pnr_details(pnr_no)
    if not response:
        return "Error in fetching API"
    if not response.success or not response.data:
        return f"user should double check the PNR number provided.\n{response.message}"
    
    assert response.data.passengerList is not None
    return getWaitListPosition(response.data.passengerList)

# Tools For geting train status and related tools 

@mcp.tool
async def get_live_train_status(train_number: str, train_date: str) -> str:
    """
    Get the current live status and position of an Indian Railways train.
    
    Args:
        train_number: The train number (e.g., "12618")
        train_date: The journey date in DD-Mon-YYYY format (e.g., "26-Dec-2025")
    """
    response = await fetch_train_status(train_number, train_date)
    if not response:
        return "Error fetching train status. Please check the train number and date."
    if not response.success:
        return "Train status not available. Please verify the train number and date."
    
    return get_current_train_position(response)

@mcp.tool
async def get_train_arrival_at_station(train_number: str, train_date: str, station_code: str) -> str:
    """
    Get the expected arrival time of a train at a specific station.
    
    Args:
        train_number: The train number (e.g., "12618")
        train_date: The journey date in DD-Mon-YYYY format (e.g., "26-Dec-2025")
        station_code: The station code to check arrival for (e.g., "HWH", "NDLS")
    """
    response = await fetch_train_status(train_number, train_date)
    if not response:
        return "Error fetching train status. Please check the train number and date."
    if not response.success:
        return "Train status not available. Please verify the train number and date."
    
    return get_expected_arrival_at_station(response, station_code)

@mcp.tool
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

@mcp.tool
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



def main():
    mcp.run()

if __name__ == "__main__":
    main()
