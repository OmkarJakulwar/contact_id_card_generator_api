#Unit tests for the Contact/ID Card Generator API.

from __future__ import annotations

import json
import re
from typing import Optional

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from app.config import settings


client = TestClient(app)


def test_missing_required_fields_returns_422() -> None:
    """Missing ``firstName`` or ``lastName`` should result in a 422 error."""

    response = client.post(
        "/card/generate",
        json={"lastName": "Doe"},
    )
    assert response.status_code == 422
    # The response should indicate a validation error for missing firstName
    data = response.json()
    assert data["detail"]


def test_invalid_email_returns_422() -> None:
    """An incorrectly formatted email should trigger Pydantic validation."""

    payload = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "invalid-email",
    }
    response = client.post("/card/generate", json=payload)
    assert response.status_code == 422


def test_invalid_phone_returns_400() -> None:
    """Phone numbers with invalid characters should return a 400 error."""

    payload = {
        "firstName": "John",
        "lastName": "Doe",
        "phone": "123-ABC-7890",
    }
    response = client.post("/card/generate", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "Invalid phone number" in data["detail"]


def test_address_formatting() -> None:
    """Address components should be combined into a single string."""

    payload = {
        "firstName": "Jane",
        "lastName": "Doe",
        "addressLine1": "123 Main St",
        "city": "Dublin",
        "country": "Ireland",
    }
    response = client.post("/card/generate", json=payload)
    assert response.status_code == 201
    data = response.json()
    # Address should include the provided parts in order, separated by comma
    assert data["address"] == "123 Main St, Dublin, Ireland"


def test_qr_generation_included() -> None:
    """When includeQr is true, the response should include a payload and a data URL."""

    payload = {
        "firstName": "Alice",
        "lastName": "Smith",
        "email": "alice@example.com",
        "includeQr": True,
    }
    response = client.post("/card/generate", json=payload)
    assert response.status_code == 201
    data = response.json()
    # qrPayload should be a JSON string containing cardId and email
    qr_payload = data.get("qrPayload")
    assert qr_payload is not None
    decoded = json.loads(qr_payload)
    assert decoded["email"] == "alice@example.com"
    assert decoded["cardId"] == data["cardId"]
    # qrCodeDataUrl should be a base64 PNG data URL
    qr_url = data.get("qrCodeDataUrl")
    assert qr_url is not None
    assert qr_url.startswith("data:image/png;base64,")
    # The base64 portion should be decodable
    encoded_part = qr_url.split(",", 1)[1]
    import base64

    base64.b64decode(encoded_part)


def test_qr_not_included_when_false() -> None:
    """If includeQr is false or omitted, QR related fields should be null."""

    payload = {
        "firstName": "Bob",
        "lastName": "Jones",
        # includeQr omitted defaults to false
    }
    response = client.post("/card/generate", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["qrPayload"] is None
    assert data["qrCodeDataUrl"] is None


def test_theme_defaulting() -> None:
    """When a theme is not provided, the response should use the default from settings."""

    payload = {"firstName": "John", "lastName": "Snow"}
    response = client.post("/card/generate", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["theme"] == settings.default_theme


def test_card_image_generation() -> None:
    """When includeCardImage is true, the response should include a card image data URL."""

    payload = {
        "firstName": "Eve",
        "lastName": "Black",
        "email": "eve@example.com",
        "addressLine1": "42 High St",
        "city": "Dublin",
        "country": "Ireland",
        "includeQr": True,
        "includeCardImage": True,
    }
    response = client.post("/card/generate", json=payload)
    assert response.status_code == 201
    data = response.json()

    # cardImageDataUrl should be a base64 PNG data URL
    img_url = data.get("cardImageDataUrl")
    assert img_url is not None
    assert img_url.startswith("data:image/png;base64,")

    # Ensure the base64 portion decodes without error
    encoded_part = img_url.split(",", 1)[1]
    import base64

    decoded = base64.b64decode(encoded_part)

    # The decoded image data should have non-zero length
    assert len(decoded) > 0

    # If a QR code was requested, the image should still include the QR data
    assert data.get("qrCodeDataUrl") is not None
