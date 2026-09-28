# Contact/ID Card Generator API

## Overview

This project implements a "FastAPI" service that
creates normalized "contact/identity cards" from user input.  It accepts
personal details such as name, email, phone number and address, normalizes
them into a structured JSON response, and optionally embeds a QR code, 
and then you get a generated image through pillow. 

### Features

- "Generate cards via POST /card/generate" – supply a JSON payload and
  receive a normalized card with a unique UUID, ISO timestamp, combined
  address and optional QR code.  A fully rendered card image can also
  be included in the response when requested.

- "Health check via GET /health" – returns "{ "status": "ok" }"to
  verify the service is running.

- "Schema discovery via GET /schema" – returns the JSON schemas for the
  request and response models to aid client integration.

- "Auto‑validated input" – required fields are enforced, emails are
  validated using Pydantic's "EmailStr" type and phone numbers are checked
  using a simple regular expression.

- "QR code generation" – uses the
  ["qrcode" library](https://pypi.org/project/qrcode/) to produce a QR
  code image; the image is converted to a Base64 data URL following
  established patterns.

- "Card image rendering" – optionally render the entire contact card as
  a PNG image.  When user client set "includeCardImage" to "true", the API
  draws a simple card layout using Pillow (including the QR code if
  requested) and returns it as a Base64‑encoded data URL.

- "Configurable defaults" – the default visual theme is read from the
  "DEFAULT_THEME" environment variable via Pydantic settings.

- "AWS Lambda ready" – includes an optional "handler" object using
  Mangum to adapt the ASGI app for Lambda.  No local state
  or file system access is used, ensuring compatibility with serverless
  environments.


## Endpoint Usage

### "POST /card/generate"

Generate a new contact/ID card.  The request body accepts the
following JSON fields (all strings unless noted):

 Field             Required?  Description                                        

 "firstName"         Yes        Person's given name                               
 "lastName"          Yes        Person's family name                             
 "email"              No        Valid email address; validated automatically     
 "phone"              No        Telephone number; must contain only digits and allowed symbols
 "addressLine1"       No        First line of the street address                   
 "city"               No        City or locality                                  
 "country"            No        Country                                           
 "postcode"           No        Postal or ZIP code                                
 "role"               No        Role or title associated with the person          
 "theme"              No        Visual theme for the card (e.g., "default", "dark", "blue") 
 "includeQr"          No (bool) Whether to include a QR code; defaults to "false" 
 "includeCardImage"   No (bool) Whether to include a rendered card image; defaults to "false" 
"organizationName"    No        Name of the organization or business (optional) 
 "website"            No        Website URL of the organization or person (optional) 

Example request:

```json
{
  "firstName": "Alice",
  "lastName": "Smith",
  "email": "alice@example.com",
  "phone": "+353 83 123 4567",
  "addressLine1": "1 College Green",
  "city": "Dublin",
  "country": "Ireland",
  "role": "Student",
  "theme": "dark",
  "includeQr": true,
  "includeCardImage": true,
  "organizationName": "Tasty Table",
  "website": "https://tastytable.ie"
}
```

Successful response ("201 Created"):

```json
{
  "cardId": "8a165b72-e1a4-4d0f-bb71-9ef5f253b674",
  "fullName": "Alice Smith",
  "email": "alice@example.com",
  "phone": "+353 83 123 4567",
  "address": "1 College Green, Dublin, Ireland",
  "role": "Student",
  "theme": "dark",
  "createdAt": "2026-02-21T13:45:30.123456+00:00",
  "qrPayload": "{\"cardId\":\"8a165b72-e1a4-4d0f-bb71-9ef5f253b674\",\"email\":\"alice@example.com\"}",
  "qrCodeDataUrl": "data:image/png;base64,iVBORw0KGgoAAAANSUhEU...",
  "organizationName": "Tasty Table",
  "website": "https://tastytable.ie",
  "cardImageDataUrl": "data:image/png;base64,iVBORw0KGg..."
}
```

If "includeQr" is omitted or set to "false", the "qrPayload" and
"qrCodeDataUrl" fields will be "null".

### "GET /health"

Returns a simple JSON object to indicate that the service is running:

```json
{ "status": "ok" }
```

### "GET /schema"

Returns the JSON schema definitions for both the request and response models.  This
endpoint is useful for client code generation and validating payloads
against the API contract.

Example response:

```json
{
  "request": { /* JSON Schema for CardRequest */ },
  "response": { /* JSON Schema for CardResponse */ }
}
```

## How others can use this API

This API can act as a lightweight "identity provider" for any application.  
Here are a few ways you can integrate it:

- Customer profiles: When a user signs up for your e‑commerce or
  CRM project, call "POST /card/generate" with the customer's
  details to produce a standardized identity card.  Store the
  resulting "cardId" and the card JSON in your database.

- Student profiles: In school or university portals, create
  student ID cards with roles such as "Student" and include a
  personalized theme.  The QR code can embed the student ID and be
  printed on physical cards.  You can also set "includeCardImage" to
  "true" to receive a fully rendered PNG of the card; embed the
  returned "cardImageDataUrl" directly into your portal without
  additional any king of styling.


To call the API from Python, you can use the `requests` library:

python code
import requests

payload = {
    "firstName": "Charlie",
    "lastName": "Brown",
    "includeQr": True,
    "includeCardImage": True
}
response = requests.post("http://localhost:8000/card/generate", json=payload)
card = response.json()
print(card["cardId"], card.get("qrCodeDataUrl"))
if card.get("cardImageDataUrl"):
    # Decode the Base64 image and save it for inspection
    import base64
    with open("generated_card.png", "wb") as f:
        f.write(base64.b64decode(card["cardImageDataUrl"].split(",", 1)[1]))


## AWS Lambda deployment

The api service is designed to run on AWS Lambda.  To deploy:

1. Install the "mangum" package.
2. Wrap the FastAPI app with Mangum – this project defines a
   "handler" object in "app/main.py" for this purpose.
3. Build a deployment package or container image containing the
   application code and dependencies in a docker.
4. Configure AWS Lambda to use `app.main.handler` as the entry point.
5. Use API Gateway to route HTTP requests to your Lambda function.


## Running tests

Install the dev dependencies and run below command:
pytest


This will execute the unit tests under the "tests/" directory and
verify validation, address formatting, QR code generation.