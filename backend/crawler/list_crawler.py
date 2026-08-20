import logging
import math
import os
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from config import BASE_URL, JOB_CATEGORIES, PER_PAGE
from app.database import SessionLocal
from app.models import JobIndex

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def collect_job_ids(page, job_name: str, job_code: int, existing_ids: set[str]) -> int:
    list_url = f"{BASE_URL}/zf_user/jobs/list/job-category?cat_kewd={job_code}"
    page.goto(list_url)

    total_tag = page.query_selector(".common_recruilt_list .total_count em")
    if not total_tag:
        logger.info("[%s] 공고 없음 스킵", job_name)
        return 0

    job_count = int(total_tag.inner_html().strip().replace(",", ""))
    total_pages = math.ceil(job_count / PER_PAGE)
    logger.info("[%s] 전체 공고 %d건 / 총 %d페이지", job_name, job_count, total_pages)

    db = SessionLocal()
    count = 0

    try:
        for page_num in range(1, total_pages + 1):
            logger.info("[%s] %d/%d 페이지 수집 중", job_name, page_num, total_pages)

            page.goto(f"{list_url}&page={page_num}")
            page.wait_for_selector(".list_item")

            for job in page.query_selector_all(".list_recruiting .list_item"):
                job_index = parse_job_row(job, job_name)
                if job_index is None or job_index.rec_idx in existing_ids:
                    continue

                try:
                    db.add(job_index)
                    db.commit()
                    existing_ids.add(job_index.rec_idx)
                    count += 1
                except Exception as e:
                    db.rollback()
                    logger.error("저장 실패 (rec_idx=%s): %s", job_index.rec_idx, e)
    finally:
        db.close()

    logger.info("[%s] 총 %d개 저장 완료", job_name, count)
    return count


def parse_job_row(job, job_name: str) -> JobIndex | None:
    company_tag = job.query_selector(".col.company_nm a.str_tit") or job.query_selector(
        ".col.company_nm span.str_tit"
    )
    company = company_tag.inner_text().strip() if company_tag else "없음"

    title_tag = job.query_selector(".job_tit a")
    title = title_tag.inner_text().strip() if title_tag else "없음"
    href = title_tag.get_attribute("href") if title_tag else None

    try:
        rec_idx = parse_qs(urlparse(href).query)["rec_idx"][0]
    except (KeyError, IndexError, TypeError):
        logger.warning("rec_idx 추출 실패, 건너뜀: %s", href)
        return None

    return JobIndex(rec_idx=rec_idx, company=company, title=title, href=href, job_name=job_name)


def main():
    db = SessionLocal()
    existing_ids = set(r[0] for r in db.query(JobIndex.rec_idx).all())
    db.close()
    logger.info("기존 공고 %d개 로드됨", len(existing_ids))

    headless = os.getenv("HEADLESS", "true").lower() == "true"
    total_count = 0

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        for job_name, job_code in JOB_CATEGORIES.items():
            logger.info("[%s] 크롤링 시작", job_name)
            total_count += collect_job_ids(page, job_name, job_code, existing_ids)

        browser.close()

    logger.info("전체 %d개 공고 수집 완료!", total_count)


if __name__ == "__main__":
    main()
