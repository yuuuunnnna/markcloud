from fastapi import FastAPI, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from database import get_db, engine
from models import Base, Trademark
from pydantic import BaseModel
from sqlalchemy import or_, func
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
# 모델 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="마크클라우드 api")

# 정적 파일과 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 검색 요청 모델
class TrademarkSearchRequest(BaseModel):
    keyword: Optional[str] = None
    register_status: Optional[str] = None
    application_date_from: Optional[str] = None
    application_date_to: Optional[str] = None
    main_code: Optional[str] = None
    page: int = 1
    page_size: int = 20

# 검색 응답 모델
class TrademarkResponse(BaseModel):
    applicationNumber: str
    productName: Optional[str]
    productNameEng: Optional[str]
    applicationDate: Optional[str]
    registerStatus: Optional[str]
    registrationNumber: Optional[List[Optional[str]]]
    registrationDate: Optional[List[Optional[str]]]
    asignProductMainCodeList: Optional[List[Optional[str]]]
    asignProductSubCodeList: Optional[List[Optional[str]]]

    class Config:
        from_attributes = True

# 페이징 응답 모델
class PaginatedResponse(BaseModel):
    items: List[TrademarkResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@app.get("/")
async def main():
    return FileResponse('static/index.html')

# POST 검색 API
@app.post("/api/trademarks/search", response_model=PaginatedResponse)
async def search_trademarks_post(
    search_request: TrademarkSearchRequest, 
    db: Session = Depends(get_db)
):
    query = db.query(Trademark)

    # 유사도 , keyword 유무 분기 처리
    if search_request.keyword:
        query = query.filter(
            text("""
                similarity("productName", :kw) > 0.1
                OR similarity("productNameEng", :kw) > 0.1
            """)
        ).order_by(
            text("""
                GREATEST(similarity("productName", :kw), similarity("productNameEng", :kw)) DESC
            """)
        ).params(kw=search_request.keyword)

    # 등록 상태 필터
    if search_request.register_status:
        query = query.filter(
            func.lower(Trademark.registerStatus).contains(func.lower(search_request.register_status))
        )

    # 출원일 범위 필터
    if search_request.application_date_from:
        try:
            datetime.strptime(search_request.application_date_from, '%Y%m%d')
            query = query.filter(Trademark.applicationDate >= search_request.application_date_from)
        except ValueError:
            raise HTTPException(status_code=400, detail="시작일자 형식이 올바르지 않습니다. YYYYMMDD 형식으로 입력해주세요.")

    if search_request.application_date_to:
        try:
            datetime.strptime(search_request.application_date_to, '%Y%m%d')
            query = query.filter(Trademark.applicationDate <= search_request.application_date_to)
        except ValueError:
            raise HTTPException(status_code=400, detail="종료일자 형식이 올바르지 않습니다. YYYYMMDD 형식으로 입력해주세요.")

    # 상품 분류 메인 코드 필터
    if search_request.main_code:
        query = query.filter(Trademark.asignProductMainCodeList.any(search_request.main_code))

    # 페이징
    total = query.count()
    skip = (search_request.page - 1) * search_request.page_size
    trademarks = query.offset(skip).limit(search_request.page_size).all()


    return {
        "items": trademarks,
        "total": total,
        "page": search_request.page,
        "page_size": search_request.page_size,
        "total_pages": (total + search_request.page_size - 1) // search_request.page_size
    }
