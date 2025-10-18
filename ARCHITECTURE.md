# Kanban Service 아키텍처

## 샤딩 및 DB 분리 대비 설계

### Foreign Key 제거

이 프로젝트는 **향후 샤딩 및 데이터베이스 분리**를 고려하여 설계되었습니다.

#### 설계 결정

- ❌ **DB 레벨 Foreign Key 사용 안함**
- ✅ **애플리케이션 레벨에서 참조 무결성 관리**
- ✅ **샤딩 시 테이블을 다른 DB 서버로 분산 가능**

#### 모델 구조

```python
# ❌ 기존 방식 (FK 사용 - 샤딩 불가)
workspace_id = Column(ForeignKey("workspaces.id", ondelete="CASCADE"))

# ✅ 현재 방식 (FK 없음 - 샤딩 가능)
workspace_id = Column(
    Integer,
    nullable=False,
    index=True,
    comment="References workspaces.id (no FK for sharding)"
)
```

### CASCADE 삭제 처리

DB의 `ondelete="CASCADE"` 대신 **애플리케이션 코드에서 직접 처리**합니다.

#### Workspace 삭제 시
```
Workspace 삭제
  ↓
1. 해당 Workspace의 모든 Project 찾기
2. 각 Project의 모든 Ticket 찾기
3. 각 Ticket의 모든 Task 삭제
4. 모든 Ticket 삭제
5. 모든 Project 삭제
6. Workspace 삭제
```

#### 코드 예시 (`app/api/workspaces.py:85`)

```python
@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: int, db: Session = Depends(get_db)):
    # 애플리케이션 레벨에서 CASCADE 삭제 (샤딩 대비)
    projects = db.query(Project).filter(Project.workspace_id == workspace_id).all()
    project_ids = [p.id for p in projects]

    if project_ids:
        tickets = db.query(Ticket).filter(Ticket.project_id.in_(project_ids)).all()
        ticket_ids = [t.id for t in tickets]

        if ticket_ids:
            # Tasks 삭제
            db.query(Task).filter(Task.ticket_id.in_(ticket_ids)).delete()

        # Tickets 삭제
        db.query(Ticket).filter(Ticket.project_id.in_(project_ids)).delete()

    # Projects 삭제
    db.query(Project).filter(Project.workspace_id == workspace_id).delete()

    # Workspace 삭제
    db.delete(workspace)
    db.commit()
```

### 향후 샤딩 시나리오

#### 1단계: 현재 (단일 DB)
```
PostgreSQL (wealist_db)
├── workspaces
├── projects
├── tickets
└── tasks
```

#### 2단계: 테이블 샤딩
```
DB Shard 1                    DB Shard 2
├── workspaces (id 1-1000)   ├── workspaces (id 1001-2000)
├── projects (workspace 1-1000)  ├── projects (workspace 1001-2000)
├── tickets                   ├── tickets
└── tasks                     └── tasks
```

#### 3단계: 서비스 분리
```
Workspace Service (DB 1)      Ticket Service (DB 2)
├── workspaces                ├── tickets
└── projects                  └── tasks
```

### 장점

✅ **확장성**: 트래픽 증가 시 DB를 수평 분할 가능
✅ **유연성**: 테이블을 다른 DB/서비스로 쉽게 이동
✅ **성능**: 각 샤드에서 독립적으로 쿼리 실행
✅ **마이그레이션**: FK 제약 없이 데이터 이동 가능

### 단점 및 대응

❌ **참조 무결성**: DB가 자동으로 보장하지 않음
✅ **대응**: 애플리케이션 로직에서 체크 (예: Project 생성 시 Workspace 존재 확인)

❌ **트랜잭션**: 여러 DB에 걸친 트랜잭션 불가
✅ **대응**: Saga 패턴, 분산 트랜잭션 (향후 도입)

❌ **JOIN 성능**: 샤드 간 JOIN 불가
✅ **대응**: 데이터 비정규화, 캐싱, API 조합

### 테스트

모든 CASCADE 삭제 로직은 테스트로 검증되었습니다:

```bash
# 36개 테스트, 97% 커버리지
docker-compose exec kanban pytest --cov
```

주요 테스트:
- `test_delete_workspace_success`: Workspace 삭제 시 하위 데이터 모두 삭제 확인
- `test_delete_project_success`: Project 삭제 시 Ticket, Task 삭제 확인
- `test_delete_ticket_success`: Ticket 삭제 시 Task 삭제 확인

---

이 설계를 통해 **초기에는 단일 DB로 단순하게 시작**하되, **나중에 샤딩이나 MSA로 확장 가능**한 구조를 확보했습니다.
