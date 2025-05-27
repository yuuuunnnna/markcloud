# 마크클라우드 (MarkCloud)

상표 검색 API - 상표 검색 및 조회 서비스입니다.

## 주요 기능

- 키워드 기반 상표 검색 (한글/영문)
- 다양한 조건별 필터링 (등록상태, 출원일자, 상품분류코드)
- PostgreSQL pg_trgm 확장을 활용한 유사도 검색
- 페이지네이션 지원으로 대용량 데이터 효율적 조회
- Docker 기반 간편 배포 환경

## 기술 스택

- **Backend**: FastAPI, Python 3.9+
- **Database**: PostgreSQL
- **Search**: PostgreSQL pg_trgm (trigram) 확장
- **Deployment**: Docker

## 설치 및 실행

### Docker Compose 이용

```bash
# 서비스 구동
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build

# 서비스 중지
docker-compose down
```

### 로컬 개발 환경

```bash
# 필요한 패키지 설치
pip install -r requirements.txt

# PostgreSQL 설정 (필요시)
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=trademark_db

# pg_trgm 확장 활성화 (PostgreSQL에서 실행)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

# 서버 실행
uvicorn main:app --reload
```

## API 엔드포인트

### 상표 검색

```
POST /api/trademarks
```

**요청 파라미터**:
- `keyword`: 검색어 (상품명)
- `register_status`: 등록상태
- `application_date_from`: 출원일자 시작 (YYYYMMDD)
- `application_date_to`: 출원일자 종료 (YYYYMMDD)
- `main_code`: 상품분류 메인코드
- `page`: 페이지 번호 (기본값: 1)
- `page_size`: 페이지 크기 (기본값: 20)


## 구현 상세

### 데이터베이스 설계

상표 정보를 효율적으로 저장하기 위해 다음과 같은 스키마를 사용합니다:

- **Primary Key**: applicationNumber (출원번호)
- **검색 대상 필드**: productName, productNameEng, applicationDate, registerStatus
- **배열 타입**: registrationNumber, registrationDate, asignProductMainCodeList 등 다중 값을 가지는 필드

### 검색 최적화

1. **인덱스 활용**
   - GIN 인덱스: productName, productNameEng 

2. **유사도 검색**
   - PostgreSQL의 pg_trgm 확장을 활용하여 유사 문자열 검색 구현
   - 검색 키워드와 상표명 간의 유사도에 기반한 결과 제공

3. **쿼리 최적화**
   - 복합 조건에 대한 효율적인 필터링
   - 키워드 분할을 통한 AND 검색 지원

## 개발 과정 및 고려사항

### 1. 기술 선택 배경

- **FastAPI**: 비동기 처리 및 자동 문서화 기능으로 API 개발 생산성 향상
- **PostgreSQL**: 배열 타입 및 pg_trgm과 같은 고급 기능을 활용한 검색 성능 최적화
- **Docker**: 개발/운영 환경의 일관성 확보 및 배포 과정 간소화

### 2. 문제 해결 과정

트레이드마크 검색 시 다음과 같은 문제와 해결 방안을 고려했습니다:

- **유사 상표 검색 문제**: PostgreSQL의 pg_trgm 확장을 활용하여 문자열 유사도 검색 구현
- **초기화 프로세스 간소화**: Docker 환경에서 자동으로 pg_trgm 확장을 활성화하는 초기화 스크립트 적용
- **트랜잭션 관리**: 데이터베이스 오류 발생 시 안전한 롤백 및 대체 검색 로직으로 전환

### 3. 성능 최적화

- 인덱스 전략: 검색 패턴에 최적화된 인덱스 설계
- 커넥션 풀링: 데이터베이스 연결 재사용으로 성능 향상
- 쿼리 최적화: 효율적인 필터링 및 조건 처리

## 향후 개선 계획

1. **검색 기능 강화**
   - 한글 형태소 분석 적용
   - 검색 결과 랭킹 알고리즘 개선
   - Elastic search 적용

2. **API 확장**
   - 사용자 인증 및 권한 관리
   - 검색 기록 및 즐겨찾기 기능
   - 배치 처리 API

3. **인프라 개선**
   - 분산 캐싱
   - 로깅 및 모니터링 체계


## 파일 구조

```
markcloud/
├── main.py                # FastAPI 애플리케이션
├── database.py            # 데이터베이스 설정
├── models.py              # db 테이블 정의
├── load_data.py           # 데이터 로드 스크립트
├── init-db.sh             # 데이터베이스 초기화 스크립트
├── static/                # 정적 파일
├── docker-compose.yml     # Docker 설정
└── README.md              # 프로젝트 문서
```


