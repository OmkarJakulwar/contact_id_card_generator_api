"""
FastAPI application for generating contact/ID cards.

This module defines the web API using FastAPI.  It exposes three
endpoints:

* "POST /card/generate" generates a card from a request body.
* "GET /health" a simple health check for monitoring.
* "GET /schema" returns JSON schemas for the request and response
  models to get client integrations.

The main logic for card generation is in the "generate_card" function in the "services/card_generator.py" module,
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from .models import CardRequest, CardResponse
from .services.card_generator import generate_card
 

# Create the FastAPI application.
app = FastAPI(title="Contact/ID Card Generator API")


@app.get("/")
def Home() -> JSONResponse:
    # A simple welcome message for the root endpoint.  This is not required
    return JSONResponse(
        content={
            "message": "Welcome to the Contact/ID Card Generator API! "
                       "Visit /docs for API documentation."
        }
    )


@app.post("/card/generate", response_model=CardResponse, status_code=201)
async def create_card(request: CardRequest) -> CardResponse:
    # Generate a card from the request.  
    try:
        card = generate_card(request)
    except ValueError as exc:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(exc))
    return card


@app.get("/health")
async def health() -> dict[str, str]:
    # A simple health check endpoint. 
    return {"status": "ok"}


@app.get("/schema")
async def schema() -> dict[str, dict]:
    # Return the JSON schemas for the request and response models.  This can be useful for client integrations that want to validate their payloads against the API's expected formats.

    return {
        "request": CardRequest.model_json_schema(),
        "response": CardResponse.model_json_schema(),
    }


# AWS Lambda integration
try:
    # Only import Mangum when available.  If the package is missing
    # (e.g., running locally), this import will fail silently.
    from mangum import Mangum  # type: ignore

    handler = Mangum(app, lifespan="off")
except Exception:
    # In local development there is no need to expose a handler.
    handler = None
