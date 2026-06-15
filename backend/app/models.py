from code import interact

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UniqueConstraint, func

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

class JobRaw(Base):
    __tablename__ = "jobs_raw"

    id         = Column(Integer, primary_key=True, index=True)
    rec_idx    = Column(String(20))
    company    = Column(String(255))
    title      = Column(String(500))
    href       = Column(String(500))
    job_name   = Column(String(100))
    is_crawled = Column(Boolean, default=False)
    crawled_at = Column(DateTime, default=func.now())

    # 복합 UNIQUE
    __table_args__ = (
        UniqueConstraint("rec_idx", "job_name", name="uq_rec_idx_job_name"),
    )