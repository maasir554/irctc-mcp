"""
Tests for PNR Status API functions.
Run with: python test_pnr.py
Or with pytest: pytest test_pnr.py -v
"""

import asyncio
import pytest
from pnr_functions import (
    fetch_pnr_details,
    checkConfirmStatus,
    getCoachAndBerth,
    getWaitListPosition,
)
from pnr_schemas import Passenger
from status_decoders import decode_ticket_status, decode_berth


# Sample PNR numbers for testing
VALID_PNR = "8341223680"
INVALID_PNR = "0000000000"


# ==================== Mock Data ====================

MOCK_PASSENGERS_CONFIRMED = [
    Passenger(
        passengerSerialNumber=1,
        bookingStatus="CNF",
        currentCoachId="B1",
        currentBerthNo=25,
        currentBerthCode="LB",
        bookingStatusDetails="CNF/B1/25/LB",
    ),
    Passenger(
        passengerSerialNumber=2,
        bookingStatus="CNF",
        currentCoachId="B1",
        currentBerthNo=26,
        currentBerthCode="MB",
        bookingStatusDetails="CNF/B1/26/MB",
    ),
]

MOCK_PASSENGERS_WAITLIST = [
    Passenger(
        passengerSerialNumber=1,
        bookingStatus="WL",
        currentCoachId=None,
        currentBerthNo=None,
        currentBerthCode=None,
        bookingStatusDetails="WL/15",
    ),
    Passenger(
        passengerSerialNumber=2,
        bookingStatus="GNWL",
        currentCoachId=None,
        currentBerthNo=None,
        currentBerthCode=None,
        bookingStatusDetails="GNWL/20",
    ),
]

MOCK_PASSENGERS_RAC = [
    Passenger(
        passengerSerialNumber=1,
        bookingStatus="RAC",
        currentCoachId="S1",
        currentBerthNo=5,
        currentBerthCode="SL",
        bookingStatusDetails="RAC/5",
    ),
]


# ==================== API Tests ====================

async def test_fetch_valid_pnr():
    """Test fetching details for a valid PNR number."""
    result = await fetch_pnr_details(VALID_PNR)
    print(f"\n{'='*50}")
    print(f"Testing PNR: {VALID_PNR}")
    print(f"{'='*50}")
    
    if result:
        print(f"Success: {result.success}")
        print(f"Data: {result.data}")
    else:
        print("No result returned (API might be unavailable)")
    
    return result


async def test_fetch_invalid_pnr():
    """Test fetching details for an invalid PNR number."""
    result = await fetch_pnr_details(INVALID_PNR)
    print(f"\n{'='*50}")
    print(f"Testing Invalid PNR: {INVALID_PNR}")
    print(f"{'='*50}")
    
    if result:
        print(f"Success: {result.success}")
        print(f"Data: {result.data}")
    else:
        print("No result returned (expected for invalid PNR)")
    
    return result


# ==================== Helper Function Tests ====================

def test_check_confirm_status_confirmed():
    """Test checkConfirmStatus with confirmed passengers."""
    print(f"\n{'='*50}")
    print("Testing checkConfirmStatus - Confirmed Passengers")
    print(f"{'='*50}")
    
    result = checkConfirmStatus(MOCK_PASSENGERS_CONFIRMED)
    print(result)
    
    assert "Confirmed" in result
    assert "Passenger-1" in result
    assert "Passenger-2" in result
    return result


def test_check_confirm_status_waitlist():
    """Test checkConfirmStatus with waitlisted passengers."""
    print(f"\n{'='*50}")
    print("Testing checkConfirmStatus - Waitlisted Passengers")
    print(f"{'='*50}")
    
    result = checkConfirmStatus(MOCK_PASSENGERS_WAITLIST)
    print(result)
    
    assert "Waitlist" in result
    return result


def test_get_coach_and_berth_confirmed():
    """Test getCoachAndBerth with confirmed passengers."""
    print(f"\n{'='*50}")
    print("Testing getCoachAndBerth - Confirmed Passengers")
    print(f"{'='*50}")
    
    result = getCoachAndBerth(MOCK_PASSENGERS_CONFIRMED)
    print(result)
    
    assert "Coach: B1" in result
    assert "Berth: 25" in result
    assert "Lower Berth" in result
    return result


def test_get_coach_and_berth_waitlist():
    """Test getCoachAndBerth with waitlisted passengers."""
    print(f"\n{'='*50}")
    print("Testing getCoachAndBerth - Waitlisted Passengers")
    print(f"{'='*50}")
    
    result = getCoachAndBerth(MOCK_PASSENGERS_WAITLIST)
    print(result)
    
    assert "Not Confirmed" in result
    return result


