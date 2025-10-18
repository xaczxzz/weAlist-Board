# weAlist 공통 인프라 공유 가이드

이 문서는 weAlist 공통 인프라를 다른 팀(예: Member 팀)과 공유하기 위한 가이드입니다.

## 공유해야 할 파일

다른 팀에게 다음 파일들을 공유하세요:

### 1. 인프라 디렉토리 전체
```
infrastructure/
├── docker-compose.yaml    # PostgreSQL, Redis 설정
├── .env.example           # 환경변수 템플릿
├── .gitignore            # Git 제외 설정
├── README.md             # 인프라 사용 가이드
└── SHARING.md            # 이 파일
```

### 2. 환경변수 설정 정보

**⚠️ 주의: 실제 `.env` 파일은 공유하지 마세요! 비밀번호가 포함되어 있습니다.**

대신 다음 정보를 **안전한 방법**으로 공유하세요:
- Slack DM, 비밀번호 관리 도구(1Password, LastPass 등), 또는 암호화된 메시지

## 공유해야 할 환경변수 값

### PostgreSQL 설정
```bash
POSTGRES_DB=wealist_db
POSTGRES_USER=wealist_user
POSTGRES_PASSWORD=[실제 비밀번호 - 안전하게 공유]
```

### Redis 설정
```bash
REDIS_PASSWORD=[실제 비밀번호 - 안전하게 공유]
```

## 다른 팀이 해야 할 작업

### 1. 인프라 파일 복사
```bash
# weAlist 공통 인프라 디렉토리를 자신의 프로젝트로 복사
cp -r infrastructure/ /path/to/member-service/infrastructure/
```

### 2. 환경변수 파일 생성
```bash
cd infrastructure
cp .env.example .env
```

### 3. `.env` 파일에 실제 비밀번호 입력
```bash
# .env 파일을 열어서 POSTGRES_PASSWORD와 REDIS_PASSWORD를
# 공유받은 실제 비밀번호로 변경
vim .env  # 또는 nano .env
```

**중요: 비밀번호는 Kanban 팀과 동일하게 설정해야 합니다!**

### 4. 인프라가 이미 실행 중인지 확인
```bash
# wealist-network 네트워크가 있는지 확인
docker network ls | grep wealist-network

# wealist-postgres 컨테이너가 실행 중인지 확인
docker ps | grep wealist-postgres
```

- **이미 실행 중이면**: `docker-compose up -d`를 실행하지 마세요! (중복 실행 방지)
- **실행 중이 아니면**: `docker-compose up -d`로 인프라를 시작하세요

### 5. 자신의 서비스 docker-compose.yaml 수정

Member 서비스의 `docker-compose.yaml`에서 다음과 같이 설정:

```yaml
version: '3.8'

services:
  member:  # 자신의 서비스 이름
    build:
      context: .
      dockerfile: Dockerfile
    container_name: member-api
    env_file:
      - .env
    environment:
      # Kanban 팀과 동일한 데이터베이스 정보 사용
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@wealist-postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@wealist-redis:6379/0
      # 자신의 서비스 포트는 다르게 설정 (예: 8001)
      MEMBER_PORT: 8001
    ports:
      - "${MEMBER_PORT:-8001}:8000"  # Kanban은 8000, Member는 8001
    volumes:
      - .:/app
    networks:
      - wealist-network  # ← 중요: 같은 네트워크 사용
    restart: unless-stopped
    depends_on:
      - wealist-postgres  # ← 중요: 컨테이너 이름 동일하게
      - wealist-redis

# 외부 네트워크 사용
networks:
  wealist-network:
    external: true  # ← 중요: 이미 존재하는 네트워크 사용
```

### 6. 자신의 서비스 .env.example 수정

Member 서비스의 `.env.example`에 다음 내용 추가:

```bash
# 데이터베이스 설정 (infrastructure/.env와 동일하게 설정)
POSTGRES_DB=wealist_db
POSTGRES_USER=wealist_user
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD_IN_PRODUCTION

# Redis 설정 (infrastructure/.env와 동일하게 설정)
REDIS_PASSWORD=CHANGE_THIS_PASSWORD_IN_PRODUCTION

# 애플리케이션 설정
ENV=development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
MEMBER_PORT=8001  # Kanban과 다른 포트 사용

# CORS 설정
CORS_ORIGINS=http://localhost:3000,http://localhost:8001
```

## 데이터베이스 스키마 분리

같은 PostgreSQL 인스턴스를 사용하지만, 각 팀은 자신의 테이블을 관리합니다:

- **Kanban 팀**: workspaces, projects, tickets, tasks 테이블
- **Member 팀**: users, sessions, roles 등 회원 관련 테이블

서로의 테이블을 직접 수정하지 마세요! API를 통해 데이터를 주고받으세요.

## 주의사항

### ✅ 해야 할 것
- infrastructure/.env 파일의 비밀번호를 Kanban 팀과 **정확히 동일하게** 설정
- 서비스 포트는 **다르게** 설정 (Kanban: 8000, Member: 8001)
- 같은 `wealist-network` 네트워크 사용
- 컨테이너 이름 참조: `wealist-postgres`, `wealist-redis`

### ❌ 하지 말아야 할 것
- infrastructure의 docker-compose.yaml 수정 (변경 필요 시 두 팀이 협의)
- .env 파일을 Git에 커밋 (절대 금지!)
- 다른 팀의 데이터베이스 테이블 직접 수정
- 인프라가 이미 실행 중인데 다시 `docker-compose up` 실행

## 문제 해결

### Q: "network wealist-network not found" 에러가 발생해요
**A:** 인프라를 먼저 실행하세요:
```bash
cd infrastructure
docker-compose up -d
```

### Q: 데이터베이스 연결이 안 돼요
**A:** 비밀번호가 일치하는지 확인:
1. `infrastructure/.env`의 POSTGRES_PASSWORD
2. `services/member/.env`의 POSTGRES_PASSWORD
3. 두 값이 정확히 같아야 합니다

### Q: 포트 충돌이 발생해요
**A:** 각 서비스는 다른 포트를 사용해야 합니다:
- Kanban: 8000
- Member: 8001
- 다른 서비스: 8002, 8003, ...

### Q: 인프라를 재시작하고 싶어요
**A:** 두 팀이 협의한 후 진행:
```bash
# 모든 서비스 중지
cd services/kanban && docker-compose down
cd services/member && docker-compose down

# 인프라 재시작
cd infrastructure
docker-compose down
docker-compose up -d

# 서비스 재시작
cd services/kanban && docker-compose up -d
cd services/member && docker-compose up -d
```

## 연락처

인프라 관련 문제가 있거나 변경이 필요한 경우:
- Kanban 팀과 협의 필요
- 변경 사항은 두 팀 모두에게 영향을 미칩니다

---

📝 **이 문서를 Member 팀과 공유하세요!**
