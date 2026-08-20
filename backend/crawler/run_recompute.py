import logging

from crawler.keyword_extractor import extract_keywords
from app.database import SessionLocal
from app.models import JobDetail

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    db = SessionLocal()
    jobs = db.query(JobDetail).filter(JobDetail.content != "").all()
    logger.info("총 %d개 재추출 시작", len(jobs))

    updated = 0
    for i, job in enumerate(jobs):
        new_tech = extract_keywords(job.content)
        if job.tech_stack != new_tech:
            job.tech_stack = new_tech
            updated += 1
        if (i + 1) % 500 == 0:
            db.commit()
            logger.info("%d/%d 처리...", i + 1, len(jobs))

    db.commit()
    logger.info("완료: %d개 갱신됨", updated)
    db.close()


if __name__ == "__main__":
    main()
