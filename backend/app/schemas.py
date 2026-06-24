from pydantic import BaseModel
from datetime import datetime

# /jobs 응답 형태
class JobDetailResponse(BaseModel):
    id: int
    company: str
    title: str
    job_name: str
    tech_stack: str
    href: str
    date: str

    class Config:
        from_attributes = True 

# /stats 응답 형태
class StatsResponse(BaseModel):
    tech: str
    count: int

# /last-updated 응답 형태
class LastUpdatedResponse(BaseModel):
    last_updated: datetime | None