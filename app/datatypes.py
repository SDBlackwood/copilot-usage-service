import pydantic
from typing import Optional


class Usage(pydantic.BaseModel):
    message_id: int
    timestamp: str
    report_name: Optional[str] = None
    credits_used: int


class UsageResponse(pydantic.BaseModel):
    usage: list[Usage]


class CurrentPeriod(pydantic.BaseModel):
    text: str
    timestamp: str
    id: int
    report_id: Optional[int] = None


class CurrentPeriodResponse(pydantic.BaseModel):
    messages: list[CurrentPeriod]
