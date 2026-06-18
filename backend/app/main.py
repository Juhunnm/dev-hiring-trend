from collections import Counter
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import JobDetail

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CLIENT_URL")],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "hello"}

@app.get('/jobs')
def get_jobs(db : Session = Depends(get_db)):
    jobs = db.query(JobDetail).all()
    return jobs

# 직무별 공고
@app.get('/jobs/{job_name}')
def get_jobs_by_name(job_name : str,db : Session = Depends(get_db)):
    jobs= db.query(JobDetail).filter(JobDetail.job_name == job_name).all()
    return jobs

# 기술스택 통계
@app.get("/stats")
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