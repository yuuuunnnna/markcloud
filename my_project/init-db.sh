#!/bin/bash
set -e

echo "데이터베이스 초기화 스크립트 시작..."

# PostgreSQL 클라이언트가 설치되어 있는지 확인
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL 클라이언트가 설치되어 있지 않습니다."
    exit 1
fi

# 환경 변수 사용
DB_USER=${POSTGRES_USER:-postgres}
DB_PASS=${POSTGRES_PASSWORD:-password}
DB_HOST=${POSTGRES_HOST:-db}
DB_PORT=${POSTGRES_PORT:-5432}
DB_NAME=${POSTGRES_DB:-trademark_db}

# pg_trgm 확장 활성화
echo "pg_trgm 확장 활성화..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;" || true

# 테이블이 있는지 확인
TABLE_EXISTS=$(PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -t -c "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='trademarks');")
TABLE_EXISTS=$(echo $TABLE_EXISTS | xargs)

if [ "$TABLE_EXISTS" = "t" ]; then
    echo "상표 테이블이 이미 존재합니다. GIN 인덱스 생성..."
    
    # 인덱스 생성
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE INDEX IF NOT EXISTS idx_trademark_name_gin ON trademarks USING GIN (\"productName\" gin_trgm_ops);" || true
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE INDEX IF NOT EXISTS idx_trademark_name_eng_gin ON trademarks USING GIN (\"productNameEng\" gin_trgm_ops);" || true
    
    echo "인덱스 생성 완료"
    
    # 데이터가 있는지 확인
    DATA_COUNT=$(PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM trademarks;")
    DATA_COUNT=$(echo $DATA_COUNT | xargs)
    
    if [ "$DATA_COUNT" -gt "0" ]; then
        echo "상표 데이터가 이미 존재합니다. 데이터 로드를 건너뜁니다."
    else
        echo "테이블은 있지만 데이터가 없습니다. 데이터를 로드합니다..."
        python load_data.py
    fi
else
    echo "상표 테이블이 없습니다. 테이블과 데이터를 초기화합니다..."
    python load_data.py
    
    # 테이블 생성 후 인덱스 생성
    echo "GIN 인덱스 생성..."
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE INDEX IF NOT EXISTS idx_trademark_name_gin ON trademarks USING GIN (\"productName\" gin_trgm_ops);" || true
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE INDEX IF NOT EXISTS idx_trademark_name_eng_gin ON trademarks USING GIN (\"productNameEng\" gin_trgm_ops);" || true
    
    echo "인덱스 생성 완료"
fi

echo "데이터베이스 초기화 완료!" 