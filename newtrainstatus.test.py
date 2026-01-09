"""Tests for new train status functions."""

import asyncio
import json
import pytest
from new_train_status_schemas import NewTrainStatusResponse
from new_train_status_functions import (
    fetch_new_train_status,
    format_delay,
    get_expected_arrival_at_station,
    get_current_train_position,
    get_train_route,
    get_upcoming_stations,
    get_train_summary,
)


# Load example data for testing
def load_example_response() -> NewTrainStatusResponse:
    """Load the example JSON file and return a parsed response."""
    with open("example-new-status.json") as f:
        data = json.load(f)
    return NewTrainStatusResponse.model_validate(data)


class TestFormatDelay:
    """Tests for format_delay function."""

    def test_on_time(self):
        assert format_delay(0) == "On Time"

    def test_delayed_minutes_only(self):
        assert format_delay(30) == "Delayed by 30 mins"

    def test_delayed_hours_and_minutes(self):
        assert format_delay(67) == "Delayed by 1h 7m"
        assert format_delay(125) == "Delayed by 2h 5m"

    def test_early(self):
        assert format_delay(-15) == "Early by 15 mins"
        assert format_delay(-5) == "Early by 5 mins"


class TestGetExpectedArrivalAtStation:
    """Tests for get_expected_arrival_at_station function."""

    def test_current_station(self):
        response = load_example_response()
        result = get_expected_arrival_at_station(response, "CDI")
        assert "currently at/near" in result
        assert "CHANDNI" in result

    def test_upcoming_station(self):
        response = load_example_response()
        result = get_expected_arrival_at_station(response, "BAU")
        assert "BURHANPUR" in result
        assert "Scheduled Arrival" in result
        assert "Expected Arrival" in result

    def test_destination_station(self):
        response = load_example_response()
        result = get_expected_arrival_at_station(response, "KCG")
        assert "KACHEGUDA" in result

    def test_previous_station(self):
        response = load_example_response()
        result = get_expected_arrival_at_station(response, "BGKT")
        assert "already passed" in result
        assert "BHAGAT KI KOTHI" in result

    def test_station_not_found(self):
        response = load_example_response()
        result = get_expected_arrival_at_station(response, "XYZ")
        assert "not found" in result

    def test_case_insensitive(self):
        response = load_example_response()
        result_upper = get_expected_arrival_at_station(response, "BAU")
        result_lower = get_expected_arrival_at_station(response, "bau")
        assert "BURHANPUR" in result_upper
        assert "BURHANPUR" in result_lower


