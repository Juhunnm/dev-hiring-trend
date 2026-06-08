from playwright.sync_api import sync_playwright

SECTION_KEYWORDS = {
    "tech": ["사용기술", "tech stack", "기술스택", "개발환경", "사용 기술"],
    "required": ["자격요건", "자격 요건", "requirements", "필수조건", "필수 조건", "이런 분을 찾아요"],
    "preferred": ["우대사항", "우대 사항", "nice to have", "우대조건", "이런 분이면 더 좋아요"],
}

def extract_sections(text):
    lines = text.split("\n")
    result = {"tech": [], "required": [], "preferred": []}
    current = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 섹션 제목인지 확인
        matched = False
        for section, keywords in SECTION_KEYWORDS.items():
            if any(kw.lower() in line.lower() for kw in keywords):
                current = section  # 섹션 제목 발견 → current 업데이트
                matched = True
                break

        # 섹션 제목이 아니고 + 현재 섹션이 있으면 → 내용 저장
        if not matched and current:
            result[current].append(line)

    return result


IFRAME_URL = "https://www.saramin.co.kr/zf_user/jobs/relay/view-detail?rec_idx=53863954&rec_seq=0&t_category=non-logged_relay_view&t_content=view_detail&t_ref=&t_ref_content="

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    page.goto(IFRAME_URL, timeout=60000)
    page.wait_for_load_state("networkidle")

    content = page.inner_text("body")

    # 섹션 추출
    sections = extract_sections(content)

    print("=== 사용기술 ===")
    print(sections["tech"])

    print("\n=== 자격요건 ===")
    print(sections["required"])

    print("\n=== 우대사항 ===")
    print(sections["preferred"])

    page.wait_for_timeout(5000)
    browser.close()

    # 문제점 마지막꺼 필터링할떄 마지막 요소까지 긁어봐버림