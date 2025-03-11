from fastapi import FastAPI, Depends, HTTPException
import httpx
from app.settings import Settings
from app.datatypes import CurrentPeriod, CurrentPeriodResponse
import pydantic

app = FastAPI()
settings = Settings()


async def egress_client():
    """
    Return a httpx client for egress requests for calling outbound endpoints
    This is so that we can easily mock the client in tests
    """
    return httpx.Client()


@app.get("/usage")
async def get_usage(client: httpx.Client = Depends(egress_client)):
    # Query the `current-period` endpoint for  raw message data for the current billing period
    # Try/Catch to handdle upstream failures and return graceful error messages
    try:
        print("Fetching billing period data from: ", settings.billing_period_endpoint)
        response = client.get(settings.billing_period_endpoint)
        response.raise_for_status()
        data = response.json()
        # Parse the data into the CurrentPeriodResponse type
        current_period_usage = CurrentPeriodResponse.model_validate(data)
    except httpx.HTTPStatusError as e:
        print("Error fetching billing period data: ", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch billing period data: {e}"
        )
    except pydantic.ValidationError as e:
        print("Error parsing billing period data: ", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to parse billing period data: {e}"
        )

    return {
        "usage": [
            {
                "message_id": 123,
                "timestamp": "2021-01-01T00:00:00Z",
                "report_name": "Report 1",
                "credits_used": 100,
            },
            {
                "message_id": 124,
                "timestamp": "2021-01-01T00:00:00Z",
                "report_name": "Report 2",
                "credits_used": 200,
            },
        ]
    }
