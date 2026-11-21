"""Tests for the database schema and the Alembic migrations (WBS-1.2).

These tests need PostgreSQL with pgvector. Set DATABASE_URL, for example:
postgresql+asyncpg://chiron:chiron@localhost:5432/chiron
"""

import asyncio

import asyncpg
import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import command
from app.db.models import Base

EXPECTED_TABLES = {
    "subjects",
    "classes",
    "users",
    "courses",
    "units",
    "topics",
    "teaching_assignments",
    "student_teachers",
    "teacher_administrators",
    "student_administrators",
    "assessments",
    "assessment_topics",
    "grades",
    "refresh_tokens",
    "jobs",
    "sources",
    "passages",
    "questions",
    "question_sources",
    "question_citations",
    "summaries",
    "summary_sources",
    "quizzes",
    "quiz_sources",
    "quiz_questions",
    "quiz_options",
    "quiz_answers",
    "study_plans",
    "study_plan_items",
    "study_plan_steps",
    "token_usage",
}

SUBJECT = "00000000-0000-0000-0000-000000000001"
CLASS = "00000000-0000-0000-0000-000000000002"
COURSE = "00000000-0000-0000-0000-000000000003"
UNIT = "00000000-0000-0000-0000-000000000004"
TOPIC = "00000000-0000-0000-0000-000000000005"
STUDENT = "00000000-0000-0000-0000-000000000010"
TEACHER = "00000000-0000-0000-0000-000000000011"
TEACHER_2 = "00000000-0000-0000-0000-000000000012"
ADMIN = "00000000-0000-0000-0000-000000000013"
JOB = "00000000-0000-0000-0000-000000000020"
SOURCE = "00000000-0000-0000-0000-000000000021"
QUIZ = "00000000-0000-0000-0000-000000000030"
QUIZ_QUESTION = "00000000-0000-0000-0000-000000000031"
PLAN = "00000000-0000-0000-0000-000000000040"

SEED = f"""
INSERT INTO subjects (id, name) VALUES ('{SUBJECT}', 'Kimya');
INSERT INTO classes (id, portal_class_id, name, grade_level, section)
    VALUES ('{CLASS}', '10-A', '10-A', 10, 'A');
INSERT INTO courses (id, portal_course_id, name, subject_id, grade_level)
    VALUES ('{COURSE}', 'KIM10', 'Kimya 10', '{SUBJECT}', 10);
INSERT INTO units (id, portal_unit_id, course_id, position, name)
    VALUES ('{UNIT}', 'KIM10-U1', '{COURSE}', 1, 'Unit');
INSERT INTO topics (id, portal_topic_id, unit_id, position, name)
    VALUES ('{TOPIC}', 'KIM10-U1-T1', '{UNIT}', 1, 'Topic');
INSERT INTO users (id, portal_id, role, first_name, last_name, class_id)
    VALUES ('{STUDENT}', 'OGR-1001', 'student', 'Elif', 'Aksoy', '{CLASS}');
INSERT INTO users (id, portal_id, role, first_name, last_name, subject_id)
    VALUES ('{TEACHER}', 'OGT-2001', 'teacher', 'Murat', 'Ercan', '{SUBJECT}');
INSERT INTO users (id, portal_id, role, first_name, last_name, subject_id)
    VALUES ('{TEACHER_2}', 'OGT-2002', 'teacher', 'Gulsen', 'Tekin', '{SUBJECT}');
INSERT INTO users (id, portal_id, role, first_name, last_name)
    VALUES ('{ADMIN}', 'YON-3001', 'administrator', 'Ayse', 'Tunc');
INSERT INTO jobs (id, user_id, type, status) VALUES ('{JOB}', '{STUDENT}', 'quiz', 'waiting');
"""


ASSESSMENT = (
    "INSERT INTO assessments (id, portal_assessment_id, course_id, class_id, title, type, date) "
    f"VALUES ('{QUIZ}', 'KIM10-10A-KS1', '{COURSE}', '{CLASS}', 'Quiz', 'quiz', '2026-11-01')"
)


def upgrade(alembic_config) -> None:
    command.upgrade(alembic_config, "head")


