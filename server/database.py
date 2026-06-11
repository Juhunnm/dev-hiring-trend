import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
print("[sqlalchemy] 데이터베이스에 연결되었습니다.")
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()#테이블 구조를 python 클래스로 만들떄 필요함

def get_db():
    db = SessionLocal()
    try :
        yield db
    finally:
        db.close()