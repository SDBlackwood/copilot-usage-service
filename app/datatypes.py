import pydantic
from typing import Optional
class Usage(pydantic.BaseModel):
    message_id: int
    timestamp: str
    report_name: Optional[str] = None
    credits_used: int

class UsageResponse(pydantic.BaseModel):
    usage: list[Usage]