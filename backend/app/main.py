from collections import Counter
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import JobDetail, JobIndex
from app.schemas import JobDetailResponse, LastUpdatedResponse, StatsResponse

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "hello"}

# 전체 직무 공고
@app.get('/jobs', response_model=list[JobDetailResponse])
def get_jobs(db : Session = Depends(get_db)):
    return db.query(
        JobDetail.id,
        JobDetail.company,
        JobDetail.title,
        JobDetail.job_name,
        JobDetail.tech_stack,
        JobDetail.href,
        JobDetail.date
    ).all()

# 직무별 공고
@app.get('/jobs/{job_name}',response_model=list[JobDetailResponse])
def get_job_by_name(job_name : str,db : Session = Depends(get_db)):
    return db.query(
        JobDetail.id,
        JobDetail.company,
        JobDetail.title,
        JobDetail.job_name,
        JobDetail.tech_stack,
        JobDetail.href,
        JobDetail.date,
    ).filter(JobDetail.job_name == job_name).all()
 
# 카테고리별 직무 이름
@app.get('/job-categories')
def get_job_categories(db : Session = Depends(get_db)):
    job_categories = (
        db.query(JobDetail.job_name)
        .group_by(JobDetail.job_name)
        .order_by(func.count(JobDetail.job_name)
        .desc()).all()
    )
    return [c.job_name for c in job_categories]



# 기술스택 통계
@app.get("/stats",response_model=list[StatsResponse])
def get_stats(job_name : str = None,db: Session = Depends(get_db)):
    query = db.query(JobDetail)

    if(job_name) :
        query = query.filter(JobDetail.job_name == job_name)

    jobs = query.all()

    counter = Counter()
    for job in jobs:
        if job.tech_stack:
            keywords = [k.strip() for k in job.tech_stack.split(",")]
            counter.update(keywords)

    return [
        {"tech": tech, "count": count}
        for tech, count in counter.most_common()
    ]

# 메타 데이터 (마지막 크롤링 날짜)
@app.get('/last-updated', response_model=LastUpdatedResponse)
def get_last_updated(db : Session = Depends(get_db)):
    result = db.query(func.max(JobIndex.crawled_at)).scalar()
    return{"last_updated" : result}