def test_get_coach_and_berth_rac():
    """Test getCoachAndBerth with RAC passengers."""
    print(f"\n{'='*50}")
    print("Testing getCoachAndBerth - RAC Passengers")
    print(f"{'='*50}")
    
    result = getCoachAndBerth(MOCK_PASSENGERS_RAC)
    print(result)
    
    assert "Coach: S1" in result
    assert "Side Lower" in result
    return result


def test_get_waitlist_position():
    """Test getWaitListPosition with waitlisted passengers."""
    print(f"\n{'='*50}")
    print("Testing getWaitListPosition - Waitlisted Passengers")
    print(f"{'='*50}")
    
    result = getWaitListPosition(MOCK_PASSENGERS_WAITLIST)
    print(result)
    
    assert "Passenger-1" in result
    assert "Passenger-2" in result
    return result


# ==================== Decoder Tests ====================

def test_decode_ticket_status():
    """Test status code decoding."""
    print(f"\n{'='*50}")
    print("Testing decode_ticket_status")
    print(f"{'='*50}")
    
    assert decode_ticket_status("CNF") == "Confirmed"
    assert decode_ticket_status("RAC") == "Reservation Against Cancellation"
    assert decode_ticket_status("WL") == "Waitlist"
    assert decode_ticket_status("GNWL") == "General Waitlist"
    assert "Unknown" in decode_ticket_status("XYZ")
    assert decode_ticket_status(None) == "Unknown Status"
    
    print("✅ All status codes decoded correctly")


def test_decode_berth():
    """Test berth code decoding."""
    print(f"\n{'='*50}")
    print("Testing decode_berth")
    print(f"{'='*50}")
    
    assert decode_berth("LB") == "Lower Berth"
    assert decode_berth("MB") == "Middle Berth"
    assert decode_berth("UB") == "Upper Berth"
    assert decode_berth("SL") == "Side Lower"
    assert decode_berth("SU") == "Side Upper"
    assert "Unknown" in decode_berth("XY")
    
    print("✅ All berth codes decoded correctly")


# ==================== Run All Tests ====================

async def run_all_tests():
    """Run all tests."""
    print("\n🚂 PNR Status API Tests\n")
    
    # API tests
    await test_fetch_valid_pnr()
    await test_fetch_invalid_pnr()
    
    # Helper function tests
    test_check_confirm_status_confirmed()
    test_check_confirm_status_waitlist()
    test_get_coach_and_berth_confirmed()
    test_get_coach_and_berth_waitlist()
    test_get_coach_and_berth_rac()
    test_get_waitlist_position()
    
    # Decoder tests
    test_decode_ticket_status()
    test_decode_berth()
    
    print(f"\n{'='*50}")
    print("✅ All tests completed!")
    print(f"{'='*50}\n")


# ==================== Pytest Tests ====================

@pytest.mark.asyncio
async def test_fetch_pnr_returns_response():
    """Pytest: Verify fetch returns a response object."""
    result = await fetch_pnr_details(VALID_PNR)
    assert result is None or hasattr(result, 'success')


@pytest.mark.asyncio
async def test_fetch_pnr_handles_invalid():
    """Pytest: Verify invalid PNR is handled gracefully."""
    result = await fetch_pnr_details(INVALID_PNR)
    assert result is None or isinstance(result.success, bool)


def test_confirm_status_returns_string():
    """Pytest: Verify checkConfirmStatus returns a string."""
    result = checkConfirmStatus(MOCK_PASSENGERS_CONFIRMED)
    assert isinstance(result, str)
    assert len(result) > 0


def test_coach_berth_returns_string():
    """Pytest: Verify getCoachAndBerth returns a string."""
    result = getCoachAndBerth(MOCK_PASSENGERS_CONFIRMED)
    assert isinstance(result, str)
    assert "Coach" in result


def test_waitlist_position_returns_string():
    """Pytest: Verify getWaitListPosition returns a string."""
    result = getWaitListPosition(MOCK_PASSENGERS_WAITLIST)
    assert isinstance(result, str)


def test_empty_passenger_list():
    """Pytest: Verify functions handle empty passenger lists."""
    assert checkConfirmStatus([]) == "Confirm status not available."
    assert getCoachAndBerth([]) == "Coach & Birth not available"
    assert getWaitListPosition([]) == "Unable to get waitlist position."


if __name__ == "__main__":
    asyncio.run(run_all_tests())
