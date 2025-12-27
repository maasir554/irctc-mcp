from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StationSearchResult(BaseModel):
    """A station search result."""
    code: str
    name: str


class StationSearchResponse(BaseModel):
    """Response from station search API."""
    success: bool
    data: list[StationSearchResult]
    total: int
    query: str


class TrainSearchResult(BaseModel):
    """A train search result."""
    number: str
    name: str
    from_stn_code: str = Field(alias="fromStnCode")
    to_stn_code: str = Field(alias="toStnCode")

    class Config:
        populate_by_name = True


class TrainSearchResponse(BaseModel):
    """Response from train search API."""
    success: bool
    data: list[TrainSearchResult]
    total: int
    query: str


class LatLng(BaseModel):
    """Geographical coordinates."""
    latitude: float
    longitude: float


class CurrentPosition(BaseModel):
    """Current position of the train."""
    lat_lng: LatLng = Field(alias="latLng")
    station_code: str = Field(alias="stationCode")
    status: int
    distance_from_origin_km: float = Field(alias="distanceFromOriginKm")
    distance_from_last_station_km: float = Field(alias="distanceFromLastStationKm")

    class Config:
        populate_by_name = True


class RouteStation(BaseModel):
    """A station in the train's route."""
    platform_number: str = Field(alias="platformNumber")
    station_code: str = Field(alias="stationCode")
    station_name: str
    stop_index: int = Field(alias="stopIndex")
    platform_sources: Optional[str] = Field(default=None, alias="platformSources")
    
    # Scheduled times (Unix timestamps)
    scheduled_arrival_time: Optional[int] = Field(default=None, alias="scheduledArrivalTime")
    scheduled_departure_time: Optional[int] = Field(default=None, alias="scheduledDepartureTime")
    
    # Actual times (Unix timestamps)
    actual_arrival_time: Optional[int] = Field(default=None, alias="actualArrivalTime")
    actual_departure_time: Optional[int] = Field(default=None, alias="actualDepartureTime")
    
    # Delay information (in seconds)
    scheduled_arrival_delay_secs: Optional[int] = Field(default=None, alias="scheduledArrivalDelaySecs")
    scheduled_departure_delay_secs: Optional[int] = Field(default=None, alias="scheduledDepartureDelaySecs")

    class Config:
        populate_by_name = True

    def get_arrival_delay_minutes(self) -> Optional[int]:
        """Get arrival delay in minutes."""
        if self.scheduled_arrival_delay_secs is not None:
            return self.scheduled_arrival_delay_secs // 60
        return None

    def get_departure_delay_minutes(self) -> Optional[int]:
        """Get departure delay in minutes."""
        if self.scheduled_departure_delay_secs is not None:
            return self.scheduled_departure_delay_secs // 60
        return None

    def get_scheduled_arrival_datetime(self) -> Optional[datetime]:
        """Convert scheduled arrival timestamp to datetime."""
        if self.scheduled_arrival_time:
            return datetime.fromtimestamp(self.scheduled_arrival_time)
        return None

    def get_scheduled_departure_datetime(self) -> Optional[datetime]:
        """Convert scheduled departure timestamp to datetime."""
        if self.scheduled_departure_time:
            return datetime.fromtimestamp(self.scheduled_departure_time)
        return None

    def get_actual_arrival_datetime(self) -> Optional[datetime]:
        """Convert actual arrival timestamp to datetime."""
        if self.actual_arrival_time:
            return datetime.fromtimestamp(self.actual_arrival_time)
        return None

    def get_actual_departure_datetime(self) -> Optional[datetime]:
        """Convert actual departure timestamp to datetime."""
        if self.actual_departure_time:
            return datetime.fromtimestamp(self.actual_departure_time)
        return None


class TrainStatusData(BaseModel):
    """Train status data from the API."""
    current_position: CurrentPosition = Field(alias="currentPosition")
    arrival_status: str = Field(alias="arrivalStatus")
    last_updated_timestamp: int = Field(alias="lastUpdatedTimestamp")
    route: list[RouteStation]
    data_source: str = Field(alias="dataSource")
    unmapped_field_13: Optional[str] = Field(default=None, alias="unmappedField_13")

    class Config:
        populate_by_name = True

    def get_last_updated_datetime(self) -> datetime:
        """Convert last updated timestamp to datetime."""
        return datetime.fromtimestamp(self.last_updated_timestamp)


class TrainStatusResponse(BaseModel):
    """Root response from the train status API."""
    success: bool
    data: TrainStatusData

    class Config:
        populate_by_name = True
