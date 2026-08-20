import re

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


def extract_keywords(text: str) -> str:
    """본문 텍스트에서 기술 키워드를 추출 (단어 경계 기반 정확 매칭)"""
    found = []
    for keyword in TECH_KEYWORDS:
        # 앞뒤에 영숫자가 없을 때만 매칭 (Go가 Google에 안 걸림)
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(keyword) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text, re.IGNORECASE):
            found.append(keyword)
    return ", ".join(found)
