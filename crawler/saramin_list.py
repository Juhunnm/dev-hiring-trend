from datetime import datetime 
import math
from urllib.parse import parse_qs, urlparse
from playwright.sync_api import sync_playwright

from server.database import SessionLocal
from server.models import JobRaw


JOB_CODE = 87 #웹개발
JOB_NAME = '웹개발'

LIST_URL = f"https://www.saramin.co.kr/zf_user/jobs/list/job-category?cat_kewd={JOB_CODE}"

db = SessionLocal()
count = 0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    # 목록 페이지 접속
    page.goto(LIST_URL)

    # 공고 총 갯수
    total_tag = page.query_selector(".common_recruilt_list .total_count em")
    total_count = int((total_tag.inner_html().strip()).replace(",",""))

    # 기본 페이지 공고수 50
    per_page = 50
    total_pages = math.ceil(total_count/per_page)

    print(f"전체 공고: {total_count}건 / 총 {total_pages}페이지\n")

    # 전체 공고 담을 리스트
    all_jobs = []

    for page_num in  range(1,total_pages + 1) :
        print(f"{page_num}/{total_pages} 페이지 수집 중 ...")

        url = f"{LIST_URL}&page={page_num}"
        page.goto(url)
        page.wait_for_selector(".list_item")
        
        # 공고 목록 추출
        jobs = page.query_selector_all(".list_recruiting .list_item")
    
        for job in jobs:
            # 회사명
            company_tag = job.query_selector(".col.company_nm a.str_tit")
            if not company_tag:
                company_tag = job.query_selector(".col.company_nm span.str_tit")
            company = company_tag.inner_text().strip() if company_tag else "없음"

            # 공고 제목 
            title_tag = job.query_selector(".job_tit a")
            title = title_tag.inner_text().strip() if title_tag else "없음"

            # href 추출
            href = title_tag.get_attribute("href") if title_tag else "없음"

            
            try :
                #hrefe 에서 rec_idx 추출
                parsed = parse_qs(urlparse(href).query)
                rec_idx = parsed['rec_idx'][0]

                job_raw = JobRaw(
                rec_idx = rec_idx,
                company = company,
                title      = title,
                href       = href,
                job_name   =JOB_NAME,
                )
                db.add(job_raw)
                db.commit()
                count += 1
            except Exception as e:
                db.rollback()
            
    print(f"\n총 {count}개 공고 수집 완료!")
    browser.close()
db.close()
