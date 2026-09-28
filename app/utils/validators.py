from __future__ import annotations

import re
from typing import Iterable, Optional


# Regular expression permitting a leading plus sign followed by digits, parentheses, spaces or hyphens.  
PHONE_REGEX = re.compile(r"^\+?[0-9\-\s\(\)]+$")


def validate_phone(phone: Optional[str]) -> bool:
    """Perform a basic checks on a phone number."""
    if not phone:
        return False
    return bool(PHONE_REGEX.fullmatch(phone.strip()))


def format_address(*parts: Optional[str]) -> str:
    """Combine address components into a single string."""

    normalized = [p.strip() for p in parts if p and p.strip()]
    return ", ".join(normalized)
