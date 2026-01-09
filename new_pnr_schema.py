from pydantic import BaseModel
from typing import Optional


class PassengerStatus(BaseModel):
    ReferenceId: Optional[str] = None
    Pnr: Optional[str] = None
    Number: int
    Prediction: str
    PredictionPercentage: Optional[float] = None
    ConfirmTktStatus: str
    Coach: str
    Berth: int
    BookingStatus: str
    CurrentStatus: str
    CoachPosition: Optional[str] = None
    BookingBerthNo: str
    BookingCoachId: str
    BookingStatusNew: str
    BookingStatusIndex: str
    CurrentBerthNo: str
    CurrentCoachId: str
    BookingBerthCode: Optional[str] = None
    CurrentBerthCode: Optional[str] = None
    CurrentStatusNew: str
    CurrentStatusIndex: str


class StationDetails(BaseModel):
    category: str
    division: str
    latitude: str
    longitude: str
    state: str
    stationCode: str
    stationName: str


class PNRData(BaseModel):
    Pnr: str
    TrainNo: str
    TrainName: str
    Doj: str
    BookingDate: str
    Quota: str
    DestinationDoj: str
    SourceDoj: str
    From: str
    To: str
    ReservationUpto: str
    BoardingPoint: str
    Class: str
    ChartPrepared: bool
    BoardingStationName: str
    TrainStatus: str
    TrainCancelledFlag: bool
    ReservationUptoName: str
    PassengerCount: int
    PassengerStatus: list[PassengerStatus]
    DepartureTime: str
    ArrivalTime: str
    ExpectedPlatformNo: str
    BookingFare: str
    TicketFare: str
    CoachPosition: str
    Rating: float
    FoodRating: float
    PunctualityRating: float
    CleanlinessRating: float
    SourceName: str
    DestinationName: str
    Duration: str
    RatingCount: int
    HasPantry: bool
    GroupingId: Optional[str] = None
    OptVikalp: bool
    VikalpData: str
    VikalpTransferred: bool
    VikalpTransferredMessage: str
    FromDetails: Optional[StationDetails] = None
    BoardingPointDetails: Optional[StationDetails] = None


class PNRResponse(BaseModel):
    status: bool
    message: str
    timestamp: int
    data: Optional[PNRData] = None