class TestGetCurrentTrainPosition:
    """Tests for get_current_train_position function."""

    def test_returns_train_info(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "17606" in result
        assert "Bhagat Ki Kothi - Kacheguda Express" in result

    def test_shows_route(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "BHAGAT KI KOTHI" in result
        assert "KACHEGUDA" in result

    def test_shows_current_station(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "CHANDNI" in result
        assert "CDI" in result

    def test_shows_progress(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "Distance Covered" in result
        assert "Progress" in result
        assert "%" in result

    def test_shows_delay(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "Delay" in result or "On Time" in result

    def test_shows_next_stop(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "Next Stop" in result
        assert "BURHANPUR" in result


class TestGetTrainRoute:
    """Tests for get_train_route function."""

    def test_returns_route_string(self):
        response = load_example_response()
        result = get_train_route(response)
        assert "->" in result

    def test_marks_current_station(self):
        response = load_example_response()
        result = get_train_route(response)
        assert ">>>" in result
        assert "<<<" in result

    def test_includes_source_and_destination(self):
        response = load_example_response()
        result = get_train_route(response)
        assert "BGKT" in result
        assert "KCG" in result

    def test_without_non_stops(self):
        response = load_example_response()
        result = get_train_route(response, include_non_stops=False)
        # Non-stop stations should not have brackets
        assert "[" not in result or ">>>" in result

    def test_with_non_stops(self):
        response = load_example_response()
        result = get_train_route(response, include_non_stops=True)
        # Should include bracketed non-stop stations
        assert "[" in result


class TestGetUpcomingStations:
    """Tests for get_upcoming_stations function."""

    def test_returns_upcoming_stations(self):
        response = load_example_response()
        result = get_upcoming_stations(response)
        assert "Upcoming Stations" in result

    def test_respects_limit(self):
        response = load_example_response()
        result = get_upcoming_stations(response, limit=3)
        # Should show "... and X more stations" if there are more
        assert "1." in result
        assert "2." in result
        assert "3." in result

    def test_shows_station_details(self):
        response = load_example_response()
        result = get_upcoming_stations(response, limit=1)
        assert "BURHANPUR" in result
        assert "Scheduled" in result

    def test_shows_delay_info(self):
        response = load_example_response()
        result = get_upcoming_stations(response, limit=1)
        assert "Delayed" in result or "Early" in result or "Platform" in result


class TestGetTrainSummary:
    """Tests for get_train_summary function."""

    def test_shows_train_name_and_number(self):
        response = load_example_response()
        result = get_train_summary(response)
        assert "17606" in result
        assert "Bhagat Ki Kothi - Kacheguda Express" in result

    def test_shows_route(self):
        response = load_example_response()
        result = get_train_summary(response)
        assert "BHAGAT KI KOTHI" in result
        assert "KACHEGUDA" in result
        assert "→" in result

    def test_shows_position(self):
        response = load_example_response()
        result = get_train_summary(response)
        assert "📍" in result

    def test_shows_delay_status(self):
        response = load_example_response()
        result = get_train_summary(response)
        assert "⏱️" in result
        assert "Running" in result or "late" in result or "on time" in result

    def test_shows_next_stop(self):
        response = load_example_response()
        result = get_train_summary(response)
        assert "➡️" in result
        assert "Next" in result


class TestFetchNewTrainStatus:
    """Tests for fetch_new_train_status function (integration tests)."""

    @pytest.mark.asyncio
    async def test_fetch_valid_train(self):
        """Test fetching status for a valid running train."""
        # Using a commonly running train for testing
        result = await fetch_new_train_status("12138", start_day=0)
        
        if result is not None:
            assert result.status == True
            assert result.data.train_number == "12138"
            assert result.data.train_name
            assert result.data.source
            assert result.data.destination

    @pytest.mark.asyncio
    async def test_fetch_with_start_day(self):
        """Test fetching with different start_day values."""
        # Test with yesterday's train
        result = await fetch_new_train_status("12138", start_day=1)
        
        # Result may or may not be available depending on the train schedule
        # Just verify no exception is raised
        assert result is None or isinstance(result, NewTrainStatusResponse)

    @pytest.mark.asyncio
    async def test_fetch_invalid_train(self):
        """Test fetching status for an invalid train number."""
        result = await fetch_new_train_status("99999", start_day=0)
        # Should return None or a response with status=False
        assert result is None or result.status == False


class TestSchemaValidation:
    """Tests for schema validation."""

    def test_example_json_validates(self):
        """Test that the example JSON validates against the schema."""
        response = load_example_response()
        assert response.status == True
        assert response.message == "Success"
        assert response.data.train_number == "17606"

    def test_data_fields(self):
        """Test that data fields are correctly parsed."""
        response = load_example_response()
        data = response.data
        
        assert data.train_name == "Bhagat Ki Kothi - Kacheguda Express"
        assert data.source == "BGKT"
        assert data.destination == "KCG"
        assert data.delay == 67
        assert data.total_distance == 1946
        assert data.distance_from_source == 1232

    def test_upcoming_stations(self):
        """Test that upcoming stations are correctly parsed."""
        response = load_example_response()
        upcoming = response.data.upcoming_stations
        
        assert len(upcoming) > 0
        # First non-empty station should be BURHANPUR
        burhanpur = next((s for s in upcoming if s.station_code == "BAU"), None)
        assert burhanpur is not None
        assert burhanpur.station_name == "BURHANPUR"
        assert burhanpur.arrival_delay == 64

    def test_previous_stations(self):
        """Test that previous stations are correctly parsed."""
        response = load_example_response()
        previous = response.data.previous_stations
        
        assert len(previous) > 0
        # First station should be source
        assert previous[0].station_code == "BGKT"

    def test_helper_methods(self):
        """Test helper methods on the data model."""
        response = load_example_response()
        data = response.data
        
        hours, mins = data.get_delay_hours_minutes()
        assert hours == 1
        assert mins == 7
        
        progress = data.get_progress_percentage()
        assert 63 < progress < 64  # Should be around 63.3%
        
        remaining = data.get_remaining_distance()
        assert remaining == 714


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
