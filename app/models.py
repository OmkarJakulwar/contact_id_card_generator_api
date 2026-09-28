from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class CardRequest(BaseModel):
    """Model representing the payload for generating a contact/ID card.

    All fields are either required or optional strings.  "firstName" and
    "lastName", "email", "phone" are required.  "includeQr" defaults to "False".  The
    "EmailStr" type automatically validates the email format if provided.
    """

    firstName: str = Field(..., description="The person's given name")
    lastName: str = Field(..., description="The person's family name")
    email: EmailStr = Field(
        ..., description="A valid email address (optional)"
    )
    phone: str = Field(
        ..., description="A telephone number (optional)"
    )

    addressLine1: Optional[str] = Field(
        None, description="First line of the street address (optional)"
    )
    city: Optional[str] = Field(None, description="City or locality (optional)")
    country: Optional[str] = Field(None, description="Country (optional)")
    postcode: Optional[str] = Field(
        None, description="Postal or ZIP code (optional)"
    )
    role: Optional[str] = Field(
        None, description="Role or title associated with the person (optional)"
    )
    theme: Optional[str] = Field(
        None, description="Visual theme for the card (optional)"
    )
    includeQr: Optional[bool] = Field(
        False,
        description="Set to true to include a QR code on the card. Defaults to false.",
    )

    includeCardImage: Optional[bool] = Field(
        False,
        description="Set to true to include a rendered image of the card in the response. Defaults to false.",
    )

    # Domain‑specific optional fields
    # example, a restaurant or hospital can provide its name here.  
    organizationName: Optional[str] = Field(
        None, description="Name of the organization or business (optional)"
    )
    # "website" accepts a URL pointing to the organization's or person's website. 
    website: Optional[HttpUrl] = Field(
        None, description="Website URL of the organization or person (optional)"
    )


class CardResponse(BaseModel):
    """Model representing the response for a generated contact/ID card."""

    cardId: str
    fullName: str
    email: Optional[str]
    phone: Optional[str]
    address: str
    role: Optional[str]
    theme: str
    createdAt: datetime
    qrPayload: Optional[str]
    qrCodeDataUrl: Optional[str]

    # Domain‑specific optional fields
    organizationName: Optional[str] = Field(
        None, description="Name of the organization or business (optional)"
    )
    website: Optional[str] = Field(
        None, description="Website URL of the organization or person (optional)"
    )

    # Base64 data URL of the rendered card image.  When ``includeCardImage`` is true in the request, the service generates a PNG representation of the card (including the QR code) and returns it here.  Clients can embed this directly into an <img> tag.  It will be ``None`` if not requested.
    cardImageDataUrl: Optional[str] = Field(
        None, description="Data URL containing a PNG of the rendered card (optional)"
    )
