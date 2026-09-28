"""Card generation service. This module contains the core logic for transforming a CardRequest into a CardResponse, including data normalization, validation, and optional QR code and image generation.  
The main function is ``generate_card``, which takes a CardRequest and produces a fully populated CardResponse.  
This service is designed to be reusable and can be called from various parts of the application, such as API endpoints or background tasks.
"""

from __future__ import annotations

import base64
import json
import uuid
from datetime import datetime, timezone
from io import BytesIO
from typing import Optional

import qrcode


from ..config import settings
from ..models import CardRequest, CardResponse
from ..utils.validators import format_address, validate_phone

from PIL import Image, ImageDraw, ImageFont

def generate_card(request: CardRequest) -> CardResponse:
    
    # Validate phone number if provided
    if request.phone is not None and not validate_phone(request.phone):
        raise ValueError("Invalid phone number format")

    # Concatenate first and last name
    full_name = f"{request.firstName.strip()} {request.lastName.strip()}"

    # Normalize address components into a single string
    address = format_address(
        request.addressLine1, request.city, request.postcode, request.country
    )

    # Determine the theme: request overrides environment default
    theme = request.theme or settings.default_theme

    # Generate a unique UUID for the card
    card_id = str(uuid.uuid4())

    # Timestamp using UTC ISO format
    created_at = datetime.now(timezone.utc)

    # Prepare optional QR code fields
    qr_payload: Optional[str] = None
    qr_data_url: Optional[str] = None
    qr_img: Optional[object] = None

    if request.includeQr:
        # Compose payload containing the cardId and optionally the email
        payload_data = {"cardId": card_id}
        if request.email:
            payload_data["email"] = request.email
        # Convert payload to a compact JSON string
        qr_payload = json.dumps(payload_data, separators=(",", ":"))
        # Build the QR code using the qrcode library
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M, # type: ignore
            box_size=10,
            border=4,
        )
        qr.add_data(qr_payload)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Convert the PIL image to a Base64 string using an in‑memory buffer【275568671752934†L107-L119】
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG") # type: ignore
        img_bytes = buffer.getvalue()
        encoded = base64.b64encode(img_bytes).decode("utf-8")
        qr_data_url = f"data:image/png;base64,{encoded}"

    response = CardResponse(
        cardId=card_id,
        fullName=full_name,
        email=request.email,
        phone=request.phone,
        address=address,
        role=request.role,
        theme=theme,
        createdAt=created_at,
        qrPayload=qr_payload,
        qrCodeDataUrl=qr_data_url,
        organizationName=request.organizationName,
        website=str(request.website) if request.website is not None else None,
        cardImageDataUrl=None,  # will be filled in below if requested
    )

    # Generate the card image if requested, using Pillow to create a visually appealing design based on the selected theme.
    if request.includeCardImage:
        try:

            # Define dimensions and basic layout parameters
            width, height = 500, 250
            # Choose colours based on the selected theme
            if theme.lower() == "dark":
                bg_color = (34, 34, 34)
                text_color = (255, 255, 255)
                accent_color = (85, 85, 85)
            elif theme.lower() == "blue":
                bg_color = (230, 241, 255)
                text_color = (0, 0, 80)
                accent_color = (173, 216, 230)
            else:
                # default theme
                bg_color = (255, 255, 255)
                text_color = (0, 0, 0)
                accent_color = (240, 240, 240)

            # Create base image
            card_image = Image.new("RGB", (width, height), color=bg_color)
            draw = ImageDraw.Draw(card_image)

            # Load a default font; if unavailable, fallback to a basic font
            try:
                font_large = ImageFont.truetype("arial.ttf", 28)
                font_small = ImageFont.truetype("arial.ttf", 16)
            except Exception:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # Draw header background
            header_height = 60
            draw.rectangle([(0, 0), (width, header_height)], fill=accent_color)

            # Draw the full name in the header
            draw.text((20, 15), full_name, font=font_large, fill=text_color)

            # Prepare lines for contact details
            y_offset = header_height + 10
            line_spacing = 22
            info_lines = []
            if request.email:
                info_lines.append(f"Email: {request.email}")
            if request.phone:
                info_lines.append(f"Phone: {request.phone}")
            if address:
                info_lines.append(f"Address: {address}")
            if request.role:
                info_lines.append(f"Role: {request.role}")
            if request.organizationName:
                info_lines.append(f"Organization: {request.organizationName}")
            if request.website:
                info_lines.append(f"Website: {request.website}")

            for line in info_lines:
                draw.text((20, y_offset), line, font=font_small, fill=text_color)
                y_offset += line_spacing

            # If QR code was generated, paste it onto the card
            if qr_img is not None:
                # Resize the QR code to fit into the card
                qr_size = 120
                qr_img_resized = qr_img.resize((qr_size, qr_size)) # type: ignore
                # Place QR code at bottom right
                qr_x = width - qr_size - 20
                qr_y = height - qr_size - 20
                card_image.paste(qr_img_resized, (qr_x, qr_y))

            # Convert the card image to a Base64 data URL
            buffer = BytesIO()
            card_image.save(buffer, format="PNG")
            encoded_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
            response.cardImageDataUrl = f"data:image/png;base64,{encoded_img}"
        except Exception:
            # In case of any error during image generation, leave the field as None
            response.cardImageDataUrl = None

    return response
