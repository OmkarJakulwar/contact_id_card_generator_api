# Contact / ID Card Generator API

A lightweight, **serverless REST API** that turns basic personal details into a standardised **contact / ID card**. Each card has a unique ID, an optional **QR code** and an optional **rendered PNG card image**.

It is built with **FastAPI** and deployed on **AWS Lambda + API Gateway**. Any application can call it over HTTP. It is currently used by the [Campus Portal](https://github.com/OmkarJakulwar/campus_portal_Scalable_Cloud_Computing) to issue digital student ID cards during registration.

---

## Features

- **Generate cards** (`POST /card/generate`): returns a normalised card with a UUID, UTC timestamp and formatted address.
- **QR codes**: encodes the card ID and email into a QR code, returned as a Base64 data URL.
- **Card images**: renders the whole card as a PNG with Pillow, in `default`, `dark` or `blue` themes.
- **Input validation**: required fields, email format (Pydantic `EmailStr`), phone format and URL format.
- **Self-describing**: `GET /schema` returns the request and response JSON schemas. `/docs` serves interactive Swagger UI.
- **Serverless ready**: stateless, with no file system writes. Wrapped with **Mangum** so it runs on AWS Lambda.

---

## Tech Stack

Python · FastAPI · Pydantic · Pillow · qrcode · Mangum · Docker · AWS Lambda · Amazon API Gateway · Amazon ECR · Pytest

---

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/card/generate` | Generate a contact / ID card |
| GET | `/health` | Health check, returns `{"status": "ok"}` |
| GET | `/schema` | JSON schemas for the request and response |
| GET | `/docs` | Interactive API documentation (Swagger UI) |

### Request fields: `POST /card/generate`

| Field | Required | Description |
|---|---|---|
| `firstName` | Yes | Given name |
| `lastName` | Yes | Family name |
| `email` | Yes | Valid email address |
| `phone` | Yes | Digits, spaces, `+`, `-`, `(` `)` allowed |
| `addressLine1`, `city`, `postcode`, `country` | No | Combined into one `address` string |
| `role` | No | e.g. `Student`, `Staff` |
| `theme` | No | `default`, `dark` or `blue` |
| `includeQr` | No | `true` to include a QR code (default `false`) |
| `includeCardImage` | No | `true` to include a PNG card image (default `false`) |
| `organizationName` | No | Organisation / business name |
| `website` | No | Valid URL |

### Example

```bash
curl -X POST http://localhost:8000/card/generate \
  -H "Content-Type: application/json" \
  -d '{
        "firstName": "Alice",
        "lastName": "Smith",
        "email": "alice@example.com",
        "phone": "+353 83 123 4567",
        "city": "Dublin",
        "country": "Ireland",
        "role": "Student",
        "includeQr": true,
        "includeCardImage": true
      }'
```

Response (`201 Created`, shortened):

```json
{
  "cardId": "8a165b72-e1a4-4d0f-bb71-9ef5f253b674",
  "fullName": "Alice Smith",
  "email": "alice@example.com",
  "phone": "+353 83 123 4567",
  "address": "Dublin, Ireland",
  "role": "Student",
  "theme": "default",
  "createdAt": "2026-02-21T13:45:30.123456+00:00",
  "qrPayload": "{\"cardId\":\"8a165b72-...\",\"email\":\"alice@example.com\"}",
  "qrCodeDataUrl": "data:image/png;base64,iVBORw0KGgo...",
  "cardImageDataUrl": "data:image/png;base64,iVBORw0KGgo..."
}
```

Errors: `422` for missing or invalid fields (for example a bad email), `400` for an invalid phone number.

---

## Run Locally

```bash
git clone https://github.com/OmkarJakulwar/contact_id_card_generator_api.git
cd contact_id_card_generator_api

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open http://localhost:8000/docs to try the API.

Optional: set `DEFAULT_THEME` to change the theme used when a request doesn't specify one.

## Run Tests

```bash
pytest
```

The tests cover required-field validation, email and phone validation, address formatting, QR code generation, theme defaults and card image rendering.

---

## Deploy to AWS Lambda

The Dockerfile uses the official AWS Lambda Python base image, and `app.main.handler` (Mangum) is the Lambda entry point.

1. Build the image: `docker build -t id-card-api .`
2. Push it to **Amazon ECR**.
3. Create a **Lambda function** from the container image.
4. Put **API Gateway** (HTTP API) in front of it to expose `/card/generate`.

Because the service is stateless, Lambda scales it automatically with incoming requests and no servers need to be managed.

---

## Project Structure

```
app/
  main.py                  # FastAPI app, routes and Lambda handler
  models.py                # Pydantic request / response models
  config.py                # Settings (DEFAULT_THEME)
  services/card_generator.py  # Card, QR code and image generation logic
  utils/validators.py      # Phone validation and address formatting
tests/test_card_api.py     # Pytest test suite
Dockerfile                 # AWS Lambda container image
```

## Author

**Omkar Jakulwar**
