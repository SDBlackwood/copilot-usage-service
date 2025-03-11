from fastapi import FastAPI, Depends, HTTPException
import httpx
from app.settings import Settings
from app.datatypes import CurrentPeriod, CurrentPeriodResponse, ReportResponse, Usage
import pydantic
from collections import Counter

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

    response_list = []

    # Caclulate credits used for each message
    for message in current_period_usage.messages:
        credits_used = 0
        report_name = None
        timestamp = message.timestamp
        message_id = message.id

        if message.report_id is None:
            credits_used = _calculate_credits_for_message(message)
        else:
            # NOTE: we would apply the same validation on the report data as we did
            # on the billing period data here, however due to time constraints I'm skipping that.

            try:
                # Call the report endpoint to get the credits used
                response = client.get(f"{settings.report_endpoint}/{message.report_id}")
                response.raise_for_status()
                data = ReportResponse.model_validate(response.json())
                credits_used = data.credits_cost
                report_name = data.name
            except httpx.HTTPStatusError as e:
                # If report request was 404, fall back to previous calculation
                if e.response.status_code == 404:
                    credits_used = _calculate_credits_for_message(message)
                else:
                    print("Error fetching report data: ", e)
                    raise HTTPException(
                        status_code=500, detail=f"Failed to fetch report data: {e}"
                    )
            except pydantic.ValidationError as e:
                print("Error parsing report data: ", e)
                raise HTTPException(
                    status_code=500, detail=f"Failed to parse report data: {e}"
                )

        response = Usage(
            message_id=message_id, timestamp=timestamp, credits_used=credits_used
        )

        if report_name is not None:
            response.report_name = report_name

        response_list.append(response)

    return response_list


def _calculate_credits_for_message(message: CurrentPeriod) -> int:
    """
    Calculate the credits used for a message based on the message id
    """
    cost = settings.base_cost_per_message
    # Add 0.05 for each character in the message
    cost += 0.05 * len(message.text)

    # Count words by length and calculate cost
    short, medium, long = _count_words_by_length(message.text)

    # Add the credits for each bucket
    cost += short * 0.02
    cost += medium * 0.03
    cost += long * 0.04

    # Calculate the cost for the third vowels or uppercase rule
    cost += _calculate_third_vowels_or_uppercase_cost(message.text)

    # Round to the nearest integer
    return cost


def _calculate_third_vowels_or_uppercase_cost(text: str) -> int:
    """
    Given the text caclulates if any third (i.e. 3rd, 6th, 9th) character is an
    uppercase or lowercase vowel (a, e, i, o, u) add 0.3 credits for each occurrence.
    """
    cost = 0
    # Range over the text skipping every 3rd character
    for i in range(0, len(text), 3):
        if text[i].lower() in ["a", "e", "i", "o", "u"]:
            cost += 0.3
        elif text[i].isupper():
            cost += 0.3
    return round(cost, 2)


def _count_words_by_length(text: str) -> tuple[int, int, int]:
    """
    Count words in a text by their length categories:
    - short: 1-3 characters
    - medium: 4-7 characters
    - long: 8+ characters

    Returns a dictionary with counts for each category.
    """
    counter = Counter()
    for word in text.split():
        if len(word) >= 1 and len(word) <= 3:
            counter["short"] += 1
        elif len(word) >= 4 and len(word) <= 7:
            counter["medium"] += 1
        else:
            counter["long"] += 1

    return counter["short"], counter["medium"], counter["long"]
