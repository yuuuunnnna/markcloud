# load_data.py
from database import SessionLocal, init_db
from models import Trademark
import pandas as pd
from fastapi import FastAPI, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 테이블 초기화 
init_db()

# json 로드
df = pd.read_json("trademark_sample.json")
df = df.fillna("")

# 세션설정
session = SessionLocal()

# ORM 객체 변환 후 삽입
for row in df.to_dict(orient="records"):
    try:
        obj = Trademark(**row)
        session.add(obj)
    except Exception as e:
        print(f"삽입 오류: {e} | 데이터: {row.get('applicationNumber')}")

# 커밋
session.commit()
session.close()
print("삽입 완료")

