import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import httpx
from train_status_schemas import TrainStatusResponse, StationSearchResponse, StationSearchResult, TrainSearchResponse, TrainSearchResult

load_dotenv()

TRAIN_STATUS_API_BASE = os.getenv("TRAIN_STATUS_API_BASE")


async def fetch_train_status(train_number: str) -> TrainStatusResponse | None:
    """
    Fetch live train status from the API.
    
    Args:
        train_number: The train number (e.g., "12618")
    
    Returns:
        TrainStatusResponse if successful, None otherwise
    """
    assert TRAIN_STATUS_API_BASE is not None, "TRAIN_STATUS_API_BASE environment variable is not set"
    
    url = f"{TRAIN_STATUS_API_BASE}/trains/live-status"
    params = {
        "trainNo": train_number
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return TrainStatusResponse(**response.json())
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching train status: {e}")
            return None
        except httpx.RequestError as e:
            print(f"Request error fetching train status: {e}")
            return None
        except Exception as e:
            print(f"Error parsing train status response: {e}")
            return None

async def get_station_codes_from_name(station_name: str, limit: int = 8) -> list[StationSearchResult]:
    """
    Search for station codes by station name.
    
    Args:
        station_name: The station name to search for (e.g., "rani kamla")
        limit: Maximum number of results to return (default: 8)
    
    Returns:
        List of StationSearchResult with code and name
    """
    assert TRAIN_STATUS_API_BASE is not None, "TRAIN_STATUS_API_BASE environment variable is not set"
    
    url = f"{TRAIN_STATUS_API_BASE}/search"
    params = {
        "type": "station",
        "q": station_name,
        "limit": limit
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            result = StationSearchResponse(**response.json())
            return result.data
        except httpx.HTTPStatusError as e:
            print(f"HTTP error searching stations: {e}")
            return []
        except httpx.RequestError as e:
            print(f"Request error searching stations: {e}")
            return []
        except Exception as e:
            print(f"Error parsing station search response: {e}")
            return []


async def get_train_numbers_from_name(train_name: str, limit: int = 8) -> list[TrainSearchResult]:
    """
    Search for train numbers by train name.
    
    Args:
        train_name: The train name to search for (e.g., "Punjab")
        limit: Maximum number of results to return (default: 8)
    
    Returns:
        List of TrainSearchResult with number, name, fromStnCode, and toStnCode
    """
    assert TRAIN_STATUS_API_BASE is not None, "TRAIN_STATUS_API_BASE environment variable is not set"
    
    url = f"{TRAIN_STATUS_API_BASE}/search"
    params = {
        "type": "train",
        "q": train_name,
        "limit": limit
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            result = TrainSearchResponse(**response.json())
            return result.data
        except httpx.HTTPStatusError as e:
            print(f"HTTP error searching trains: {e}")
            return []
        except httpx.RequestError as e:
            print(f"Request error searching trains: {e}")
            return []
        except Exception as e:
            print(f"Error parsing train search response: {e}")
            return []


# Indian Standard Time offset (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


def get_expected_arrival_at_station(train_status: TrainStatusResponse, station_code: str) -> str:
    """
    Get the expected arrival date and time of a train at a particular station.
    
    Args:
        train_status: The TrainStatusResponse object from fetch_train_status
        station_code: The station code to check (e.g., "HWH")
    
    Returns:
        A formatted string with arrival information in IST
    """
    station_code_upper = station_code.upper()
    
    # Find the station in the route
    for station in train_status.data.route:
        if station.station_code.upper() == station_code_upper:
            # Get scheduled arrival time
            scheduled_time_str = None
            if station.scheduled_arrival_time:
                scheduled_dt = datetime.fromtimestamp(station.scheduled_arrival_time, tz=IST)
                scheduled_time_str = scheduled_dt.strftime("%d %b %Y, %I:%M %p IST")
            
            # Determine arrival time - prefer actual if available, otherwise scheduled
            if station.actual_arrival_time:
                arrival_timestamp = station.actual_arrival_time
                arrival_type = "Actual"
            elif station.scheduled_arrival_time:
                arrival_timestamp = station.scheduled_arrival_time
                arrival_type = "Scheduled"
            else:
                return f"No arrival time available for {station.station_name} ({station_code_upper})"
            
            # Convert to IST datetime
            arrival_dt = datetime.fromtimestamp(arrival_timestamp, tz=IST)
            formatted_time = arrival_dt.strftime("%d %b %Y, %I:%M %p IST")
            
            # Build response string
            result = f"Arrival at {station.station_name} ({station_code_upper}):\n"
            
            # Add scheduled time
            if scheduled_time_str:
                result += f"  Scheduled: {scheduled_time_str}\n"
            
            # Add actual/expected time
            result += f"  {arrival_type}: {formatted_time}"
            
            # Add delay info if available
            if station.scheduled_arrival_delay_secs is not None and station.scheduled_arrival_delay_secs > 0:
                delay_mins = station.scheduled_arrival_delay_secs // 60
                if delay_mins >= 60:
                    delay_hrs = delay_mins // 60
                    remaining_mins = delay_mins % 60
                    result += f" (Delayed by {delay_hrs}h {remaining_mins}m)"
                else:
                    result += f" (Delayed by {delay_mins} mins)"
            elif station.scheduled_arrival_delay_secs is not None and station.scheduled_arrival_delay_secs < 0:
                early_mins = abs(station.scheduled_arrival_delay_secs) // 60
                result += f" (Early by {early_mins} mins)"
            
            # Add platform info if available
            if station.platform_number:
                result += f"\n  Platform: {station.platform_number}"
            
            return result
    
    return f"Station {station_code_upper} not found in the train's route"


def get_current_train_position(train_status: TrainStatusResponse) -> str:
    """
    Get the current position of a train.
    
    Args:
        train_status: The TrainStatusResponse object from fetch_train_status
    
    Returns:
        A formatted string with the train's current position details
    """
    position = train_status.data.current_position
    
    # Find station name and delay info from route
    station_name = None
    delay_secs = None
    for station in train_status.data.route:
        if station.station_code.upper() == position.station_code.upper():
            station_name = station.station_name
            delay_secs = station.scheduled_arrival_delay_secs
            break
    
    # Build the result string
    result = "Current Train Position:\n"
    
    # Station info
    if station_name:
        result += f"  Station: {station_name} ({position.station_code})\n"
    else:
        result += f"  Station Code: {position.station_code}\n"
    
    # Coordinates
    result += f"  Coordinates: {position.lat_lng.latitude}°N, {position.lat_lng.longitude}°E\n"
    
    # Distance info
    result += f"  Distance from Origin: {position.distance_from_origin_km:.1f} km\n"
    if position.distance_from_last_station_km > 0:
        result += f"  Distance from Last Station: {position.distance_from_last_station_km:.1f} km\n"
    
    # Status interpretation
    status_map = {
        0: "Not Started",
        1: "In Transit",
        2: "At Station",
        3: "Arrived at Destination"
    }
    status_text = status_map.get(position.status, f"Unknown ({position.status})")
    result += f"  Status: {status_text}\n"
    
    # Overall arrival status
    result += f"  Arrival Status: {train_status.data.arrival_status}\n"
    
    # Current delay/early info
    if delay_secs is not None and delay_secs > 0:
        delay_mins = delay_secs // 60
        if delay_mins >= 60:
            delay_hrs = delay_mins // 60
            remaining_mins = delay_mins % 60
            result += f"  Current Delay: {delay_hrs}h {remaining_mins}m\n"
        else:
            result += f"  Current Delay: {delay_mins} mins\n"
    elif delay_secs is not None and delay_secs < 0:
        early_mins = abs(delay_secs) // 60
        result += f"  Running Early: {early_mins} mins\n"
    elif delay_secs == 0:
        result += f"  Running: On Time\n"
    
    # Last updated time
    last_updated_dt = datetime.fromtimestamp(train_status.data.last_updated_timestamp, tz=IST)
    result += f"  Last Updated: {last_updated_dt.strftime('%d %b %Y, %I:%M %p IST')}"
    
    return result


def get_train_route(train_status: TrainStatusResponse) -> str:
    """
    Get the complete route of a train with all stations in sequence.
    
    Args:
        train_status: The TrainStatusResponse object from fetch_train_status
    
    Returns:
        A formatted string showing all stations with names and codes in sequence
    """
    if not train_status.data.route:
        return "No route information available"
    
    # Sort stations by stop_index to ensure correct order
    sorted_route = sorted(train_status.data.route, key=lambda s: s.stop_index)
    
    # Format each station as "Station Name (CODE)"
    station_entries = [
        f"{station.station_name} ({station.station_code})"
        for station in sorted_route
    ]
    
    # Join with arrows to show direction
    route_string = " -> ".join(station_entries)
    
    return route_string
