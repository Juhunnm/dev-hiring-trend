from datetime import datetime
from playwright.sync_api import sync_playwright


from config import BASE_URL, TECH_KEYWORDS
from app.database import SessionLocal
from app.models import JobDetail, JobIndex

# 본문이랑, 키워드 목록 각각 저장

db = SessionLocal()



def extract_keywords(text) :
    found =[]
    for keyword in TECH_KEYWORDS:
        if keyword.lower() in text.lower():
            found.append(keyword)
    return ", ".join(found)

    
today = datetime.now().strftime("%Y%m%d")


rows = db.query(JobIndex).filter(JobIndex.is_crawled == False).all()
print(f"총 {len(rows)}개 공고 크롤링 시작\n")


with sync_playwright() as p :
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    for i, row in enumerate(rows[:100]):
        print(f"[{i+1}/{len(rows)}] {row.company} - {row.title}")

        try :
            detail_url = f"{BASE_URL}{row.href}"
            page.goto(detail_url)

            page.wait_for_selector(".iframe_content", timeout=1000)

            iframe_tag = page.query_selector(".iframe_content")
            iframe_src = iframe_tag.get_attribute('src')
            iframe_url = f"https://www.saramin.co.kr{iframe_src}"

            page.goto(iframe_url)
                
            content = page.inner_text('body')
            tech_stack = extract_keywords(content)

            job_detail = JobDetail(
                company=row.company,
                title=row.title,
                job_name=row.job_name,
                content=content,
                tech_stack=tech_stack,
                href=row.href,
                date=today
            )
            db.add(job_detail)
            row.is_crawled = True
            db.commit()
            
        except Exception as e:
            print(f"-> 오류 :{e}")
            db.rollback()
            job = JobDetail(
                company=row.company,
                title=row.title,
                job_name=row.job_name,
                content="",
                tech_stack="",
                href=row.href,
                date=today
            )
            db.add(job)
            db.commit()
    browser.close() 
db.close()