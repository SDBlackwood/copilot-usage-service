from fastapi import FastAPI, Depends, HTTPException
import httpx
from app.settings import Settings
from app.datatypes import CurrentPeriod, CurrentPeriodResponse, ReportResponse, Usage
import pydantic
from collections import Counter
import re

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
        credits_used = float(0)
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
                print(
                    f"Fetching report data from: {settings.report_endpoint}/{message.report_id}"
                )
                response = client.get(f"{settings.report_endpoint}/{message.report_id}")
                response.raise_for_status()
                data = ReportResponse.model_validate(response.json())
                credits_used = float(data.credit_cost)
                report_name = data.name
                print(f"Report name: {report_name}")
                print(f"Credits used: {credits_used}")
            except httpx.HTTPStatusError as e:
                # If report request was 404, fall back to previous calculation
                if e.response.status_code == 404:
                    print("Report not found, falling back to previous calculation")
                    credits_used = _calculate_credits_for_message(message)
                else:
                    print("Error fetching report data: ", e)
                    raise HTTPException(
                        status_code=500, detail=f"Failed to fetch report data: {e}"
                    )
            except pydantic.ValidationError as e:
                # If we cannot parse the report data, fall back to previous calculation
                # We don't want to fail the entire request if one report fails to parse
                # This doesn mean that failures can go unnoticed, so we would want to add
                # logging and alerting here.
                print("Error parsing report data: ", e)
                credits_used = _calculate_credits_for_message(message)

        response = Usage(
            message_id=message_id, timestamp=timestamp, credits_used=credits_used
        )

        if report_name is not None:
            response.report_name = report_name

        # Turn into a dict and exclude missing values
        response_dict = response.model_dump(exclude_none=True)
        response_list.append(response_dict)

    return response_list


def _calculate_credits_for_message(message: CurrentPeriod) -> float:
    """
    Calculate the credits used for a message based on the message id
    """
    cost = float(settings.base_cost_per_message)
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

    # Caclulate the message char lenght
    cost += _calculate_word_length_cost(message.text)

    # If all words are unique, remove 2 credites (only if the credit is > 1)
    if cost > float(settings.base_cost_per_message) + 2 and len(
        set(message.text.split())
    ) == len(message.text.split()):
        cost -= 2

    # Convert to pallendrome and Double
    if is_pallendrome(message.text):
        cost *= 2

    # Round to 2 decimal plaes.
    # NOTE: we may want to be careful about how much we are rounding off here
    return round(cost, 2)


def _calculate_third_vowels_or_uppercase_cost(text: str) -> float:
    """
    Given the text caclulates if any third (i.e. 3rd, 6th, 9th) character is an
    uppercase or lowercase vowel (a, e, i, o, u) add 0.3 credits for each occurrence.
    """
    cost = float(0)
    # Range over the text skipping every 3rd character
    for i in range(0, len(text), 3):
        if text[i].lower() in ["a", "e", "i", "o", "u"]:
            cost += 0.3
        elif text[i].isupper():
            cost += 0.3
    return round(cost, 2)


def _count_words_by_length(text: str) -> tuple[float, float, float]:
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

    return float(counter["short"]), float(counter["medium"]), float(counter["long"])


def _calculate_word_length_cost(text: str) -> int:
    """
    Add 5 credits if messages is > 100 characters
    """
    cost = 0
    if len(text) > 100:
        cost += 5
    return cost


def is_pallendrome(text: str) -> bool:
    """
    Check if a text is a pallendrome
    """
    # Uppercase the text and remove non-alphanumeric characters
    text = text.upper()
    # Only match a-z A-Z 0-9 and otherwise replace with empty string
    regex = re.compile(r"[^a-zA-Z0-9]")
    text = regex.sub("", text)
    # Compare the text with its reverse
    return text == text[::-1]
