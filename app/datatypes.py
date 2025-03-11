import pydantic
from typing import Optional


class Usage(pydantic.BaseModel):
    message_id: int
    timestamp: str
    report_name: Optional[str] = None
    # This needs to be a float to handle the decimal places
    credits_used: float


class UsageResponse(pydantic.BaseModel):
    usage: list[Usage]


class CurrentPeriod(pydantic.BaseModel):
    text: str
    timestamp: str
    id: int
    report_id: Optional[int] = None


class CurrentPeriodResponse(pydantic.BaseModel):
    messages: list[CurrentPeriod]


class ReportResponse(pydantic.BaseModel):
    id: int
    name: str
    credit_cost: int
