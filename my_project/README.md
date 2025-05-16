# 마크클라우드 API (Trademark Search API)

상표 검색 및 조회를 위한 FastAPI 기반 API 서비스입니다.

## 실행 방법

### Docker Compose 이용 

```bash
# 서비스 구동
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

### 로컬 실행

```bash
# 필요한 패키지 설치
pip install -r requirements.txt

# PostgreSQL 서버가 로컬에서 실행 중이어야 합니다
# 환경 변수 설정 (필요시)
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=trademark_db

# 서버 실행
uvicorn main:app --reload
```

## API 사용법

### 1. 상표 검색 API

#### POST /api/trademarks/search

```json
{
  "keyword": "애플",
  "register_status": "등록",
  "application_date_from": "20200101",
  "application_date_to": "20221231",
  "main_code": "09",
  "page": 1,
  "page_size": 20
}
```

#### GET /api/trademarks?keyword=애플&register_status=등록

쿼리 파라미터:
- `keyword`: 검색어 (상품명 한글/영문)
- `register_status`: 등록상태 (등록, 출원, 소멸 등)
- `application_date_from`: 출원일자 시작 (YYYYMMDD)
- `application_date_to`: 출원일자 종료 (YYYYMMDD)
- `main_code`: 상품분류 메인코드
- `page`: 페이지 번호 (기본값: 1)
- `page_size`: 페이지 크기 (기본값: 20)

### 2. 상표 상세 조회 API

#### GET /api/trademarks/{application_number}

응답 예시:
```json
{
  "applicationNumber": "4020200012345",
  "productName": "애플",
  "productNameEng": "APPLE",
  "applicationDate": "20200101",
  "registerStatus": "등록",
  "registrationNumber": ["40-1234567"],
  "registrationDate": ["20200701"],
  "asignProductMainCodeList": ["09", "42"],
  "asignProductSubCodeList": ["G390802", "G390803"]
}
```

## 구현된 기능

1. **상표 검색**: 키워드, 등록상태, 출원일자, 상품분류코드 등 복합 조건 검색
2. **페이지네이션**: 대용량 결과를 효율적으로 제공하기 위한 페이지 단위 조회
3. **데이터 초기화**: 샘플 JSON 데이터를 PostgreSQL에 로드하는 기능
4. **Docker 지원**: Docker Compose를 통한 원활한 배포 및 실행 환경 제공

## 기술적 의사결정

### 기술 스택 선택

- **FastAPI**: 비동기 처리, 자동 문서화, 타입 힌팅 등 현대적인 웹 API 개발을 위해 선택
- **SQLAlchemy**: ORM을 통한 데이터베이스 작업 추상화 및 코드 가독성 향상
- **PostgreSQL**: 배열 타입, 전문 검색 등 상표 데이터 처리에 적합한 기능 제공
- **Docker**: 개발/운영 환경의 일관성 확보 및 배포 프로세스 간소화

### 데이터 모델링

상표 데이터의 특성을 고려하여 다음과 같은 구조로 설계했습니다:

1. **Primary Key**: `applicationNumber`(출원번호)를 기본키로 사용
2. **배열 타입**: 여러 값을 가질 수 있는 필드(등록번호, 상품코드 등)에 PostgreSQL의 배열 타입 활용
3. **검색 최적화**: 자주 검색되는 필드에 인덱스 적용

### 검색 기능 구현

1. **키워드 분할**: 공백으로 구분된 여러 키워드를 AND 조건으로 검색
2. **대소문자 무시**: `func.lower()` 함수를 사용하여 대소문자 구분 없이 검색
3. **부분 일치**: `contains` 함수를 사용한 부분 일치 검색 지원

## 개발 과정에서 고민했던 점

### 1. 데이터 로딩 전략

초기에는 Alembic을 사용한 마이그레이션을 고려했으나, 단순한 데이터 로딩 요구사항에 따라 직접 초기화 스크립트 방식을 채택했습니다. 이로써 설정의 복잡성을 줄이고 배포 과정을 단순화했습니다.

### 2. 검색 성능 최적화

상표 검색은 사용자의 입력에 따라 다양한 조건이 조합될 수 있어 성능 이슈가 발생할 수 있습니다. 이를 위해:

- 인덱스 적용: 자주 검색되는 필드에 적절한 인덱스 생성
- 쿼리 최적화: 불필요한 조인이나 중복된 조건 제거

### 3. 확장성 고려

향후 데이터 증가와 기능 확장을 고려하여:

- 모듈화된 코드 구조
- 명확한 API 계약
- Docker 기반 환경으로 스케일링 용이성 확보

## 개선하고 싶은 부분

1. **전문 검색 기능 강화**: 한글 형태소 분석을 통한 검색 정확도 향상
2. **캐싱 레이어 도입**: 자주 요청되는 쿼리 결과 캐싱을 통한 성능 개선
3. **사용자 인증/인가**: API 접근 제어 및 사용량 제한 기능 추가
4. **로깅 및 모니터링**: 요청/응답 로깅 및 성능 지표 수집 체계 구축
5. **테스트 자동화**: 단위/통합 테스트 확대를 통한 품질 향상



