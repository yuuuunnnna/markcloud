from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
# from dotenv import load_dotenv

# load_dotenv()

def get_database_url():
    user = os.getenv("POSTGRES_USER", "yuna")
    password = os.getenv("POSTGRES_PASSWORD", "password")
    host = os.getenv("POSTGRES_HOST", "db")  # Docker 서비스 이름 사용
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "trademark_db")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# 엔진 생성
engine = create_engine(
    get_database_url(),
    pool_size=5,  # 커넥션 풀 크기
    max_overflow=10,  # 추가로 생성할 수 있는 커넥션 수
    pool_timeout=30,  # 커넥션 타임아웃 (초)
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # 모든 테이블 생성
    Base.metadata.create_all(bind=engine)