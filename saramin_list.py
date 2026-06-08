from itertools import count
import math

from playwright.sync_api import sync_playwright


JOB_CODE = 87 #웹개발
JOB_NAME = '웹개발'

LIST_URL = f"https://www.saramin.co.kr/zf_user/jobs/list/job-category?cat_kewd={JOB_CODE}"
# https://www.saramin.co.kr/zf_user/jobs/list/job-category?cat_kewd=87
with sync_playwright() as p:
    # true로 했을때 오류 발생(봇 예상)
    browser = p.chromium.launch(headless=False)
    
    # context = browser.new_context(
    #     user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    # )
    # page = context.new_page()
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

            # href에서 rec_idx 추출
            href = title_tag.get_attribute("href") if title_tag else "없음"

            all_jobs.append({
                "commpany" : company,
                "title" : title,
                "href" : href
            })
    print(f"\n총 {len(all_jobs)}개 공고 수집 완료!")
    browser.close()
