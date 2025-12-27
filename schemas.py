from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class BookingStatus(str, Enum):
    CONFIRMED = "CNF"
    RAC = "RAC"
    WAITLIST = "WL"
    CANCELLED = "CAN"
    NO_SEAT_BERTH = "NOSB"
    GENERAL_WL = "GNWL"
    REMOTE_WL = "RLWL"
    POOLED_WL = "PQWL"
    TATKAL_WL = "TQWL"

# 1. Passenger Model
class Passenger(BaseModel):
    passengerSerialNumber: Optional[int] = None
    concessionOpted: Optional[bool] = None
    forGoConcessionOpted: Optional[bool] = None
    passengerIcardFlag: Optional[bool] = None
    childBerthFlag: Optional[bool] = None
    passengerNationality: Optional[str] = None
    passengerQuota: Optional[str] = None
    passengerCoachPosition: Optional[int] = None
    waitListType: Optional[int] = None
    bookingStatusIndex: Optional[int] = None
    bookingStatus: Optional[BookingStatus|str] = None
    bookingCoachId: Optional[str] = None
    bookingBerthNo: Optional[int] = None
    bookingBerthCode: Optional[str] = None
    bookingStatusDetails: Optional[str] = None
    currentStatusIndex: Optional[int] = None
    currentStatus: Optional[str] = None
    currentCoachId: Optional[str] = None
    currentBerthNo: Optional[int] = None
    currentBerthCode: Optional[str] = None
    currentStatusDetails: Optional[str] = None

# 2. Data Model
class PNRData(BaseModel):
    pnrNumber: str
    dateOfJourney: str
    trainNumber: str
    trainName: str
    sourceStation: str
    destinationStation: str
    reservationUpto: str
    boardingPoint: str
    journeyClass: str
    numberOfpassenger: int
    
    chartStatus: Optional[str] = "Chart Not Prepared" 
    informationMessage: Optional[List[str]] = []
    
    passengerList: Optional[List[Passenger]] = []
    
    timeStamp: Optional[str] = None
    bookingFare: int
    ticketFare: int
    quota: str
    reasonType: Optional[str] = None
    ticketTypeInPrs: Optional[str] = None
    vikalpStatus: Optional[str] = None
    waitListType: Optional[int] = None
    bookingDate: str
    arrivalDate: str
    distance: int
    isWL: str

# 3. Root Response Model
class RailwaysAPIResponse(BaseModel):
    success: bool
    # Even 'data' can be None if success is False (e.g., "Invalid PNR")
    data: Optional[PNRData] = None
    generatedTimeStamp: int