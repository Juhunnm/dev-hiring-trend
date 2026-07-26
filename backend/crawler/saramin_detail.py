import random
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from config import BASE_URL, TECH_KEYWORDS
from app.database import SessionLocal
from app.models import JobDetail, JobIndex
from playwright_stealth import Stealth


db = SessionLocal()

def extract_keywords(text):
    found = []
    for keyword in TECH_KEYWORDS:
        if keyword.lower() in text.lower():
            found.append(keyword)
    return ", ".join(found)


today = datetime.now().strftime("%Y%m%d")

rows = db.query(JobIndex).filter(
    (JobIndex.is_crawled == False) | (JobIndex.is_failed == True)
).all()
print(f"총 {len(rows)}개 공고 크롤링 시작\n")


with Stealth().use_sync(sync_playwright()) as p:
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    browser = p.chromium.launch(headless=headless)

    page = browser.new_page()

    for i, row in enumerate(rows):
        print(f"[{i+1}/{len(rows)}] {row.company} - {row.title}")

        try:
            detail_url = f"{BASE_URL}{row.href}"
            page.goto(detail_url)
            time.sleep(random.uniform(0.5, 1.5))
            page.wait_for_selector(".iframe_content", timeout=10000)

            iframe_tag = page.query_selector(".iframe_content")
            iframe_src = iframe_tag.get_attribute('src')
            iframe_url = f"https://www.saramin.co.kr{iframe_src}"

            page.goto(iframe_url)
            time.sleep(random.uniform(1, 2.3))
            content = page.inner_text('body')
            tech_stack = extract_keywords(content)

            existing = db.query(JobDetail).filter(JobDetail.href == row.href).first()

            if existing:
                existing.content = content
                existing.tech_stack = tech_stack
                existing.is_failed = False
            else:
                job_detail = JobDetail(
                    company=row.company,
                    title=row.title,
                    job_name=row.job_name,
                    content=content,
                    tech_stack=tech_stack,
                    href=row.href,
                    date=today,
                    is_failed=False,
                )
                db.add(job_detail)
            row.is_crawled = True
            db.commit()

        except Exception as e:
            print(f"  -> 크롤링 실패: {type(e).__name__}: {e}")
            db.rollback()

            try:
                existing = db.query(JobDetail).filter(JobDetail.href == row.href).first()
                if not existing:
                    db.add(JobDetail(
                        company=row.company,
                        title=row.title,
                        job_name=row.job_name,
                        content="",
                        tech_stack="",
                        href=row.href,
                        date=today,
                        is_failed=True,
                    ))
                else:
                    existing.is_failed = True
                row.is_crawled = True
                row.is_failed = True
                db.commit()
                print(f"    저장 확인: is_crawled={row.is_crawled}")   
            except Exception as e2:
                print(f"  -> 실패 기록도 실패: {type(e2).__name__}: {e2}")
                db.rollback()

    browser.close()
db.close()