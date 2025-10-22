# 📋 weAlist Kanban Service

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![Coverage](https://img.shields.io/badge/Coverage-97%25-brightgreen)](pytest.ini)

칸반 보드 관리 시스템 (Workspace → Project → Ticket → Task)

> **🚀 Cloud Native Ready**: Kubernetes 배포를 위한 베이스 애플리케이션

---

## 🎯 프로젝트 개요

이 프로젝트는 향후 Kubernetes 환경으로 마이그레이션하기 위한 베이스 애플리케이션입니다.
현재는 Docker Compose로 실행하며, K8s 배포에 필요한 기능들이 이미 구현되어 있습니다.

### 주요 기능

```
Workspace (워크스페이스)
  └── Project (프로젝트)
       └── Ticket (티켓)
            └── Task (작업)
```

- ✅ **Workspace**: 팀/조직 단위 관리
- ✅ **Project**: 프로젝트별 상태/우선순위 관리
- ✅ **Ticket**: 이슈/기능 단위 추적
- ✅ **Task**: 세부 작업 관리 및 완료 처리

---

## 🛠️ 기술 스택

### Backend
- **Python 3.11** - 최신 타입 힌트 지원
- **FastAPI** - 고성능 비동기 웹 프레임워크
- **SQLAlchemy 2.0** - Modern ORM with async support
- **Alembic** - 데이터베이스 마이그레이션
- **Pydantic v2** - 데이터 검증 및 직렬화

### Infrastructure
- **PostgreSQL 16** - 관계형 데이터베이스
- **Redis 7** - 캐싱 및 세션 (공통 인프라)
- **Docker & Docker Compose** - 컨테이너 오케스트레이션

### Cloud Native Features
- ✅ Health Check Endpoints (Liveness/Readiness Probes)
- ✅ Structured Logging (JSON)
- ✅ Graceful Shutdown
- ✅ Database Migration (Alembic)
- ✅ 12-Factor App Compliance
- ✅ Stateless Design (샤딩 대비)

---

## 🚀 빠른 시작

### 사전 요구사항
- Docker & Docker Compose
- Git

### 1. 공통 인프라 설정 (최초 1회)

```bash
# 저장소 클론
git clone <repository-url>
cd wealist

# 인프라 디렉토리로 이동
cd infrastructure

# 환경변수 파일 생성
cp .env.example .env

# .env 파일 수정 (중요!)
# POSTGRES_PASSWORD와 REDIS_PASSWORD를 변경하세요
nano .env

# 인프라 시작 (PostgreSQL, Redis)
docker-compose up -d

# 상태 확인
docker-compose ps
```

### 2. Kanban 서비스 실행

```bash
# Kanban 서비스 디렉토리로 이동
cd services/kanban

# 환경변수 파일 생성
cp .env.example .env

# .env 파일 수정
# infrastructure/.env와 동일한 비밀번호로 설정
nano .env

# 서비스 시작(앞에 infra 의 docker가 띄운거 확인하고 실행)
docker-compose up -d

# 로그 확인
docker-compose logs -f kanban
```

### 3. 접속 확인

```bash
# Health Check
curl http://localhost:8000/health

# API 문서
open http://localhost:8000/docs
```

---

## 📡 API 엔드포인트

### 문서
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 헬스체크
- **Health Check**: `GET /health`
- **Liveness Probe**: `GET /health/live` (K8s용)
- **Readiness Probe**: `GET /health/ready` (K8s용)

### 주요 API
| 엔드포인트 | 설명 | 인증 |
|-----------|------|------|
| `GET /workspaces` | 워크스페이스 목록 | Required |
| `POST /workspaces` | 워크스페이스 생성 | Required |
| `GET /projects` | 프로젝트 목록 | Required |
| `GET /tickets` | 티켓 목록 | Required |
| `GET /tasks` | 작업 목록 | Required |

자세한 API 명세는 Swagger UI 참고

---

## 🧪 테스트

### 전체 테스트 실행
```bash
# 커버리지 포함
docker-compose exec kanban pytest --cov

# 상세 출력
docker-compose exec kanban pytest -v

# 특정 파일만
docker-compose exec kanban pytest tests/test_api/test_workspaces.py
```

### 테스트 통계
- **총 36개 테스트**
- **커버리지 97%+**
- **평균 실행 시간: ~3초**

---

## 📁 프로젝트 구조

```
services/kanban/
├── app/
│   ├── api/              # API 라우터
│   │   ├── workspaces.py
│   │   ├── projects.py
│   │   ├── tickets.py
│   │   └── tasks.py
│   ├── models/           # SQLAlchemy 모델
│   ├── schemas/          # Pydantic 스키마
│   ├── repositories/     # 데이터 접근 계층
│   ├── services/         # 비즈니스 로직
│   └── main.py           # FastAPI 앱
├── alembic/              # DB 마이그레이션
├── tests/                # 테스트 코드
├── docker-compose.yaml
├── Dockerfile
└── requirements.txt
```

---

## 🔧 개발 가이드

### 로컬 개발 환경

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### DB 마이그레이션

```bash
# 마이그레이션 생성
docker-compose exec kanban alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
docker-compose exec kanban alembic upgrade head

# 롤백
docker-compose exec kanban alembic downgrade -1
```

### 컨테이너 재빌드

```bash
# 서비스 중지
docker-compose down

# 재빌드 후 시작
docker-compose up -d --build

# 로그 확인
docker-compose logs -f kanban
```

---

## 👥 다른 팀과 협업

이 프로젝트는 weAlist 공통 인프라를 사용합니다.

- 다른 팀(Member, Frontend 등)과 인프라를 공유하는 방법: [infrastructure/SHARING.md](../../infrastructure/SHARING.md)
- PostgreSQL/Redis 설정 및 포트 충돌 해결 가이드 포함

---

## 📚 프로젝트 문서

| 문서 | 설명 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 샤딩 대비 설계 (FK 제거) |
| [K8S_READY.md](K8S_READY.md) | Kubernetes 준비 사항 및 배포 가이드 |
| [infrastructure/SHARING.md](../../infrastructure/SHARING.md) | 팀 간 인프라 공유 가이드 |
| [JWT_TEST.md](JWT_TEST.md) | JWT 토큰 테스트 가이드 |

---

## 🚧 향후 계획 (Phase 2)

### Kubernetes 마이그레이션
- [ ] Helm Chart 작성
- [ ] ConfigMap/Secret 분리
- [ ] HPA (Horizontal Pod Autoscaler) 설정
- [ ] PersistentVolume 구성

### CI/CD 파이프라인
- [ ] GitHub Actions 워크플로우
- [ ] 자동 빌드 & 배포
- [ ] 컨테이너 이미지 레지스트리 (ECR/GCR)
- [ ] 자동 테스트 실행

### 모니터링 & 로깅
- [ ] Prometheus + Grafana
- [ ] ELK Stack 또는 Loki
- [ ] 분산 추적 (Jaeger/Zipkin)
- [ ] 알림 설정 (Slack/Discord)

### 보안 강화
- [ ] Network Policy 설정
- [ ] RBAC 구성
- [ ] Secret 암호화 (Sealed Secrets)
- [ ] 컨테이너 보안 스캔 (Trivy)

---

## 🛠️ 트러블슈팅

### 포트 충돌
```bash
# 포트 사용 확인
lsof -i :8000

# 포트 변경 (.env 파일)
PORT=8001
```

### 데이터베이스 연결 실패
```bash
# 인프라 상태 확인
cd infrastructure
docker-compose ps

# PostgreSQL 로그
docker-compose logs postgres

# 비밀번호 일치 확인
# infrastructure/.env와 services/kanban/.env 비교
```

### 컨테이너 재시작
```bash
# Kanban 서비스만 재시작
docker-compose restart kanban

# 전체 재시작 (인프라 포함)
cd infrastructure && docker-compose restart
cd services/kanban && docker-compose restart
```

---

## 🤝 기여

### 사용 도구
- [Claude Code](https://claude.ai/code) - 코드 작성 보조
- [FastAPI](https://fastapi.tiangolo.com/) - 웹 프레임워크
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM

### 참고 자료
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [12-Factor App](https://12factor.net/)
- [REST API Design Guidelines](https://restfulapi.net/)

---

## 📄 라이선스

이 프로젝트는 학습 목적으로 개발되었습니다.

---

**Made with by Oranges Team**
