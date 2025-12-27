import os
from dotenv import load_dotenv
import httpx
from schemas import Passenger, PNRData, RailwaysAPIResponse
from typing import List
from status_decoders import decode_booking_status

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
        status = decode_booking_status(p.bookingStatus)
        response += f"Passenger-{p.passengerSerialNumber}: {status}\n"
    return response if response != "" else "Confirm status not available."

def getCoachAndBerth(passengers:List[Passenger])->str:
    response = ""
    for p in passengers:
        coach_and_birth = "Not Confirmed"

        if p.bookingStatus == 'CNF':
            coach_and_birth= f"Coach: {p.currentCoachId}, Berth: {p.currentBerthNo}" 
        
        response += f"Passenger-{p.passengerSerialNumber}: {coach_and_birth}\n"

    return response


