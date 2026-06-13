import csv

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from server.database import get_db
from server.models import Job

app = FastAPI()

@app.get("/")
def root():
    return {"message": "hello"}

@app.get('/jobs')
def get_jobs_db(db : Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return jobs
@app.get
