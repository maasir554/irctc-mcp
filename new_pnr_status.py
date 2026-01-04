import httpx
from new_pnr_schema import PNRResponse
import os
from dotenv import load_dotenv
from urllib.parse import unquote

load_dotenv()

PNR_API_PATH = os.getenv("NEW_PNR_API_PATH")
PNR_API_KEY_NAME = os.getenv("NEW_PNR_API_KEY_NAME")

def fetch_pnr_status(pnr_no: str) -> PNRResponse:
    """
    Fetch PNR status from Live API.
    
    Args:
        pnr_no: The PNR number to check
        
    Returns:
        PNRResponse object containing the PNR status data
    """
    assert PNR_API_PATH is not None
    assert PNR_API_KEY_NAME is not None
    url = PNR_API_PATH
    base_url = url.rsplit('/', 1)[0]
    
    with httpx.Client() as client:
        initial_response = client.get(base_url)
        api_key = client.cookies.get(PNR_API_KEY_NAME)

        if not api_key:
            raise ValueError("Failed to retrieve XSRF-TOKEN from cookies", initial_response)
        
        decoded_token = unquote(api_key)
        headers = {
            f'X-{PNR_API_KEY_NAME}': decoded_token,
        }
        
        body = {"pnr": pnr_no}
        
        response = client.post(url, json=body, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return PNRResponse(**data)
