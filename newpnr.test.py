from new_pnr_status import (
    fetch_pnr_status,
    get_train_start_date,
    get_train_number,
    check_confirm_status,
    get_coach_and_berth,
    get_waitlist_position,
    get_journey_overview,
    get_passenger_summary,
    get_pnr_summary,
)
from new_pnr_schema import PNRResponse
from datetime import date


# Test PNR number
TEST_PNR = "8641842491"


def test_fetch_pnr_status():
    """Test fetching PNR status from the API."""
    pnr_no = TEST_PNR
    
    result = fetch_pnr_status(pnr_no)
    
    # Verify return type
    assert isinstance(result, PNRResponse)
    
    # Verify response structure
    assert result.status is True
    assert result.message == "Success"
    assert result.data is not None
    
    # Verify PNR data
    assert result.data.Pnr == pnr_no
    assert result.data.TrainNo is not None
    assert result.data.TrainName is not None
    assert result.data.PassengerCount >= 1
    assert len(result.data.PassengerStatus) == result.data.PassengerCount
    
    print(f"PNR: {result.data.Pnr}")
    print(f"Train: {result.data.TrainNo} - {result.data.TrainName}")
    print(f"From: {result.data.From} -> To: {result.data.To}")
    print(f"Date of Journey: {result.data.Doj}")
    print(f"Passengers: {result.data.PassengerCount}")
    for passenger in result.data.PassengerStatus:
        print(f"  Passenger {passenger.Number}: {passenger.CurrentStatus}")


def test_invalid_length_pnr():
    """Test that PNR with invalid length returns None without API call."""
    # Too short
    assert fetch_pnr_status("123456789") is None
    print("✓ 9 digit PNR returns None")
    
    # Too long
    assert fetch_pnr_status("12345678901") is None
    print("✓ 11 digit PNR returns None")
    
    # Empty
    assert fetch_pnr_status("") is None
    print("✓ Empty PNR returns None")
    
    # Non-numeric
    assert fetch_pnr_status("abcdefghij") is None
    print("✓ Non-numeric PNR returns None")
    
    # Mixed
    assert fetch_pnr_status("12345abcde") is None
    print("✓ Mixed alphanumeric PNR returns None")


def test_invalid_pnr_value():
    """Test that valid format but non-existent PNR returns None."""
    result = fetch_pnr_status("0000000000")
    assert result is None
    print("✓ Invalid PNR (0000000000) returns None")


def test_get_train_start_date():
    """Test getting train start date from PNR."""
    pnr_status = fetch_pnr_status(TEST_PNR)
    
    result = get_train_start_date(pnr_status)
    
    # Should return a date object
    assert result is not None
    assert isinstance(result, date)
    
    print(f"✓ Train start date: {result}")
    print(f"  Year: {result.year}, Month: {result.month}, Day: {result.day}")


def test_get_train_start_date_none():
    """Test get_train_start_date with None input."""
    result = get_train_start_date(None)
    assert result is None
    print("✓ get_train_start_date(None) returns None")


def test_get_train_number():
    """Test getting train number from PNR."""
    pnr_status = fetch_pnr_status(TEST_PNR)
    
    result = get_train_number(pnr_status)
    
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
    
    print(f"✓ Train number: {result}")


def test_get_train_number_none():
    """Test get_train_number with None input."""
    result = get_train_number(None)
    assert result is None
    print("✓ get_train_number(None) returns None")


def test_check_confirm_status():
    """Test checking confirmation status of passengers."""
    pnr_status = fetch_pnr_status(TEST_PNR)
    
    result = check_confirm_status(pnr_status)
    
    assert result is not None
    assert isinstance(result, str)
    assert "Passenger-" in result
    
    print(f"✓ Confirm status:\n{result}")


def test_check_confirm_status_none():
    """Test check_confirm_status with None input."""
    result = check_confirm_status(None)
    assert result == "PNR data not available."
    print("✓ check_confirm_status(None) returns appropriate message")


def test_get_coach_and_berth():
    """Test getting coach and berth details."""
    pnr_status = fetch_pnr_status(TEST_PNR)
    
    result = get_coach_and_berth(pnr_status)
    
    assert result is not None
    assert isinstance(result, str)
    assert "Passenger-" in result
    
    print(f"✓ Coach and Berth:\n{result}")


def test_get_coach_and_berth_none():
    """Test get_coach_and_berth with None input."""
    result = get_coach_and_berth(None)
    assert result == "PNR data not available."
    print("✓ get_coach_and_berth(None) returns appropriate message")


def test_get_waitlist_position():
    """Test getting waitlist position."""
    pnr_status = fetch_pnr_status(TEST_PNR)
    
    result = get_waitlist_position(pnr_status)
    
    assert result is not None
    assert isinstance(result, str)
    assert "Passenger-" in result
    
    print(f"✓ Waitlist position:\n{result}")


