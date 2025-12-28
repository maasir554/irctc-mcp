STATUS_MAP = {
    # Core Statuses
    "CNF": "Confirmed",
    "RAC": "Reservation Against Cancellation",
    "WL": "Waitlist",
    "CAN": "Cancelled",
    "NOSB": "No Seat Berth (Child below 12)",
    "REL": "Released",
    "NR": "Nor Reported",
    
    # Waitlist Types (Priorities)
    "GNWL": "General Waitlist",
    "RLWL": "Remote Location Waitlist",
    "PQWL": "Pooled Quota Waitlist",
    "TQWL": "Tatkal Waitlist",
    "RSWL": "Roadside Station Waitlist",
    "RQWL": "Request Waitlist",
    "CKWL": "Tatkal Waitlist (Old Code)",
}

# Berth Codes (for parsing bookingStatusDetails)
BERTH_MAP = {
    "LB": "Lower Berth",
    "MB": "Middle Berth",
    "UB": "Upper Berth",
    "SL": "Side Lower",
    "SU": "Side Upper",
    "SM": "Side Middle", # Present in some Garib Rath coaches
    "WS": "Window Side", # Chair Car
    "MS": "Middle Seat", # Chair Car
    "AS": "Aisle Seat",  # Chair Car
}

def decode_ticket_status(status_code: str | None) -> str:
    if not status_code:
        return "Unknown Status"
    
    code = status_code.strip().upper()

    return STATUS_MAP.get(code, f"Unknown Booking Status Code - ({code})")

def decode_berth(berth_code: str | None) -> str:
    if not berth_code:
        return " "
    code = berth_code.strip().upper()
    return BERTH_MAP.get(code, f"Unknown Birth Code - {code}")
