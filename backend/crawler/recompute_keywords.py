from app.database import SessionLocal
from app.models import JobDetail
from config import extract_keywords


def main():
    db = SessionLocal()

    jobs = db.query(JobDetail).filter(JobDetail.content != "").all()
    print(f"총 {len(jobs)}개 재추출 시작")

    updated = 0
    for i, job in enumerate(jobs):
        new_tech = extract_keywords(job.content)
        if job.tech_stack != new_tech:
            job.tech_stack = new_tech
            updated += 1
        if (i + 1) % 500 == 0:
            db.commit()
            print(f"  {i+1}/{len(jobs)} 처리...")

    db.commit()
    print(f"완료: {updated}개 갱신됨")
    db.close()


if __name__ == "__main__":
    main()
