from pydantic import BaseModel, Field
from typing import Optional


class NonStopStation(BaseModel):
    """A non-stop station in the route."""
    si_no: int
    station_code: str
    station_name: str
    is_diverted_station: bool = False
    distance_from_source: int
    sta: str = ""
    std: str = ""


class UpcomingStation(BaseModel):
    """An upcoming station in the train's route."""
    si_no: int
    station_code: str
    station_name: str
    is_diverted_station: Optional[bool] = False
    distance_from_source: int
    distance_from_current_station: int = 0
    distance_from_current_station_txt: str = ""
    sta: str = ""
    std: str = ""
    eta: str = ""
    etd: str = ""
    halt: int = 0
    a_day: int = 0
    arrival_delay: int = 0
    platform_number: int = 0
    on_time_rating: int = 0
    station_lat: float = 0.0
    station_lng: float = 0.0
    stoppage_number: Optional[int] = None
    day: Optional[int] = None
    eta_a_min: Optional[int] = None
    food_available: Optional[bool] = None
    non_stops: list[NonStopStation] = Field(default_factory=list)

    def get_delay_hours_minutes(self) -> tuple[int, int]:
        """Get delay as (hours, minutes) tuple."""
        hours = self.arrival_delay // 60
        minutes = self.arrival_delay % 60
        return hours, minutes


class PreviousStation(BaseModel):
    """A previously passed station in the train's route."""
    si_no: int
    station_code: str
    station_name: str
    is_diverted_station: bool = False
    distance_from_source: int
    sta: str = ""
    std: str = ""
    eta: str = ""
    etd: str = ""
    halt: int = 0
    a_day: int = 0
    arrival_delay: int = 0
    platform_number: int = 0
    station_lat: float = 0.0
    station_lng: float = 0.0
    stoppage_number: Optional[int] = None
    non_stops: list[NonStopStation] = Field(default_factory=list)


class BubbleMessage(BaseModel):
    """Bubble message with current train status info."""
    station_name: str
    message_type: str
    station_time: str


class NextStoppageInfo(BaseModel):
    """Information about the next stoppage."""
    next_stoppage_title: str
    next_stoppage: str
    next_stoppage_time_diff: str
    next_stoppage_delay: int


class CurrentLocationInfo(BaseModel):
    """Current location information item."""
    type: int
    deeplink: str = ""
    img_url: str = ""
    label: str
    message: str
    readable_message: str
    hint: str


class TtbCard(BaseModel):
    """Train ticket booking card information."""
    book_now_title: str
    rating: str
    reviews: str
    downloads: str
    text_1: str
    text_1_icon: str
    text_2: str
    text_2_icon: str
    text_3: str
    text_3_icon: str
    text_4: str
    text_4_icon: str


class DfpCarousel(BaseModel):
    """DFP Carousel (appears to be empty in examples)."""
    pass


class NewTrainStatusResponse(BaseModel):
    """Root response from the new train status API.
    
    Note: This is a flat structure where all train data fields are at the root level
    along with the success flag. We use a property to provide backward compatibility
    with code that expects a 'data' attribute.
    """
    success: bool = Field(alias="success")
    user_id: int = 0
    train_number: str
    train_name: str
    gps_unable: bool = False
    train_start_date: str
    notification_date: str = ""
    at_src_dstn: bool = False
    at_src: bool = False
    at_dstn: bool = False
    is_run_day: bool = True
    refresh_interval: int = 60
    source: str
    destination: str
    source_stn_name: str
    dest_stn_name: str
    run_days: str = ""
    journey_time: int = 0
    std: str = ""
    fog_incidence_probability: int = 0
    pantry_available: bool = False
    cur_refresh_interval: int = 30
    data_from: str = ""
    halt: int = 0
    new_alert_id: int = 0
    new_alert_msg: str = ""
    diverted_stations: Optional[list] = None
    primary_alert: int = 0
    instance_alert: int = 0
    related_alert: int = 0
    late_update: bool = False
    is_ry_eta: bool = False
    update_time: str = ""
    is_on_train: bool = False
    on_train_error_msg: str = ""
    travelling_towards: str = ""
    distance_from_source: int
    total_distance: int
    avg_speed: int = 0
    a_min: int = 0
    si_no: int
    current_station_code: str
    current_station_name: str
    status: str  # "T" for travelling/transit
    eta: str = ""  # estimated / actual arrival time
    etd: str = ""  # estimated / actual departure time
    delay: int  # Delay in minutes
    ahead_distance: int = 0
    ahead_distance_text: str = ""
    status_as_of: str
    local_address: str = ""
    platform_number: int = 0
    cur_stn_sta: str = ""  # Current station scheduled arrival
    cur_stn_std: str = ""  # Current station scheduled departure
    is_possibly_on_train: bool = False
    stoppage_number: int = 0
    a_day: int = 0
    status_as_of_min: int = 0
    dfp_carousel: Optional[DfpCarousel] = None
    upcoming_stations: list[UpcomingStation] = Field(default_factory=list)
    previous_stations: list[PreviousStation] = Field(default_factory=list)
    personalized_food_deeplink: str = ""
    travelling_from_lat_lng: list[str] = Field(default_factory=list)
    travelling_to_lat_lng: list[str] = Field(default_factory=list)
    bubble_message: Optional[BubbleMessage] = None
    next_stoppage_info: Optional[NextStoppageInfo] = None
    current_location_info: list[CurrentLocationInfo] = Field(default_factory=list)
    ttb_card: Optional[TtbCard] = None
    spent_time: float = 0.0
    disclaimer: str = ""

    @property
    def data(self) -> "NewTrainStatusResponse":
        """Backward compatibility: return self as 'data' for existing code."""
        return self

    def get_delay_hours_minutes(self) -> tuple[int, int]:
        """Get current delay as (hours, minutes) tuple."""
        hours = self.delay // 60
        minutes = self.delay % 60
        return hours, minutes

    def get_progress_percentage(self) -> float:
        """Get journey progress as percentage."""
        if self.total_distance == 0:
            return 0.0
        return (self.distance_from_source / self.total_distance) * 100

    def get_remaining_distance(self) -> int:
        """Get remaining distance to destination in km."""
        return self.total_distance - self.distance_from_source