def tables(sql) -> set[str]:
    rows = sql("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    return {row["tablename"] for row in rows} - {"alembic_version"}


def assert_rejected(sql, constraint: str, *statements: str) -> None:
    """The statements fail on the given constraint, not on another error."""
    with pytest.raises(asyncpg.IntegrityConstraintViolationError) as error:
        sql(SEED, *statements)
    assert error.value.constraint_name == constraint


# ---------------------------------------------------------------- migrations


def test_upgrade_creates_all_tables(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert tables(sql) == EXPECTED_TABLES


def test_upgrade_installs_pgvector(alembic_config, sql) -> None:
    upgrade(alembic_config)
    rows = sql("SELECT extname FROM pg_extension WHERE extname = 'vector'")
    assert len(rows) == 1


def test_downgrade_removes_all_tables(alembic_config, sql) -> None:
    upgrade(alembic_config)
    command.downgrade(alembic_config, "base")
    assert tables(sql) == set()


def test_models_match_migrations(alembic_config, database_url) -> None:
    upgrade(alembic_config)

    async def diff() -> list:
        engine = create_async_engine(database_url)
        try:
            async with engine.connect() as connection:
                return await connection.run_sync(
                    lambda sync: compare_metadata(MigrationContext.configure(sync), Base.metadata)
                )
        finally:
            await engine.dispose()

    assert asyncio.run(diff()) == []


# ---------------------------------------------------------------- constraints


def test_seed_is_valid(alembic_config, sql) -> None:
    upgrade(alembic_config)
    sql(SEED)


def test_portal_id_is_unique(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "uq_users_portal_id",
        "INSERT INTO users (portal_id, role, first_name, last_name) "
        "VALUES ('OGR-1001', 'student', 'X', 'Y')",
    )


def test_password_hash_needs_activation_time(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "ck_users_password_with_activation",
        f"UPDATE users SET password_hash = 'hash' WHERE id = '{STUDENT}'",
    )


def test_only_teachers_have_a_subject(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "ck_users_subject_only_for_teacher",
        f"UPDATE users SET subject_id = '{SUBJECT}' WHERE id = '{STUDENT}'",
    )


def test_student_has_one_teacher_for_each_course(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "pk_student_teachers",
        f"INSERT INTO student_teachers (student_id, course_id, teacher_id) "
        f"VALUES ('{STUDENT}', '{COURSE}', '{TEACHER}')",
        f"INSERT INTO student_teachers (student_id, course_id, teacher_id) "
        f"VALUES ('{STUDENT}', '{COURSE}', '{TEACHER_2}')",
    )


def test_teacher_has_one_administrator(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "pk_teacher_administrators",
        f"INSERT INTO teacher_administrators (teacher_id, administrator_id) "
        f"VALUES ('{TEACHER}', '{ADMIN}')",
        f"INSERT INTO teacher_administrators (teacher_id, administrator_id) "
        f"VALUES ('{TEACHER}', '{ADMIN}')",
    )


def test_grade_needs_a_topic_of_the_assessment(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "fk_grades_assessment_id_assessment_topics",
        ASSESSMENT,
        f"INSERT INTO grades (assessment_id, topic_id, student_id, points) "
        f"VALUES ('{QUIZ}', '{TOPIC}', '{STUDENT}', 5)",
    )


def test_grade_points_are_not_negative(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "ck_grades_points_not_negative",
        ASSESSMENT,
        f"INSERT INTO assessment_topics (assessment_id, topic_id, max_points) "
        f"VALUES ('{QUIZ}', '{TOPIC}', 10)",
        f"INSERT INTO grades (assessment_id, topic_id, student_id, points) "
        f"VALUES ('{QUIZ}', '{TOPIC}', '{STUDENT}', -1)",
    )


def test_source_size_is_at_most_20_mb(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "ck_sources_size_limit",
        f"INSERT INTO sources (student_id, course_id, file_name, format, size_bytes, "
        f"storage_key, status, job_id) VALUES ('{STUDENT}', '{COURSE}', 'a.pdf', 'pdf', "
        f"20971521, 'key', 'processing', '{JOB}')",
    )


def test_source_format_is_checked(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "ck_sources_source_format",
        f"INSERT INTO sources (student_id, course_id, file_name, format, size_bytes, "
        f"storage_key, status, job_id) VALUES ('{STUDENT}', '{COURSE}', 'a.doc', 'doc', "
        f"100, 'key', 'processing', '{JOB}')",
    )


def test_quiz_question_has_one_correct_option(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "uq_quiz_options_one_correct",
        f"INSERT INTO quizzes (id, student_id, course_id, job_id) "
        f"VALUES ('{QUIZ}', '{STUDENT}', '{COURSE}', '{JOB}')",
        f"INSERT INTO quiz_questions (id, quiz_id, position, text, topic_id) "
        f"VALUES ('{QUIZ_QUESTION}', '{QUIZ}', 1, 'Q', '{TOPIC}')",
        f"INSERT INTO quiz_options (question_id, position, text, is_correct) "
        f"VALUES ('{QUIZ_QUESTION}', 1, 'A', true)",
        f"INSERT INTO quiz_options (question_id, position, text, is_correct) "
        f"VALUES ('{QUIZ_QUESTION}', 2, 'B', true)",
    )


def test_study_hours_are_between_1_and_4(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "ck_study_plan_items_hours_range",
        f"INSERT INTO study_plans (id, student_id, week_start, status) "
        f"VALUES ('{PLAN}', '{STUDENT}', '2026-11-16', 'ready')",
        f"INSERT INTO study_plan_items (plan_id, position, topic_id, course_id, reason, "
        f"success_rate, hours) VALUES ('{PLAN}', 1, '{TOPIC}', '{COURSE}', "
        f"'below_threshold', 45, 5)",
    )


def test_one_study_plan_for_each_student_and_week(alembic_config, sql) -> None:
    upgrade(alembic_config)
    assert_rejected(
        sql,
        "uq_study_plans_student_id_week_start",
        f"INSERT INTO study_plans (student_id, week_start, status) "
        f"VALUES ('{STUDENT}', '2026-11-16', 'ready')",
        f"INSERT INTO study_plans (student_id, week_start, status) "
        f"VALUES ('{STUDENT}', '2026-11-16', 'ready')",
    )


def test_deleting_a_user_deletes_the_personal_data(alembic_config, sql) -> None:
    """FR-09, NFR-06: no row of a deleted student stays in the database."""
    upgrade(alembic_config)
    sql(
        SEED,
        f"INSERT INTO sources (id, student_id, course_id, file_name, format, size_bytes, "
        f"storage_key, status, job_id) VALUES ('{SOURCE}', '{STUDENT}', '{COURSE}', 'a.pdf', "
        f"'pdf', 100, 'key', 'ready', '{JOB}')",
        f"INSERT INTO passages (source_id, position, text, page) VALUES ('{SOURCE}', 1, 'x', 1)",
        f"INSERT INTO refresh_tokens (user_id, token_hash, expires_at) "
        f"VALUES ('{STUDENT}', 'h', now() + interval '1 day')",
        f"INSERT INTO token_usage (student_id, purpose, provider, model, prompt_tokens, "
        f"completion_tokens) VALUES ('{STUDENT}', 'question', 'p', 'm', 10, 5)",
        f"INSERT INTO student_teachers (student_id, course_id, teacher_id) "
        f"VALUES ('{STUDENT}', '{COURSE}', '{TEACHER}')",
        f"INSERT INTO student_administrators (student_id, administrator_id) "
        f"VALUES ('{STUDENT}', '{ADMIN}')",
        f"INSERT INTO study_plans (student_id, week_start, status) "
        f"VALUES ('{STUDENT}', '2026-11-16', 'no_grades')",
        ASSESSMENT,
        f"INSERT INTO assessment_topics (assessment_id, topic_id, max_points) "
        f"VALUES ('{QUIZ}', '{TOPIC}', 10)",
        f"INSERT INTO grades (assessment_id, topic_id, student_id, points) "
        f"VALUES ('{QUIZ}', '{TOPIC}', '{STUDENT}', 5)",
        f"INSERT INTO questions (student_id, course_id, question, answer, has_answer) "
        f"VALUES ('{STUDENT}', '{COURSE}', 'q', 'a', true)",
        f"INSERT INTO summaries (student_id, course_id, job_id) "
        f"VALUES ('{STUDENT}', '{COURSE}', '{JOB}')",
        f"INSERT INTO quizzes (student_id, course_id, job_id) "
        f"VALUES ('{STUDENT}', '{COURSE}', '{JOB}')",
        f"DELETE FROM users WHERE id = '{STUDENT}'",
    )
    for table in [
        "sources",
        "passages",
        "refresh_tokens",
        "token_usage",
        "student_teachers",
        "student_administrators",
        "study_plans",
        "grades",
        "questions",
        "summaries",
        "quizzes",
        "jobs",
    ]:
        assert sql(f"SELECT count(*) AS n FROM {table}")[0]["n"] == 0, table


def test_deleting_a_teacher_keeps_the_students(alembic_config, sql) -> None:
    """The students of a deleted teacher become unassigned in that course."""
    upgrade(alembic_config)
    sql(
        SEED,
        f"INSERT INTO student_teachers (student_id, course_id, teacher_id) "
        f"VALUES ('{STUDENT}', '{COURSE}', '{TEACHER}')",
        f"DELETE FROM users WHERE id = '{TEACHER}'",
    )
    assert sql(f"SELECT count(*) AS n FROM users WHERE id = '{STUDENT}'")[0]["n"] == 1
    assert sql("SELECT count(*) AS n FROM student_teachers")[0]["n"] == 0


@pytest.mark.parametrize(
    ("table", "member", "constraint"),
    [
        (
            "teacher_administrators",
            "teacher_id",
            "fk_teacher_administrators_administrator_id_users",
        ),
        (
            "student_administrators",
            "student_id",
            "fk_student_administrators_administrator_id_users",
        ),
    ],
)
def test_administrator_with_assignments_cannot_be_deleted(
    alembic_config, sql, table: str, member: str, constraint: str
) -> None:
    """Each teacher and student keeps one administrator. Move the assignments first."""
    upgrade(alembic_config)
    user = TEACHER if member == "teacher_id" else STUDENT
    assert_rejected(
        sql,
        constraint,
        f"INSERT INTO {table} ({member}, administrator_id) VALUES ('{user}', '{ADMIN}')",
        f"DELETE FROM users WHERE id = '{ADMIN}'",
    )
