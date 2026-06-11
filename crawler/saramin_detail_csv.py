import csv
from datetime import datetime 
from playwright.sync_api import sync_playwright

# 본문이랑, 키워드 목록 각각 저장
BASE_URL = 'https://www.saramin.co.kr'

TECH_KEYWORDS = [
    "Python", "Java", "C#", "C++", "JavaScript", "TypeScript",
    "Spring", "React", "Vue", "Next.js", "Django", "FastAPI",
    "MySQL", "PostgreSQL", "MongoDB", "Redis",
    "AWS", "Docker", "Kubernetes", "Git"
]

def extract_keywords(text) :
    found =[]
    for keyword in TECH_KEYWORDS:
        if keyword.lower() in text.lower():
            found.append(keyword)
    return ", ".join(found)

    
today = datetime.now().strftime("%Y%m%d")
output_file = f"data/jobs_detail_웹개발_{today}.csv"

with sync_playwright() as p :
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    all_jobs = []

    with open("data/jobs_웹개발_20260608.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"총 {len(rows)}개 공고 크롤링 시작\n")

    for i, row in enumerate(rows[:20]):
        print(f"[{i+1}/{len(rows)}] {row['company']} - {row['title']}")

        try :
            detail_url = f"{BASE_URL}{row['href']}"
            page.goto(detail_url)

            page.wait_for_selector(".iframe_content", timeout=1000)

            iframe_tag = page.query_selector(".iframe_content")
            iframe_src = iframe_tag.get_attribute('src')
            iframe_url = f"https://www.saramin.co.kr{iframe_src}"

            page.goto(iframe_url)
                
            content = page.inner_text('body')

            tech_stack = extract_keywords(content)

            all_jobs.append({
                "company" : row["company"],
                "title" : row["title"],
                "content" : content,
                "tech_stack" : tech_stack,
                "date" : today
            })
        except Exception as e:
            print(f"-> 오류 :{e}")

            all_jobs.append({
                "company": row["company"],
                "title": row["title"],
                "content": "",
                "tech_stack": "",
                "date": today
            })
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f :
        writer = csv.DictWriter(f, fieldnames=["company", "title", "content", "tech_stack", "date"])
        writer.writeheader()
        writer.writerows(all_jobs)

    print(f"\n[v]{output_file} 저장 완료!")
    browser.close()