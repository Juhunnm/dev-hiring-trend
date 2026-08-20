import logging

from crawler.detail_crawler import sync_skills
from crawler.keyword_extractor import extract_keywords
from app.database import SessionLocal
from app.models import JobPosting, Skill

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    db = SessionLocal()
    skill_cache: dict[str, Skill] = {}

    postings = db.query(JobPosting).filter(JobPosting.content.isnot(None), JobPosting.content != "").all()
    logger.info("총 %d개 재추출 시작", len(postings))

    updated = 0
    for i, posting in enumerate(postings):
        before = {s.name for s in posting.skills}
        tech_stack = extract_keywords(posting.content)
        sync_skills(db, skill_cache, posting, tech_stack)

        after = {t.strip() for t in tech_stack.split(",") if t.strip()}
        if before != after:
            updated += 1

        if (i + 1) % 500 == 0:
            db.commit()
            logger.info("%d/%d 처리...", i + 1, len(postings))

    db.commit()
    logger.info("완료: %d개 갱신됨", updated)
    db.close()


if __name__ == "__main__":
    main()
