# Database Design (WBS-1.2)

| Field | Details |
|---|---|
| WBS activity | WBS-1.2 Database design and migrations (task T-01, issue #13) |
| Owner | Burak Emre Polat |
| Reviewer | Metin Furkan Amarat |
| Status | Draft, 16.11.2026 |

This note describes the PostgreSQL schema of Chiron.
The models are in `backend/app/db/models.py`. The first migration is `backend/alembic/versions/0001_initial_schema.py`.

Sources: Requirements Specification v1.0, Project Plan v1.1 (WBS-1.2), the [architecture note](architecture.md), the [API contract](../../contracts/openapi.yaml) and the [portal data design](portal-data.md).

## 1. Decisions

| Decision | Reason | Who |
|---|---|---|
| PostgreSQL 17 with pgvector. One database for all data and the embeddings. | Charter and Project Plan. | Charter |
| SQLAlchemy 2 with the async API (`asyncpg`). Alembic for migrations. | FastAPI, the answer stream and LiteLLM are async. | Burak, 16.11.2026 |
| Chiron tables use UUID primary keys. Portal records keep the portal ID in a unique `portal_*_id` column. | The API contract uses UUIDs. Imports match records by the portal ID. | API contract |
| Enumerations are text columns with a `CHECK` constraint, not PostgreSQL enum types. | A new value needs only a new constraint, not an `ALTER TYPE`. | Burak |
| The names of unique constraints and indexes have the table name and all columns, for example `uq_study_plans_student_id_week_start`. | Two constraints that start with the same column get different names. Each name tells what it checks. | Review by Metin |
| Chiron stores each grade row, not only the success rate. | The success rate is a query and stays correct after a corrected grade. Answers question 7 of the portal data design. | Burak |
| Each student and each teacher has exactly one administrator. | The mock data and UC-02 use this model. Answers question 2 of the portal data design. | Burak, 16.11.2026 |
| A later import adds a deleted user again as a new account that is not active. Chiron keeps no list of deleted users. | No trace of a deleted user stays (NFR-06). Answers question 5 of the portal data design. | Burak, 16.11.2026 |
| A teacher and a student have separate administrator assignments. Moving a teacher does not move the students. | UC-02 A3 of the Requirements Specification. | Requirements Specification |
| Chiron adds the account fields that the portal does not give: `password_hash`, `activated_at`, `grades_read_at`. | FR-02, FR-11, UC-01 E3. Answers question 6 of the portal data design. | Burak |

## 2. Tables

```mermaid
erDiagram
    subjects ||--o{ courses : ""
    courses ||--|{ units : ""
    units ||--|{ topics : ""
    classes ||--o{ users : "student in"
    users ||--o{ teaching_assignments : "teacher"
    courses ||--o{ teaching_assignments : ""
    classes ||--o{ teaching_assignments : ""
    users ||--o{ student_teachers : "student / teacher"
    users ||--o| teacher_administrators : "teacher / admin"
    users ||--o| student_administrators : "student / admin"
    assessments ||--|{ assessment_topics : ""
    assessment_topics ||--o{ grades : ""
    users ||--o{ grades : "student"
    users ||--o{ sources : "student"
    sources ||--o{ passages : ""
    users ||--o{ questions : "student"
    questions ||--o{ question_citations : ""
    passages ||--o{ question_citations : ""
    users ||--o{ summaries : "student"
    users ||--o{ quizzes : "student"
    quizzes ||--|{ quiz_questions : ""
    quiz_questions ||--|{ quiz_options : ""
    quiz_questions ||--o| quiz_answers : ""
    users ||--o{ study_plans : "student"
    study_plans ||--o{ study_plan_items : ""
    study_plan_items ||--|{ study_plan_steps : ""
    users ||--o{ token_usage : "student"
    users ||--o{ jobs : ""
    users ||--o{ refresh_tokens : ""
```

### 2.1 Portal data (FR-07, FR-08, FR-10 to FR-12, FR-27)

| Table | Content | Key rules |
|---|---|---|
| `subjects` | Subjects, for example Kimya | Unique name |
| `classes` | Classes, for example 10-A | Unique `portal_class_id` |
| `users` | All accounts of all roles | Unique `portal_id`. `password_hash` is set only with `activated_at`. Only teachers have `subject_id`. Only students have `class_id`. |
| `courses`, `units`, `topics` | Curriculum | Unique portal IDs. Unique `position` in the parent. |
| `teaching_assignments` | The teacher of a course in a class. A student takes the courses of the class. | Key: course and class |
| `student_teachers` | The teacher of a student in a course. Administrators change it (FR-08). | Key: student and course. One teacher for each course. |
| `teacher_administrators` | The administrator of a teacher | Key: teacher. One administrator. |
| `student_administrators` | The administrator of a student | Key: student. One administrator. |
| `assessments`, `assessment_topics` | Quizzes and exams, with the maximum points of each topic | `max_points > 0` |
| `grades` | Points of a student in a topic of an assessment | The topic must be a topic of the assessment. `points >= 0`. |

### 2.2 Sessions and jobs (FR-01, FR-03, FR-04, FR-40)

| Table | Content | Key rules |
|---|---|---|
| `refresh_tokens` | Hash of each refresh token, its expiry and its revocation time | Unique hash. Logout sets `revoked_at`. |
| `jobs` | Background jobs and their status | Status: `waiting`, `running`, `done`, `failed`. `user_id` is null for the weekly planning run. |

### 2.3 Sources and answers (FR-13 to FR-20)

| Table | Content | Key rules |
|---|---|---|
| `sources` | Uploaded files of a student in a course. The file is in Cloud Storage (`storage_key`). | `size_bytes` up to 20 MB. Format: `pdf`, `docx`, `pptx`. Status: `processing`, `ready`, `failed`. |
| `passages` | Chunks of a source with page, slide or heading, and the embedding | `vector(1024)` with an HNSW index (cosine distance) |
| `questions` | Question history with the answer | Index on student, course and time for the history page |
| `question_sources`, `question_citations` | The selected sources and the citations of an answer | |

### 2.4 Summaries and quizzes (FR-21 to FR-25)

| Table | Content | Key rules |
|---|---|---|
| `summaries`, `summary_sources` | Summary jobs and the PDF in Cloud Storage | |
| `quizzes`, `quiz_sources` | Quiz jobs, submission time and score | Score from 0 to 100 |
| `quiz_questions`, `quiz_options` | Questions with topic and citation, and their options | One correct option for each question (partial unique index) |
| `quiz_answers` | The option that the student chose | One answer for each question |

The score of each topic (FR-24) comes from `quiz_answers` with a query. Chiron does not store it again.

### 2.5 Study plans (FR-27 to FR-31)

| Table | Content | Key rules |
|---|---|---|
| `study_plans` | The plan of a student for a week | One plan for each student and week. Status: `ready`, `no_weak_topics`, `no_grades`. |
| `study_plan_items` | A weak topic with the reason, the success rate, the class average and the hours | Hours from 1 to 4. Reason: `below_threshold` or `below_class_average`. |
| `study_plan_steps` | The steps of a topic | Kind: `review_topic` or `practice_questions` |

The plan keeps the success rate and the class average of the planning run. Later grade changes do not change the plan of the week (FR-30 note).

### 2.6 AI usage (FR-34, FR-35, FR-37)

| Table | Content | Key rules |
|---|---|---|
| `token_usage` | One row for each AI request of a student: purpose, provider, model, tokens, cost | Index on student and time for the dashboards and the monthly limit |

## 3. Deleting data (FR-09, FR-17, NFR-06)

- **A user is deleted.** The database deletes all rows of the user with `ON DELETE CASCADE`: sources, passages, questions, summaries, quizzes, study plans, grades, token usage, refresh tokens, jobs and assignments. The test `test_deleting_a_user_deletes_the_personal_data` checks this.
- **An administrator is deleted.** The database refuses the deletion while teachers or students are assigned to the administrator (`ON DELETE RESTRICT` on `teacher_administrators.administrator_id` and `student_administrators.administrator_id`). First move the teachers and the students to another administrator. Then each teacher and each student always has one administrator (section 1). The API does not let an administrator delete an administrator account (`deleteUser` in the contract), so only a person who manages the school setup can do this. The test `test_administrator_with_assignments_cannot_be_deleted` checks this.
- **A teacher is deleted.** The students stay. Their `student_teachers` rows are deleted, so they have no teacher in that course. In `teaching_assignments` and `assessments`, the teacher becomes null.
- **A source is deleted.** Its passages, its citations and its links to summaries and quizzes are deleted. A quiz question keeps its text, but its citation becomes null.
- **Files in Cloud Storage.** The database does not delete files. The service that deletes a user or a source must also delete the files (`storage_key`, `pdf_storage_key`). WBS-2.3 and WBS-4.3 must test this.

## 4. Rules that the database does not check

The application must check these rules. The tests of the services must cover them.

| Rule | Requirement | Checked in |
|---|---|---|
| A course has at most 20 sources of a student | FR-13 | Upload service (WBS-4.3) |
| The user in `student_teachers.teacher_id` is a teacher, and teaches the subject of the course. The same for the other assignment tables and their roles. | FR-07, FR-08 | Assignment service (WBS-2.3) |
| `grades.points` is not more than `max_points` | FR-27 | Portal import (WBS-3.3) |
| A quiz has 5 to 10 questions | FR-22 | Quiz service (WBS-5.4) |
| A student submits a quiz only one time | Contract | Quiz service (WBS-5.5) |

## 5. Local database and tests

1. Start the database: `docker compose -f infra/docker-compose.yml up -d`.
2. Set the URL: `export DATABASE_URL=postgresql+asyncpg://chiron:chiron@localhost:5432/chiron`.
3. Run the migrations: `cd backend && uv run alembic upgrade head`.
4. Run the tests: `uv run pytest`.

The database tests in `tests/backend/db/` create an empty database for each test and drop it after the test. Without `DATABASE_URL`, pytest skips them.
They check that:

- the migration creates all tables and pgvector, and the downgrade removes them,
- the models and the migrations are the same (no autogenerate difference),
- each constraint rejects wrong data, and the error comes from the expected constraint,
- deleting a user deletes the personal data, and deleting a teacher keeps the students.

**For CI (WBS-1.4, Berkay):** add a `pgvector/pgvector:0.8.1-pg17` service container and set `DATABASE_URL`. Otherwise CI skips the database tests.

To change the schema: change `models.py`, run `uv run alembic revision --autogenerate -m "<change>"`, read the generated file and fix it, and add a test.

## 6. Open points

| Point | Proposal in this draft | Decides in |
|---|---|---|
| Embedding size. `vector(1024)` is the size of bge-m3. | 1024 | WBS-4.1 (Metin, Berkay). A different model needs a new migration. |
| The `contents` list of the portal data (videos, documents) | Not in the schema. No requirement uses it yet. | WBS-6.1 (study plan steps) |
| When does Chiron read the curriculum? | The schema supports both answers. | Portal data design, question 4 |
| An answer keeps its text after a source is deleted, but its citations to that source are deleted | Keep the answer | Review |
| Where Cloud SQL runs and which pgvector version it has | PostgreSQL 17 | WBS-9.1 (Berkay) |
