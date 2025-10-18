# Kanban Service

칸반 보드 관리 시스템 (Workspace → Project → Ticket → Task)

## 기술 스택

- Python 3.11
- FastAPI
- PostgreSQL
- Redis
- Docker & Docker Compose

## 실행 방법

```bash
# Docker Compose로 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f kanban
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
# 컨테이너 중지
docker-compose down

# 재빌드
docker-compose up -d --build
```
