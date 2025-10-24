# `kanban-service` 데이터베이스 스키마 (PostgreSQL)

이 문서는 `kanban-service` 프로젝트의 SQLAlchemy 모델을 기반으로 추정된 PostgreSQL `CREATE TABLE` 쿼리를 제공합니다. 프로젝트의 "외래 키 없음" 전략에 따라, 데이터베이스 수준의 외래 키 제약 조건은 포함되지 않습니다.

## 공통 필드 (BaseModel)

모든 테이블은 다음 공통 필드를 포함합니다:
- `id` (UUID) - 기본 키
- `created_at` (TIMESTAMP) - 생성 시간
- `updated_at` (TIMESTAMP) - 수정 시간
- `created_by` (UUID) - 생성자 (User Service 참조)
- `updated_by` (UUID) - 수정자 (User Service 참조, nullable)

## 1. `workspaces` 테이블

워크스페이스(작업 공간) 정보를 저장합니다.

```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_by UUID
);

CREATE INDEX idx_workspaces_name ON workspaces(name);
CREATE INDEX idx_workspaces_created_by ON workspaces(created_by);
CREATE INDEX idx_workspaces_updated_by ON workspaces(updated_by);

COMMENT ON COLUMN workspaces.created_by IS 'References users.user_id from User service (no FK for microservice)';
COMMENT ON COLUMN workspaces.updated_by IS 'References users.user_id from User service (no FK for microservice)';
```

## 2. `projects` 테이블

프로젝트 정보를 저장합니다. `workspace_id`는 `workspaces` 테이블의 `id`와 매핑되지만, 외래 키 제약은 없습니다.

```sql
CREATE TYPE project_status AS ENUM ('PLANNING', 'ACTIVE', 'COMPLETED', 'ON_HOLD');
CREATE TYPE priority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT');

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status project_status NOT NULL DEFAULT 'PLANNING',
    priority priority NOT NULL DEFAULT 'MEDIUM',
    workspace_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_by UUID
);

CREATE INDEX idx_projects_name ON projects(name);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_priority ON projects(priority);
CREATE INDEX idx_projects_workspace_id ON projects(workspace_id);
CREATE INDEX idx_projects_created_by ON projects(created_by);
CREATE INDEX idx_projects_updated_by ON projects(updated_by);

COMMENT ON COLUMN projects.workspace_id IS 'References workspaces.id (no FK for sharding)';
COMMENT ON COLUMN projects.created_by IS 'References users.user_id from User service (no FK for microservice)';
COMMENT ON COLUMN projects.updated_by IS 'References users.user_id from User service (no FK for microservice)';
```

## 3. `tickets` 테이블

티켓 정보를 저장합니다. `project_id`는 `projects` 테이블의 `id`와, `assignee_id`는 User Service의 `users.user_id`와 매핑되지만, 외래 키 제약은 없습니다.

```sql
CREATE TYPE ticket_status AS ENUM ('OPEN', 'IN_PROGRESS', 'REVIEW', 'DONE', 'BLOCKED');

CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(300) NOT NULL,
    description TEXT,
    status ticket_status NOT NULL DEFAULT 'OPEN',
    priority priority NOT NULL DEFAULT 'MEDIUM',
    project_id UUID NOT NULL,
    assignee_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_by UUID
);

CREATE INDEX idx_tickets_title ON tickets(title);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_project_id ON tickets(project_id);
CREATE INDEX idx_tickets_assignee_id ON tickets(assignee_id);
CREATE INDEX idx_tickets_created_by ON tickets(created_by);
CREATE INDEX idx_tickets_updated_by ON tickets(updated_by);

COMMENT ON COLUMN tickets.project_id IS 'References projects.id (no FK for sharding)';
COMMENT ON COLUMN tickets.assignee_id IS 'References users.user_id from User service - 티켓 담당자';
COMMENT ON COLUMN tickets.created_by IS 'References users.user_id from User service (no FK for microservice)';
COMMENT ON COLUMN tickets.updated_by IS 'References users.user_id from User service (no FK for microservice)';
```

## 4. `tasks` 테이블

태스크 정보를 저장합니다. `ticket_id`는 `tickets` 테이블의 `id`와, `assignee_id`는 User Service의 `users.user_id`와 매핑되지만, 외래 키 제약은 없습니다.

```sql
CREATE TYPE task_status AS ENUM ('TODO', 'IN_PROGRESS', 'REVIEW', 'DONE');

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(300) NOT NULL,
    description TEXT,
    status task_status NOT NULL DEFAULT 'TODO',
    completed_at TIMESTAMP WITH TIME ZONE,
    ticket_id UUID NOT NULL,
    assignee_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_by UUID
);

CREATE INDEX idx_tasks_title ON tasks(title);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_ticket_id ON tasks(ticket_id);
CREATE INDEX idx_tasks_assignee_id ON tasks(assignee_id);
CREATE INDEX idx_tasks_created_by ON tasks(created_by);
CREATE INDEX idx_tasks_updated_by ON tasks(updated_by);

COMMENT ON COLUMN tasks.ticket_id IS 'References tickets.id (no FK for sharding)';
COMMENT ON COLUMN tasks.assignee_id IS 'References users.user_id from User service - 작업 담당자';
COMMENT ON COLUMN tasks.completed_at IS 'Task 완료 시간 (status가 DONE일 때 설정됨)';
COMMENT ON COLUMN tasks.created_by IS 'References users.user_id from User service (no FK for microservice)';
COMMENT ON COLUMN tasks.updated_by IS 'References users.user_id from User service (no FK for microservice)';
```

## 테이블 간 관계 (논리적)

```
workspaces (1) ─── (N) projects
                      │
                      └─── (N) tickets
                              │
                              └─── (N) tasks

User Service의 users ──┬─── (N) workspaces.created_by
                        ├─── (N) projects.created_by
                        ├─── (N) tickets.created_by/assignee_id
                        └─── (N) tasks.created_by/assignee_id
```

## 중요 사항

1. **외래 키 없음**: 마이크로서비스 아키텍처 및 샤딩을 위해 데이터베이스 수준의 외래 키 제약 조건을 사용하지 않습니다.

2. **UUID 사용**: 모든 ID는 UUID 타입을 사용하여 분산 환경에서 고유성을 보장합니다.

3. **타임스탬프**: 모든 테이블은 `created_at`과 `updated_at`을 포함하며, `TIMESTAMP WITH TIME ZONE`을 사용합니다.

4. **Audit 정보**: `created_by`와 `updated_by`는 User Service의 사용자를 참조하지만, 외래 키 제약은 없습니다.

5. **Enum 타입**: 상태(Status)와 우선순위(Priority)는 PostgreSQL ENUM 타입으로 정의됩니다.

6. **인덱스**: 자주 조회되는 컬럼에 인덱스가 생성되어 있습니다 (name, status, priority, 외래 키 참조 컬럼 등).
