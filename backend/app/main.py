from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import JobCategory, JobPosting, JobPostingCategory, JobPostingSkill, PostingStatus, Skill
from app.schemas import JobPostingResponse, LastUpdatedResponse, StatsResponse

load_dotenv()

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[os.getenv("FRONTEND_URL")],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.get("/")
def root():
    return {"message": "hello"}


def _to_response(posting: JobPosting) -> JobPostingResponse:
    return JobPostingResponse(
        id=posting.id,
        company=posting.company,
        title=posting.title,
        url=posting.url,
        status=posting.status.value,
        categories=[c.name for c in posting.categories],
        skills=[s.name for s in posting.skills],
    )


# 전체 공고
@app.get("/api/jobs", response_model=list[JobPostingResponse])
def get_jobs(db: Session = Depends(get_db)):
    postings = (
        db.query(JobPosting)
        .options(joinedload(JobPosting.categories), joinedload(JobPosting.skills))
        .all()
    )
    return [_to_response(p) for p in postings]


# 직무별 공고
@app.get("/api/jobs/{job_name}", response_model=list[JobPostingResponse])
def get_job_by_name(job_name: str, db: Session = Depends(get_db)):
    postings = (
        db.query(JobPosting)
        .join(JobPosting.categories)
        .filter(JobCategory.name == job_name)
        .options(joinedload(JobPosting.categories), joinedload(JobPosting.skills))
        .all()
    )
    return [_to_response(p) for p in postings]


# 카테고리별 직무 이름 (공고 수 많은 순)
@app.get("/api/job-categories")
def get_job_categories(db: Session = Depends(get_db)):
    rows = (
        db.query(JobCategory.name, func.count(JobPostingCategory.job_posting_id).label("cnt"))
        .join(JobPostingCategory, JobPostingCategory.category_id == JobCategory.id)
        .join(JobPosting, JobPosting.id == JobPostingCategory.job_posting_id)
        .filter(JobPosting.status != PostingStatus.PENDING)
        .group_by(JobCategory.name)
        .order_by(func.count(JobPostingCategory.job_posting_id).desc())
        .all()
    )
    return [r.name for r in rows]


# 기술스택 통계
@app.get("/api/stats", response_model=list[StatsResponse])
def get_stats(job_name: str | None = None, db: Session = Depends(get_db)):
    query = db.query(
        Skill.name,
        func.count(func.distinct(JobPostingSkill.job_posting_id)).label("cnt"),
    ).join(JobPostingSkill, JobPostingSkill.skill_id == Skill.id)

    if job_name:
        query = (
            query.join(JobPosting, JobPosting.id == JobPostingSkill.job_posting_id)
            .join(JobPostingCategory, JobPostingCategory.job_posting_id == JobPosting.id)
            .join(JobCategory, JobCategory.id == JobPostingCategory.category_id)
            .filter(JobCategory.name == job_name)
        )

    rows = query.group_by(Skill.name).order_by(
        func.count(func.distinct(JobPostingSkill.job_posting_id)).desc()
    ).all()

    return [{"tech": name, "count": cnt} for name, cnt in rows]


# 메타 데이터 (마지막 목록 수집 시각)
@app.get("/api/last-updated", response_model=LastUpdatedResponse)
def get_last_updated(db: Session = Depends(get_db)):
    result = db.query(func.max(JobPosting.indexed_at)).scalar()
    return {"last_updated": result}
