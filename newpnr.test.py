from new_pnr_status import fetch_pnr_status
from new_pnr_schema import PNRResponse


def test_fetch_pnr_status():
    """Test fetching PNR status from the API."""
    pnr_no = "8341223680"
    
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


if __name__ == "__main__":
    test_fetch_pnr_status()
    print("\n✅ Test passed!")
