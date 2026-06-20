from code import interact
from xmlrpc.client import boolean

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UniqueConstraint, func

from app.database import Base


class JobDetail(Base):
    __tablename__ = "job_details"

    id         = Column(Integer, primary_key=True, index=True)
    company    = Column(String(255))
    title      = Column(String(500))
    job_name   = Column(String(100))
    tech_stack = Column(String(500))
    content    = Column(Text)
    href       = Column(String(500))
    date       = Column(String(20)) 
    is_failed = Column(Boolean,default=False)
    created_at = Column(DateTime, default=func.now())

class JobIndex(Base):
    __tablename__ = "job_indexes"

    id         = Column(Integer, primary_key=True, index=True)
    rec_idx    = Column(String(20))
    company    = Column(String(255))
    title      = Column(String(500))
    href       = Column(String(500))
    job_name   = Column(String(100))
    is_crawled = Column(Boolean, default=False)
    is_failed = Column(Boolean,default=False)
    crawled_at = Column(DateTime, default=func.now())

    # 복합 UNIQUE
    __table_args__ = (
        UniqueConstraint("rec_idx", "job_name", name="uq_rec_idx_job_name"),
    )