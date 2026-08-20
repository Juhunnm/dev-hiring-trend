import logging
import os
import random
import time
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from config import BASE_URL
from crawler.keyword_extractor import extract_keywords
from app.database import SessionLocal
from app.models import JobPosting, JobPostingSkill, PostingStatus, Skill

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MIN_CONTENT_LENGTH = 50  # 이보다 짧으면 텍스트 추출 실패(이미지 공고 등)로 간주


def is_image_posting(content: str) -> bool:
    """공고 본문이 텍스트로 거의 안 잡히면 이미지 기반 공고로 추정.
    TODO(stage 2): True인 경우 로컬 LLM(Ollama)로 이미지 OCR + 키워드 추출 연결
    """
    return len(content.strip()) < MIN_CONTENT_LENGTH


def fetch_detail_content(page, url: str) -> str:
    page.goto(f"{BASE_URL}{url}")
    time.sleep(random.uniform(0.5, 1.5))
    page.wait_for_selector(".iframe_content", timeout=10000)

    iframe_src = page.query_selector(".iframe_content").get_attribute("src")
    page.goto(f"https://www.saramin.co.kr{iframe_src}")
    time.sleep(random.uniform(1, 2.3))

    return page.inner_text("body")


def sync_skills(db, skill_cache: dict[str, Skill], posting: JobPosting, tech_stack: str):
    """추출된 기술 스택과 현재 연결된 skills를 동기화 (추가/제거 모두 반영)."""
    new_names = {t.strip() for t in tech_stack.split(",") if t.strip()}
    current_names = {s.name for s in posting.skills}

    for name in new_names - current_names:
        skill = skill_cache.get(name) or db.query(Skill).filter(Skill.name == name).first()
        if not skill:
            skill = Skill(name=name)
            db.add(skill)
            db.flush()
        skill_cache[name] = skill
        db.add(JobPostingSkill(job_posting_id=posting.id, skill_id=skill.id))

    if current_names - new_names:
        (
            db.query(JobPostingSkill)
            .filter(JobPostingSkill.job_posting_id == posting.id)
            .filter(JobPostingSkill.skill_id.in_(
                s.id for s in posting.skills if s.name in (current_names - new_names)
            ))
            .delete(synchronize_session=False)
        )


def crawl_posting(page, db, skill_cache: dict[str, Skill], posting: JobPosting):
    try:
        content = fetch_detail_content(page, posting.url)

        if is_image_posting(content):
            logger.warning("이미지 공고로 추정 (id=%s), tech_stack 추출 스킵", posting.id)

        tech_stack = extract_keywords(content)

        posting.content = content
        posting.status = PostingStatus.CRAWLED
        posting.crawled_at = datetime.now(timezone.utc)
        sync_skills(db, skill_cache, posting, tech_stack)
        db.commit()

    except Exception as e:
        logger.error("크롤링 실패 (id=%s, url=%s): %s: %s", posting.id, posting.url, type(e).__name__, e)
        db.rollback()
        try:
            posting.status = PostingStatus.FAILED
            db.commit()
        except Exception as e2:
            logger.error("실패 기록도 실패 (id=%s): %s: %s", posting.id, type(e2).__name__, e2)
            db.rollback()


def main():
    db = SessionLocal()
    skill_cache: dict[str, Skill] = {}

    postings = db.query(JobPosting).filter(
        JobPosting.status.in_([PostingStatus.PENDING, PostingStatus.FAILED])
    ).all()
    logger.info("총 %d개 공고 크롤링 시작", len(postings))

    headless = os.getenv("HEADLESS", "true").lower() == "true"

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        for i, posting in enumerate(postings):
            logger.info("[%d/%d] %s - %s", i + 1, len(postings), posting.company, posting.title)
            crawl_posting(page, db, skill_cache, posting)

        browser.close()

    db.close()


if __name__ == "__main__":
    main()
