import re

JOB_CATEGORIES = {
    "개발PM":           2247,
    "게임개발":           80,
    "기술지원":           81,
    "데이터분석가":        82,
    "데이터엔지니어":      83,
    "백엔드/서버개발":     84,
    "보안컨설팅":          85,
    "앱개발":             86,
    "웹개발":             87,
    "웹마스터":           88,
    "유지보수":           89,
    "정보보안":           90,
    "퍼블리셔":           91,
    "프론트엔드":          92,
    "CISO":              93,
    "CPO":               94,
    "DBA":               95,
    "FAE":               96,
    "GM(게임운영)":       97,
    "IT컨설팅":           98,
    "QA/테스터":          99,
    "SE(시스템엔지니어)": 100,
    "SI개발":            101,
    "ICT컨설팅":         102,
    "BI 엔지니어":       2246,
    "데이터 사이언티스트": 2248,
    "SQA":             2229,
    "보안관제":          2239,
}

# 기술 스택 키워드
TECH_KEYWORDS = [
    # 언어
    "Python", "Java", "Kotlin", "C#", "C++", "JavaScript", "TypeScript",
    "Go", "Golang", "Rust", "Swift", "Objective-C", "Ruby", "PHP", "Scala",
    "R", "MATLAB", "Dart", "Perl", "Groovy",
    # 백엔드 프레임워크
    "Spring", "Spring Boot", "Django", "FastAPI", "Flask", "Express",
    "Nest.js", "NestJS", "Node.js", "NodeJS", "Ruby on Rails", "Laravel",
    ".NET", "ASP.NET",
    # 프론트엔드
    "React", "Vue", "Vue.js", "Angular", "Next.js", "Nuxt", "Svelte",
    "jQuery", "Redux", "Flutter", "React Native",
    # 데이터베이스
    "MySQL", "PostgreSQL", "MariaDB", "Oracle", "MongoDB", "Redis",
    "Elasticsearch", "Cassandra", "DynamoDB", "MSSQL", "SQLite",
    # 인프라/클라우드
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "K8s", "Terraform",
    "Ansible", "Jenkins", "GitLab", "GitHub Actions", "ArgoCD",
    "Nginx", "Apache", "Kafka", "RabbitMQ", "Airflow",
    # 데이터/ML
    "Spark", "Hadoop", "TensorFlow", "PyTorch", "Pandas", "NumPy",
    "Scikit-learn", "Tableau", "PowerBI", "Kibana", "Grafana",
    "Snowflake", "dbt", "Looker",
    # 보안
    "Splunk", "SIEM", "Wireshark", "Nessus", "Burp Suite", "Metasploit",
    # 기타
    "Git", "GraphQL", "REST", "gRPC", "Linux", "Jira", "Figma", "Confluence",
]

#크롤링 베이스 url
BASE_URL = "https://www.saramin.co.kr"


PER_PAGE = 50

def extract_keywords(text):
    """본문 텍스트에서 기술 키워드를 추출 (단어 경계 기반 정확 매칭)"""
    found = []
    for keyword in TECH_KEYWORDS:
        # 앞뒤에 영숫자가 없을 때만 매칭 (Go가 Google에 안 걸림)
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(keyword) + r'(?![a-zA-Z0-9])'
        if re.search(pattern, text, re.IGNORECASE):
            found.append(keyword)
    return ", ".join(found)
