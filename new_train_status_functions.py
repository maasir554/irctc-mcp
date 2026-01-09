import os
from datetime import datetime, timezone, timedelta, date
from dotenv import load_dotenv
import httpx
from new_train_status_schemas import (
    NewTrainStatusResponse,
    TrainStatusData,
    UpcomingStation,
    PreviousStation,
)
from train_status_schemas import (
    StationSearchResponse,
    StationSearchResult,
    TrainSearchResponse,
    TrainSearchResult,
)

load_dotenv()

NEW_TRAIN_STATUS_API_BASE = os.getenv("NEW_TRAIN_STATUS_API_BASE")


# Indian Standard Time offset (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

async def fetch_new_train_status(train_number: str, start_day: int = 0) -> NewTrainStatusResponse | None:
    """
    Fetch live train status from the RailYatri API.
    
    Args:
        train_number: The train number (e.g., "12138")
        start_day: Days ago the train started (0 = today, 1 = yesterday, 2 = day before yesterday, etc.)
    
    Returns:
        NewTrainStatusResponse if successful, None otherwise
    """
    assert NEW_TRAIN_STATUS_API_BASE is not None
    url = f"{NEW_TRAIN_STATUS_API_BASE}/{train_number}/json"
    params = {
        "start_day": start_day
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return NewTrainStatusResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching train status: {e}")
            return None
        except httpx.RequestError as e:
            print(f"Request error fetching train status: {e}")
            return None
        except Exception as e:
            print(f"Error parsing train status response: {e}")
            return None

def format_delay(delay_minutes: int) -> str:
    """Format delay in minutes to a human-readable string."""
    if delay_minutes == 0:
        return "On Time"
    elif delay_minutes > 0:
        hours = delay_minutes // 60
        mins = delay_minutes % 60
        if hours > 0:
            return f"Delayed by {hours}h {mins}m"
        return f"Delayed by {mins} mins"
    else:
        early_mins = abs(delay_minutes)
        return f"Early by {early_mins} mins"


def get_expected_arrival_at_station(train_status: NewTrainStatusResponse, station_code: str) -> str:
    """
    Get the expected arrival date and time of a train at a particular station.
    
    Args:
        train_status: The NewTrainStatusResponse object from fetch_new_train_status
        station_code: The station code to check (e.g., "KCG")
    
    Returns:
        A formatted string with arrival information
    """
    station_code_upper = station_code.upper()
    data = train_status.data
    
    # Check if it's the current station
    if data.current_station_code.upper() == station_code_upper:
        result = f"Train is currently at/near {data.current_station_name} ({station_code_upper})\n"
        result += f"  Status: {data.status_as_of}\n"
        if data.eta:
            result += f"  ETA: {data.eta}\n"
        if data.delay > 0:
            result += f"  {format_delay(data.delay)}"
        return result
    
    # Search in upcoming stations
    for station in data.upcoming_stations:
        if station.station_code.upper() == station_code_upper:
            result = f"Arrival at {station.station_name} ({station_code_upper}):\n"
            if station.sta:
                result += f"  Scheduled Arrival: {station.sta}\n"
            if station.eta:
                result += f"  Expected Arrival: {station.eta}\n"
            if station.arrival_delay != 0:
                result += f"  {format_delay(station.arrival_delay)}\n"
            if station.platform_number:
                result += f"  Platform: {station.platform_number}\n"
            if station.distance_from_current_station_txt:
                result += f"  Distance: {station.distance_from_current_station_txt}"
            return result
    
    # Search in previous stations
    for station in data.previous_stations:
        if station.station_code.upper() == station_code_upper:
            result = f"Train has already passed {station.station_name} ({station_code_upper}):\n"
            if station.sta:
                result += f"  Scheduled Arrival: {station.sta}\n"
            if station.eta:
                result += f"  Actual Arrival: {station.eta}\n"
            if station.arrival_delay != 0:
                result += f"  {format_delay(station.arrival_delay)}\n"
            if station.platform_number:
                result += f"  Platform: {station.platform_number}"
            return result
    
    # Check in non-stop stations
    all_stations = data.upcoming_stations + data.previous_stations
    for station in all_stations:
        for non_stop in station.non_stops:
            if non_stop.station_code.upper() == station_code_upper:
                return f"{non_stop.station_name} ({station_code_upper}) is a non-stop station. Train does not halt here."
    
    return f"Station {station_code_upper} not found in the train's route"


def get_current_train_position(train_status: NewTrainStatusResponse) -> str:
    """
    Get the current position of a train.
    
    Args:
        train_status: The NewTrainStatusResponse object from fetch_new_train_status
    
    Returns:
        A formatted string with the train's current position details
    """
    data = train_status.data
    
    result = f"Current Train Position - {data.train_name} ({data.train_number}):\n"
    result += f"  Route: {data.source_stn_name} ({data.source}) → {data.dest_stn_name} ({data.destination})\n"
    result += "\n"
    
    # Current location
    result += f"  Current Station: {data.current_station_name} ({data.current_station_code})\n"
    
    # Status interpretation
    status_map = {
        "T": "In Transit",
        "A": "Arrived",
        "D": "Departed",
        "S": "At Station",
    }
    status_text = status_map.get(data.status, data.status)
    result += f"  Status: {status_text}\n"
    
    # Distance and progress
    result += f"  Distance Covered: {data.distance_from_source} km / {data.total_distance} km\n"
    result += f"  Progress: {data.get_progress_percentage():.1f}%\n"
    
    if data.ahead_distance_text:
        result += f"  Position: {data.ahead_distance_text}\n"
    
    # Delay info
    if data.delay > 0:
        hours, mins = data.get_delay_hours_minutes()
        if hours > 0:
            result += f"  Delay: {hours}h {mins}m\n"
        else:
            result += f"  Delay: {mins} mins\n"
    elif data.delay == 0:
        result += f"  Running: On Time\n"
    
    # Next stoppage info
    if data.next_stoppage_info:
        result += f"\n  Next Stop: {data.next_stoppage_info.next_stoppage} ({data.next_stoppage_info.next_stoppage_time_diff})\n"
        if data.next_stoppage_info.next_stoppage_delay > 0:
            result += f"  Next Stop Delay: {format_delay(data.next_stoppage_info.next_stoppage_delay)}\n"
    
    # Last update time
    result += f"\n  {data.status_as_of}"
    if data.update_time:
        result += f"\n  Last Updated: {data.update_time}"
    
    return result


def get_train_route(train_status: NewTrainStatusResponse, include_non_stops: bool = False) -> str:
    """
    Get the complete route of a train with all stations in sequence.
    
    Args:
        train_status: The NewTrainStatusResponse object from fetch_new_train_status
        include_non_stops: Whether to include non-stop stations (default: False)
    
    Returns:
        A formatted string showing all stations with names and codes in sequence
    """
    data = train_status.data
    
    if not data.previous_stations and not data.upcoming_stations:
        return "No route information available"
    
    # Collect all stoppage stations
    all_stations: list[tuple[int, str, str, bool]] = []  # (si_no, name, code, is_current)
    
    # Add previous stations
    for station in data.previous_stations:
        all_stations.append((station.si_no, station.station_name, station.station_code, False))
        if include_non_stops:
            for ns in station.non_stops:
                all_stations.append((ns.si_no, f"[{ns.station_name}]", ns.station_code, False))
    
    # Add current station marker
    all_stations.append((data.si_no, data.current_station_name, data.current_station_code, True))
    
    # Add upcoming stations
    for station in data.upcoming_stations:
        if station.station_code:  # Skip empty placeholder stations
            all_stations.append((station.si_no, station.station_name, station.station_code, False))
            if include_non_stops:
                for ns in station.non_stops:
                    all_stations.append((ns.si_no, f"[{ns.station_name}]", ns.station_code, False))
    
    # Sort by si_no
    all_stations.sort(key=lambda x: x[0])
    
    # Format each station
    station_entries = []
    for si_no, name, code, is_current in all_stations:
        if is_current:
            station_entries.append(f">>> {name} ({code}) <<<")
        else:
            station_entries.append(f"{name} ({code})")
    
    # Join with arrows
    route_string = " -> ".join(station_entries)
    
    return route_string


def get_upcoming_stations(train_status: NewTrainStatusResponse, limit: int = 5) -> str:
    """
    Get the next upcoming stations for the train.
    
    Args:
        train_status: The NewTrainStatusResponse object from fetch_new_train_status
        limit: Maximum number of stations to show (default: 5)
    
    Returns:
        A formatted string with upcoming station details
    """
    data = train_status.data
    
    if not data.upcoming_stations:
        return "No upcoming stations available"
    
    result = f"Upcoming Stations for {data.train_name} ({data.train_number}):\n\n"
    
    count = 0
    for station in data.upcoming_stations:
        if not station.station_code:  # Skip empty placeholder
            continue
        if count >= limit:
            break
        
        result += f"  {count + 1}. {station.station_name} ({station.station_code})\n"
        if station.sta and station.eta:
            result += f"     Scheduled: {station.sta} | Expected: {station.eta}\n"
        elif station.sta:
            result += f"     Scheduled: {station.sta}\n"
        
        if station.arrival_delay != 0:
            result += f"     {format_delay(station.arrival_delay)}\n"
        
        if station.platform_number:
            result += f"     Platform: {station.platform_number}\n"
        
        if station.distance_from_current_station_txt:
            result += f"     {station.distance_from_current_station_txt}\n"
        
        if station.halt > 0:
            result += f"     Halt: {station.halt} min\n"
        
        result += "\n"
        count += 1
    
    remaining = len([s for s in data.upcoming_stations if s.station_code]) - count
    if remaining > 0:
        result += f"  ... and {remaining} more stations"
    
    return result


def get_train_summary(train_status: NewTrainStatusResponse) -> str:
    """
    Get a brief summary of the train's current status.
    
    Args:
        train_status: The NewTrainStatusResponse object from fetch_new_train_status
    
    Returns:
        A brief formatted summary string
    """
    data = train_status.data
    
    result = f"{data.train_name} ({data.train_number})\n"
    result += f"{data.source_stn_name} → {data.dest_stn_name}\n\n"
    
    # Current position
    if data.bubble_message:
        result += f"{data.bubble_message.message_type} {data.bubble_message.station_name}\n"
    else:
        result += f"Near {data.current_station_name}\n"
    
    # Delay
    if data.delay > 0:
        hours, mins = data.get_delay_hours_minutes()
        if hours > 0:
            result += f"Running late by {hours}h {mins}m\n"
        else:
            result += f"Running late by {mins} mins\n"
    else:
        result += f"Running on time\n"
    
    # Next stop
    if data.next_stoppage_info:
        result += f"Next: {data.next_stoppage_info.next_stoppage} {data.next_stoppage_info.next_stoppage_time_diff}\n"
    
    result += f"\n{data.status_as_of}"
    
    return result


def get_train_start_date(train_status: NewTrainStatusResponse) -> date | None:
    """
    Get the train start date as a date object.
    
    Args:
        train_status: The NewTrainStatusResponse object from fetch_new_train_status
        
    Returns:
        A date object representing when the train started, or None if parsing fails
    """
    try:
        return datetime.strptime(train_status.data.train_start_date, "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None
