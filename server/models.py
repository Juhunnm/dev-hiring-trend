from sqlalchemy import Column, DateTime, Integer, String, Text, func

from server.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id         = Column(Integer, primary_key=True, index=True)
    company    = Column(String(255))
    title      = Column(String(500))
    job_name   = Column(String(100))
    tech_stack = Column(String(500))
    content    = Column(Text)
    href       = Column(String(500))
    date       = Column(String(20))
    created_at = Column(DateTime, default=func.now())