def test_get_waitlist_position_none():
    """Test get_waitlist_position with None input."""
    result = get_waitlist_position(None)
    assert result == "PNR data not available."
    print("✓ get_waitlist_position(None) returns appropriate message")


def test_get_journey_overview():
    """Test getting journey overview."""
    pnr_status = fetch_pnr_status(TEST_PNR)
    
    result = get_journey_overview(pnr_status)
    
    assert result is not None
    assert isinstance(result, str)
    assert "Train:" in result
    assert "Date of Journey:" in result
    assert "Source Station:" in result
    assert "Destination Station:" in result
    
    print(f"✓ Journey overview:\n{result}")


def test_get_journey_overview_none():
    """Test get_journey_overview with None input."""
    result = get_journey_overview(None)
    assert result == "Failed to receive API response."
    print("✓ get_journey_overview(None) returns appropriate message")


def test_get_passenger_summary():
    """Test getting passenger summary."""
    pnr_status = fetch_pnr_status(TEST_PNR)
    
    result = get_passenger_summary(pnr_status)
    
    assert result is not None
    assert isinstance(result, str)
    assert "Passenger" in result
    assert "Booking Status:" in result
    assert "Current Status:" in result
    
    print(f"✓ Passenger summary:\n{result}")


def test_get_passenger_summary_none():
    """Test get_passenger_summary with None input."""
    result = get_passenger_summary(None)
    assert result == "PNR data not available."
    print("✓ get_passenger_summary(None) returns appropriate message")


def test_get_pnr_summary():
    """Test getting complete PNR summary."""
    pnr_status = fetch_pnr_status(TEST_PNR)
    
    result = get_pnr_summary(pnr_status)
    
    assert result is not None
    assert isinstance(result, str)
    assert "PNR:" in result
    assert "🚂" in result  # Train emoji
    assert "📅" in result  # Date emoji
    assert "Passengers" in result
    
    print(f"✓ PNR summary:\n{result}")


def test_get_pnr_summary_none():
    """Test get_pnr_summary with None input."""
    result = get_pnr_summary(None)
    assert result == "PNR data not available."
    print("✓ get_pnr_summary(None) returns appropriate message")


if __name__ == "__main__":
    print("=" * 50)
    print("Test 1: Valid PNR Fetch")
    print("=" * 50)
    test_fetch_pnr_status()
    print("\n✅ Valid PNR test passed!\n")
    
    print("=" * 50)
    print("Test 2: Invalid length PNR")
    print("=" * 50)
    test_invalid_length_pnr()
    print("\n✅ Invalid length PNR test passed!\n")
    
    print("=" * 50)
    print("Test 3: Invalid PNR value")
    print("=" * 50)
    test_invalid_pnr_value()
    print("\n✅ Invalid PNR value test passed!\n")
    
    print("=" * 50)
    print("Test 4: Get Train Start Date")
    print("=" * 50)
    test_get_train_start_date()
    test_get_train_start_date_none()
    print("\n✅ Train start date tests passed!\n")
    
    print("=" * 50)
    print("Test 5: Get Train Number")
    print("=" * 50)
    test_get_train_number()
    test_get_train_number_none()
    print("\n✅ Train number tests passed!\n")
    
    print("=" * 50)
    print("Test 6: Check Confirm Status")
    print("=" * 50)
    test_check_confirm_status()
    test_check_confirm_status_none()
    print("\n✅ Confirm status tests passed!\n")
    
    print("=" * 50)
    print("Test 7: Get Coach and Berth")
    print("=" * 50)
    test_get_coach_and_berth()
    test_get_coach_and_berth_none()
    print("\n✅ Coach and berth tests passed!\n")
    
    print("=" * 50)
    print("Test 8: Get Waitlist Position")
    print("=" * 50)
    test_get_waitlist_position()
    test_get_waitlist_position_none()
    print("\n✅ Waitlist position tests passed!\n")
    
    print("=" * 50)
    print("Test 9: Get Journey Overview")
    print("=" * 50)
    test_get_journey_overview()
    test_get_journey_overview_none()
    print("\n✅ Journey overview tests passed!\n")
    
    print("=" * 50)
    print("Test 10: Get Passenger Summary")
    print("=" * 50)
    test_get_passenger_summary()
    test_get_passenger_summary_none()
    print("\n✅ Passenger summary tests passed!\n")
    
    print("=" * 50)
    print("Test 11: Get PNR Summary")
    print("=" * 50)
    test_get_pnr_summary()
    test_get_pnr_summary_none()
    print("\n✅ PNR summary tests passed!\n")
    
    print("🎉 All tests passed!")
