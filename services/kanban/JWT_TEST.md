# JWT 인증 테스트 가이드

Member 서비스가 아직 구현되지 않은 상태에서 Kanban API를 테스트하는 방법입니다.

## 테스트용 JWT 토큰 생성

### 방법 1: 스크립트 사용 (추천)

```bash
# Docker 컨테이너 내부에서 실행
docker-compose exec kanban python scripts/generate_test_token.py

# 다른 user_id로 생성
docker-compose exec kanban python scripts/generate_test_token.py --user-id 2

# 만료 기간 지정 (기본 7일)
docker-compose exec kanban python scripts/generate_test_token.py --expire-days 30
```

### 방법 2: Python으로 직접 생성

```python
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "dev-secret-key-change-in-production"  # .env의 SECRET_KEY와 동일
ALGORITHM = "HS256"

payload = {
    "sub": "1",  # user_id
    "exp": datetime.utcnow() + timedelta(days=7),
    "iat": datetime.utcnow()
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print(token)
```

---

## API 테스트 방법

### 1. cURL

```bash
# 토큰을 변수에 저장
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Workspace 생성
curl -X POST http://localhost:8000/api/workspaces/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "백엔드팀",
    "description": "백엔드 개발팀"
  }'

# Workspace 목록 조회
curl -X GET http://localhost:8000/api/workspaces/ \
  -H "Authorization: Bearer $TOKEN"
```

### 2. HTTPie

```bash
# 토큰 변수
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Workspace 생성
http POST http://localhost:8000/api/workspaces/ \
  "Authorization: Bearer $TOKEN" \
  name="백엔드팀" \
  description="백엔드 개발팀"

# Workspace 목록
http GET http://localhost:8000/api/workspaces/ \
  "Authorization: Bearer $TOKEN"
```

### 3. Swagger UI (추천)

1. **http://localhost:8000/docs** 접속
2. 우측 상단 **"Authorize"** 버튼 클릭
3. Value 입력란에 토큰 붙여넣기 (Bearer 없이)
4. **"Authorize"** 클릭
5. 이제 모든 API에 자동으로 토큰이 포함됩니다!

---

## 개발 환경 설정

### .env 파일 확인

```bash
# services/kanban/.env
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
```

**중요:** Member 팀과 **같은 SECRET_KEY**를 사용해야 합니다!

---

## 토큰 검증 확인

### 토큰 디코딩 (디버깅용)

```python
from jose import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
SECRET_KEY = "dev-secret-key-change-in-production"

payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
print(payload)
# {"sub": "1", "exp": 1234567890, "iat": 1234567890}
```

### JWT.io에서 확인

1. https://jwt.io 접속
2. Encoded 란에 토큰 붙여넣기
3. Verify Signature 섹션에 SECRET_KEY 입력
4. Payload에서 user_id 확인 (sub 필드)

---

## API 응답 예시

### Workspace 생성 (인증 있음)

**Request:**
```bash
POST /api/workspaces/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "name": "백엔드팀",
  "description": "백엔드 개발팀"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "백엔드팀",
  "description": "백엔드 개발팀",
  "created_at": "2025-01-18T10:30:00Z",
  "updated_at": "2025-01-18T10:30:00Z",
  "created_by": 1,        // ← JWT에서 추출한 user_id
  "updated_by": null
}
```

### Ticket 생성 (담당자 지정)

**Request:**
```bash
POST /api/tickets/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "title": "로그인 API 개발",
  "project_id": 1,
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "assignee_id": 2        // ← 담당자 user_id
}
```

**Response:**
```json
{
  "id": 1,
  "title": "로그인 API 개발",
  "project_id": 1,
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "created_at": "2025-01-18T10:30:00Z",
  "updated_at": "2025-01-18T10:30:00Z",
  "created_by": 1,        // ← 생성자 (JWT에서)
  "updated_by": null,
  "assignee_id": 2        // ← 담당자
}
```

---

## 에러 처리

### 토큰 없이 API 호출

```bash
curl -X GET http://localhost:8000/api/workspaces/
```

**Response:**
```json
{
  "detail": "Not authenticated"
}
```
→ **401 Unauthorized**

### 유효하지 않은 토큰

```bash
curl -X GET http://localhost:8000/api/workspaces/ \
  -H "Authorization: Bearer invalid-token"
```

**Response:**
```json
{
  "detail": "Could not validate credentials"
}
```
→ **401 Unauthorized**

### 만료된 토큰

```json
{
  "detail": "Could not validate credentials"
}
```
→ **401 Unauthorized** (토큰 재발급 필요)

---

## Member 서비스 연동 후

Member 서비스가 구현되면:

1. **로그인** → Member 서비스에서 JWT 토큰 받기
   ```bash
   POST http://member-api/auth/login
   {
     "email": "user@example.com",
     "password": "password123"
   }
   # Response: { "access_token": "eyJ..." }
   ```

2. **받은 토큰으로 Kanban API 사용**
   ```bash
   curl -H "Authorization: Bearer eyJ..." http://localhost:8000/api/workspaces/
   ```

**현재는 테스트용 토큰으로 대체합니다!**
