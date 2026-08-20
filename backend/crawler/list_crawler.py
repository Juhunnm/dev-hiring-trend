import logging
import math
import os
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from config import BASE_URL, JOB_CATEGORIES, PER_PAGE
from app.database import SessionLocal
from app.models import JobCategory, JobPosting, JobPostingCategory, PostingStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SOURCE = "saramin"


def get_or_create_category(db, cache: dict[str, JobCategory], name: str) -> JobCategory:
    if name in cache:
        return cache[name]

    category = db.query(JobCategory).filter(JobCategory.name == name).first()
    if not category:
        category = JobCategory(name=name)
        db.add(category)
        db.flush()

    cache[name] = category
    return category


def upsert_posting_row(db, postings: dict[str, JobPosting], row: dict) -> JobPosting | None:
    rec_idx = row["rec_idx"]
    posting = postings.get(rec_idx)

    if posting is None:
        posting = JobPosting(
            source=SOURCE,
            source_id=rec_idx,
            company=row["company"],
            title=row["title"],
            url=row["href"],
            status=PostingStatus.PENDING,
        )
        db.add(posting)
        db.flush()
        postings[rec_idx] = posting

    return posting


def collect_job_ids(
    page,
    job_name: str,
    job_code: int,
    postings: dict[str, JobPosting],
    category_cache: dict[str, JobCategory],
    linked_categories: set[tuple[int, int]],
) -> int:
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
    new_links = 0

    try:
        category = get_or_create_category(db, category_cache, job_name)

        for page_num in range(1, total_pages + 1):
            logger.info("[%s] %d/%d 페이지 수집 중", job_name, page_num, total_pages)

            page.goto(f"{list_url}&page={page_num}")
            page.wait_for_selector(".list_item")

            for job in page.query_selector_all(".list_recruiting .list_item"):
                row = parse_job_row(job)
                if row is None:
                    continue

                try:
                    posting = upsert_posting_row(db, postings, row)

                    link_key = (posting.id, category.id)
                    if link_key not in linked_categories:
                        db.add(JobPostingCategory(job_posting_id=posting.id, category_id=category.id))
                        linked_categories.add(link_key)
                        new_links += 1

                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.error("저장 실패 (rec_idx=%s): %s", row["rec_idx"], e)
    finally:
        db.close()

    logger.info("[%s] 총 %d개 카테고리 연결 추가", job_name, new_links)
    return new_links


def parse_job_row(job) -> dict | None:
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

    return {"rec_idx": rec_idx, "company": company, "title": title, "href": href}


def main():
    db = SessionLocal()
    postings = {p.source_id: p for p in db.query(JobPosting).filter(JobPosting.source == SOURCE).all()}
    linked_categories = set(
        (jpc.job_posting_id, jpc.category_id) for jpc in db.query(JobPostingCategory).all()
    )
    category_cache: dict[str, JobCategory] = {}
    db.close()
    logger.info("기존 posting %d건 로드됨", len(postings))

    headless = os.getenv("HEADLESS", "true").lower() == "true"
    total_links = 0

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        for job_name, job_code in JOB_CATEGORIES.items():
            logger.info("[%s] 크롤링 시작", job_name)
            total_links += collect_job_ids(page, job_name, job_code, postings, category_cache, linked_categories)

        browser.close()

    logger.info("전체 %d건 카테고리 연결 추가 완료! (posting %d건 보유)", total_links, len(postings))


if __name__ == "__main__":
    main()
