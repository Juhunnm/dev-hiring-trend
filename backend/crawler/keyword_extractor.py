import json
import re
from pathlib import Path

_TECH_KEYWORDS_DATA_PATH = Path(__file__).resolve().parent / "data" / "tech_keywords.json"

with open(_TECH_KEYWORDS_DATA_PATH, encoding="utf-8") as f:
    TECH_KEYWORDS = list(json.load(f).keys())


def extract_keywords(text: str) -> str:
    """본문 텍스트에서 기술 키워드를 추출 (단어 경계 기반 정확 매칭)"""
    found = []
    for keyword in TECH_KEYWORDS:
        # 앞뒤에 영숫자/&가 없을 때만 매칭
        # (Go가 Google에, R이 R&D에 안 걸리게. &을 경계에서 제외한 이유: "R&D"의 R이 오탐되던 문제)
        pattern = r"(?<![a-zA-Z0-9&])" + re.escape(keyword) + r"(?![a-zA-Z0-9&])"
        if re.search(pattern, text, re.IGNORECASE):
            found.append(keyword)
    return ", ".join(found)
