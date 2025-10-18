# weAlist Kanban Service

칸반 보드 관리 시스템 (Workspace → Project → Ticket → Task)

> 이 프로젝트는 weAlist의 공통 인프라(PostgreSQL, Redis)를 사용합니다.

## 기술 스택

- Python 3.11
- FastAPI
- PostgreSQL (공통 인프라)
- Redis (공통 인프라)
- Docker & Docker Compose

## 실행 방법

### 1. 공통 인프라 설정 (최초 1회)

```bash
# infrastructure 디렉토리로 이동
cd infrastructure

# 환경변수 파일 생성
cp .env.example .env

# .env 파일에서 비밀번호 변경 (중요!)
# POSTGRES_PASSWORD와 REDIS_PASSWORD를 변경하세요

# 인프라 시작
docker-compose up -d
```

### 2. Kanban 서비스 실행

```bash
# services/kanban 디렉토리로 이동
cd services/kanban

# 환경변수 파일 생성
cp .env.example .env

# .env 파일에서 비밀번호를 infrastructure/.env와 동일하게 설정

# Kanban 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## API

- **Workspace**: 워크스페이스 관리
- **Project**: 프로젝트 관리 (상태, 우선순위)
- **Ticket**: 티켓 관리 (상태, 우선순위)
- **Task**: 작업 관리 (완료 처리 포함)

### API 문서
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 테스트

```bash
# 테스트 실행 (커버리지 포함)
docker-compose exec kanban pytest --cov

# 테스트만 실행
docker-compose exec kanban pytest -v
```

- 총 36개 테스트
- 커버리지 97%+

## 개발

```bash
# Kanban 서비스 컨테이너 중지
cd services/kanban
docker-compose down

# 재빌드
docker-compose up -d --build

# 인프라 중지 (주의: 다른 서비스도 영향받음!)
cd infrastructure
docker-compose down
```

## 다른 팀과 협업

이 프로젝트는 weAlist 공통 인프라를 사용합니다.
다른 팀(예: Member 팀)과 인프라를 공유하는 방법은 `infrastructure/SHARING.md`를 참고하세요.
