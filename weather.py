from typing import Any
import httpx
from fastmcp import FastMCP

mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_req(url:str) -> dict[str: Any] | None:
    """
    Make a request to the NWS API with proper error handeling.
    """
    headers = {
        'User-Agent': USER_AGENT, 
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
        
def format_alert(feature: dict) -> str:
    """
    Format an alert feature into a readable string.
    """
    props = feature["properties"]
    return f"""
        Event: {props.get("event", "Unknown")}
        Area: {props.get("areaDesc", "Unknown")}
        Severity: {props.get("severity", "Unknown")}
        Description: {props.get("description", "No description available.")}
        Instructions: {props.get("instruction", "No specific instructions provided.")}
    """

@mcp.tool
async def get_alerts(state: str) -> str:
    """
    Get alerts for a US state.
    
    Args:
        state: Two-Letter US State Code. (example: CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_req(url)
    if not data or "features" not in data:
        return "Unable to fetch alerts, or no alerts found."
    if not data["features"]:
        return "No active alerts for this state."
    alerts = [format_alert(feature) for feature in data['features']]
    return "\n---\n".join(alerts)

@mcp.tool
async def get_forecast(latitude: float, longitude: float) -> str:
        """
        Get weather forecast for the given location.
        
        Args: 
            latitude: latitude of the locaton
            longitude: longitude of the location
        """

        points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
        points_data = await make_nws_req(points_url)

        if not points_data:
            return "Unable to fetch the forecast data for this endpoint."
        
        forecast_url = points_data["properties"]["forecast"]
        forecast_data = await make_nws_req(forecast_url)

        if not forecast_data:
            return "Unable to fetch detailed forecast."
        
        periods = forecast_data['properties']['periods']
        forecasts = []

        for period in periods:
            forecast = f"""
                        Period: {period['name']}
                        Temperature: {period['temperature']}˚{period['temperatureUnit']}
                        Wind: {period['windSpeed']} {period["windDirection"]}
                        Forecast" {period['detailedForecast']}
                        """
            forecasts.append(forecasts)
        return "\n---\n".join(forecasts)
        
def main():
    mcp.run(transport='stdio')

if __name__ == '__main__':
    main()
