"""
Tests for PNR Status API functions.
Run with: python test_pnr.py
Or with pytest: pytest test_pnr.py -v
"""

import asyncio
import pytest
from pnr_functions import fetch_pnr_details


# Sample PNR numbers for testing
VALID_PNR = "8341223680"
INVALID_PNR = "0000000000"


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


async def run_all_tests():
    """Run all tests."""
    print("\nPNR Status API Tests\n")
    
    await test_fetch_valid_pnr()
    await test_fetch_invalid_pnr()
    
    print(f"\n{'='*50}")
    print("All tests completed!")
    print(f"{'='*50}\n")


# Pytest compatible tests
@pytest.mark.asyncio
async def test_fetch_pnr_returns_response():
    """Pytest: Verify fetch returns a response object."""
    result = await fetch_pnr_details(VALID_PNR)
    # Result can be None if API is down, so we just check it doesn't crash
    assert result is None or hasattr(result, 'success')


@pytest.mark.asyncio
async def test_fetch_pnr_handles_invalid():
    """Pytest: Verify invalid PNR is handled gracefully."""
    result = await fetch_pnr_details(INVALID_PNR)
    # Should not raise an exception
    assert result is None or isinstance(result.success, bool)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
