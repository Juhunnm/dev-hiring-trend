from datetime import datetime

from pydantic import BaseModel


# /jobs 응답 형태
class JobPostingResponse(BaseModel):
    id: int
    company: str | None
    title: str | None
    url: str | None
    status: str
    categories: list[str]
    skills: list[str]

    class Config:
        from_attributes = True


# /stats 응답 형태
class StatsResponse(BaseModel):
    tech: str
    count: int


# /last-updated 응답 형태
class LastUpdatedResponse(BaseModel):
    last_updated: datetime | None
