import math
from urllib.parse import parse_qs, urlparse
from playwright.sync_api import sync_playwright

from config import BASE_URL, JOB_CATEGORIES, PER_PAGE
from app.database import SessionLocal
from app.models import JobIndex

db = SessionLocal()
total_count = 0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    for job_name,job_code in JOB_CATEGORIES.items():
        print(f"\n[{job_name}] 크롤링 시작...")

        list_url = f"{BASE_URL}/zf_user/jobs/list/job-category?cat_kewd={job_code}"
        # 목록 페이지 접속
        page.goto(list_url)


        # 공고 총 갯수
        total_tag = page.query_selector(".common_recruilt_list .total_count em")
        if not total_tag:
            print(f"[{job_name}] 공고 없음 스킵")
            continue
        job_count = int((total_tag.inner_html().strip()).replace(",",""))
        total_pages = math.ceil(job_count/PER_PAGE)

        print(f"{job_name} 전체 공고: {job_count}건 / 총 {total_pages}페이지\n")

        count = 0

        for page_num in  range(1,total_pages + 1) :
            print(f"[{job_name}] {page_num}/{total_pages} 페이지 수집 중 ...")

            url = f"{list_url}&page={page_num}"
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

                    job_index = JobIndex(
                        rec_idx = rec_idx,
                        company = company,
                        title      = title,
                        href       = href,
                        job_name   = job_name,
                    )
                    db.add(job_index)
                    db.commit()
                    count += 1
                except Exception as e:
                    db.rollback()
        print(f"[{job_name}] 총 {count} 개 저장 완료")
        total_count += count
            
    print(f"\n전체 {total_count}개 공고 수집 완료!")
    browser.close()
db.close()
