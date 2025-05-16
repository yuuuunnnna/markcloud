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
    registrationNumber: Optional[List[str]]
    registrationDate: Optional[List[str]]
    asignProductMainCodeList: Optional[List[str]]
    asignProductSubCodeList: Optional[List[str]]

    class Config:
        from_attributes = True

# 페이징 응답 모델
class PaginatedResponse(BaseModel):
    items: List[TrademarkResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# 메인 화면
@app.get("/")
async def main():
    return FileResponse('static/index.html')


# POST 검색 API
@app.post("/api/trademarks/search", response_model=PaginatedResponse)
async def search_trademarks_post(search_request: TrademarkSearchRequest, db: Session = Depends(get_db)):
    query = db.query(Trademark)

    # 키워드 검색
    if search_request.keyword:
        keywords = search_request.keyword.strip().split()
        keyword_conditions = []
        for keyword in keywords:
            keyword_condition = or_(
                func.lower(Trademark.productName).contains(func.lower(keyword)),
                func.lower(Trademark.productNameEng).contains(func.lower(keyword))
            )
            keyword_conditions.append(keyword_condition)
        query = query.filter(*keyword_conditions)

    # 등록 상태 필터
    if search_request.register_status:
        query = query.filter(
            func.lower(Trademark.registerStatus).contains(func.lower(search_request.register_status))
        )

    # 출원일자 범위 필터
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

    # 메인코드 필터
    if search_request.main_code:
        query = query.filter(Trademark.asignProductMainCodeList.any(search_request.main_code))

    # 전체 결과 수 계산
    total = query.count()

    # 페이지네이션 적용
    skip = (search_request.page - 1) * search_request.page_size
    trademarks = query.offset(skip).limit(search_request.page_size).all()

    return {
        "items": trademarks,
        "total": total,
        "page": search_request.page,
        "page_size": search_request.page_size,
        "total_pages": (total + search_request.page_size - 1) // search_request.page_size
    }


# GET 검색 API
@app.get("/api/trademarks", response_model=PaginatedResponse)
async def search_trademarks(
    keyword: Optional[str] = Query(None),
    register_status: Optional[str] = Query(None),
    application_date_from: Optional[str] = Query(None),
    application_date_to: Optional[str] = Query(None),
    main_code: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Trademark)

    if keyword:
        query = query.filter(
            or_(
                Trademark.productName.ilike(f"%{keyword}%"),
                Trademark.productNameEng.ilike(f"%{keyword}%")
            )
        )

    if register_status:
        query = query.filter(Trademark.registerStatus == register_status)

    if application_date_from:
        query = query.filter(Trademark.applicationDate >= application_date_from)

    if application_date_to:
        query = query.filter(Trademark.applicationDate <= application_date_to)

    if main_code:
        query = query.filter(Trademark.asignProductMainCodeList.any(main_code))

    total = query.count()
    skip = (page - 1) * page_size
    trademarks = query.offset(skip).limit(page_size).all()

    return {
        "items": trademarks,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


# 단건 조회 API
@app.get("/api/trademarks/{application_number}", response_model=TrademarkResponse)
async def get_trademark(application_number: str, db: Session = Depends(get_db)):
    trademark = db.query(Trademark).filter(Trademark.applicationNumber == application_number).first()
    if not trademark:
        raise HTTPException(status_code=404, detail="Trademark not found")
    return trademark
