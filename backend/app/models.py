import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class PostingStatus(str, enum.Enum):
    PENDING = "pending"
    CRAWLED = "crawled"
    FAILED = "failed"


class JobPosting(Base):
    __tablename__ = "job_postings"

    id           = Column(Integer, primary_key=True, index=True)
    source       = Column(String(50), nullable=False, default="saramin")
    source_id    = Column(String(20), nullable=False)  # 기존 rec_idx
    company      = Column(String(255))
    title        = Column(String(500))
    url          = Column(String(500))
    status       = Column(Enum(PostingStatus), nullable=False, default=PostingStatus.PENDING)
    content      = Column(Text)
    indexed_at   = Column(DateTime, default=func.now())   # 목록 크롤링으로 처음 발견된 시각
    crawled_at   = Column(DateTime, nullable=True)         # 상세 크롤링(본문 수집) 완료 시각
    created_at   = Column(DateTime, default=func.now())

    skills     = relationship("Skill", secondary="job_posting_skills", back_populates="postings")
    categories = relationship("JobCategory", secondary="job_posting_categories", back_populates="postings")

    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_source_source_id"),
    )


class Skill(Base):
    __tablename__ = "skills"

    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=True)

    postings = relationship("JobPosting", secondary="job_posting_skills", back_populates="skills")


class JobPostingSkill(Base):
    __tablename__ = "job_posting_skills"

    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), primary_key=True)
    skill_id        = Column(Integer, ForeignKey("skills.id"), primary_key=True)


class JobCategory(Base):
    """직무 카테고리 (기존 job_name). 한 공고가 여러 카테고리에 동시에 속할 수 있어 다대다로 분리."""
    __tablename__ = "job_categories"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    postings = relationship("JobPosting", secondary="job_posting_categories", back_populates="categories")


class JobPostingCategory(Base):
    __tablename__ = "job_posting_categories"

    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), primary_key=True)
    category_id     = Column(Integer, ForeignKey("job_categories.id"), primary_key=True)


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