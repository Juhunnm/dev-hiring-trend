import logging
import os
import random
import time
from datetime import datetime

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from config import BASE_URL
from crawler.keyword_extractor import extract_keywords
from app.database import SessionLocal
from app.models import JobDetail, JobIndex

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MIN_CONTENT_LENGTH = 50  # 이보다 짧으면 텍스트 추출 실패(이미지 공고 등)로 간주


def is_image_posting(content: str) -> bool:
    """공고 본문이 텍스트로 거의 안 잡히면 이미지 기반 공고로 추정.
    TODO(stage 2): True인 경우 로컬 LLM(Ollama)로 이미지 OCR + 키워드 추출 연결
    """
    return len(content.strip()) < MIN_CONTENT_LENGTH


def fetch_detail_content(page, href: str) -> str:
    page.goto(f"{BASE_URL}{href}")
    time.sleep(random.uniform(0.5, 1.5))
    page.wait_for_selector(".iframe_content", timeout=10000)

    iframe_src = page.query_selector(".iframe_content").get_attribute("src")
    page.goto(f"https://www.saramin.co.kr{iframe_src}")
    time.sleep(random.uniform(1, 2.3))

    return page.inner_text("body")


def save_detail(db, row: JobIndex, content: str, tech_stack: str, today: str, is_failed: bool):
    existing = db.query(JobDetail).filter(JobDetail.href == row.href).first()

    if existing:
        existing.content = content
        existing.tech_stack = tech_stack
        existing.is_failed = is_failed
    else:
        db.add(JobDetail(
            company=row.company,
            title=row.title,
            job_name=row.job_name,
            content=content,
            tech_stack=tech_stack,
            href=row.href,
            date=today,
            is_failed=is_failed,
        ))

    row.is_crawled = True
    row.is_failed = is_failed
    db.commit()


def crawl_row(page, db, row: JobIndex, today: str):
    try:
        content = fetch_detail_content(page, row.href)

        if is_image_posting(content):
            logger.warning("이미지 공고로 추정 (href=%s), tech_stack 추출 스킵", row.href)

        tech_stack = extract_keywords(content)
        save_detail(db, row, content, tech_stack, today, is_failed=False)

    except Exception as e:
        logger.error("크롤링 실패 (href=%s): %s: %s", row.href, type(e).__name__, e)
        db.rollback()
        try:
            save_detail(db, row, content="", tech_stack="", today=today, is_failed=True)
        except Exception as e2:
            logger.error("실패 기록도 실패 (href=%s): %s: %s", row.href, type(e2).__name__, e2)
            db.rollback()


def main():
    db = SessionLocal()
    today = datetime.now().strftime("%Y%m%d")

    rows = db.query(JobIndex).filter(
        (JobIndex.is_crawled == False) | (JobIndex.is_failed == True)
    ).all()
    logger.info("총 %d개 공고 크롤링 시작", len(rows))

    headless = os.getenv("HEADLESS", "true").lower() == "true"

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        for i, row in enumerate(rows):
            logger.info("[%d/%d] %s - %s", i + 1, len(rows), row.company, row.title)
            crawl_row(page, db, row, today)

        browser.close()

    db.close()


if __name__ == "__main__":
    main()
