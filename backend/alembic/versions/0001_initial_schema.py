"""Initial schema (WBS-1.2). See docs/design/database.md.

Revision ID: 0001
Revises:
Create Date: 2026-11-21 16:44:39.260215

"""

from collections.abc import Sequence

import pgvector.sqlalchemy
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "classes",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("portal_class_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("grade_level", sa.SmallInteger(), nullable=False),
        sa.Column("section", sa.String(length=16), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_classes")),
        sa.UniqueConstraint("portal_class_id", name=op.f("uq_classes_portal_class_id")),
    )
    op.create_table(
        "subjects",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subjects")),
        sa.UniqueConstraint("name", name=op.f("uq_subjects_name")),
    )
    op.create_table(
        "courses",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("portal_course_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("grade_level", sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["subject_id"], ["subjects.id"], name=op.f("fk_courses_subject_id_subjects")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_courses")),
        sa.UniqueConstraint("portal_course_id", name=op.f("uq_courses_portal_course_id")),
    )
    op.create_index(op.f("ix_courses_subject_id"), "courses", ["subject_id"], unique=False)
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("portal_id", sa.String(length=64), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "student",
                "teacher",
                "administrator",
                name="role",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("class_id", sa.Uuid(), nullable=True),
        sa.Column("subject_id", sa.Uuid(), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("grades_read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role = 'student' OR class_id IS NULL", name=op.f("ck_users_class_only_for_student")
        ),
        sa.CheckConstraint(
            "role = 'teacher' OR subject_id IS NULL", name=op.f("ck_users_subject_only_for_teacher")
        ),
        sa.CheckConstraint(
            "(password_hash IS NULL) = (activated_at IS NULL)",
            name=op.f("ck_users_password_with_activation"),
        ),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["classes.id"],
            name=op.f("fk_users_class_id_classes"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"], ["subjects.id"], name=op.f("fk_users_subject_id_subjects")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("portal_id", name=op.f("uq_users_portal_id")),
    )
    op.create_index(op.f("ix_users_class_id"), "users", ["class_id"], unique=False)
    op.create_table(
        "assessments",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("portal_assessment_id", sa.String(length=64), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("class_id", sa.Uuid(), nullable=False),
        sa.Column("teacher_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "exam",
                "quiz",
                name="assessment_type",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["classes.id"],
            name=op.f("fk_assessments_class_id_classes"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            name=op.f("fk_assessments_course_id_courses"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["users.id"],
            name=op.f("fk_assessments_teacher_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assessments")),
        sa.UniqueConstraint(
            "portal_assessment_id", name=op.f("uq_assessments_portal_assessment_id")
        ),
    )
    op.create_index(op.f("ix_assessments_class_id"), "assessments", ["class_id"], unique=False)
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column(
            "type",
            sa.Enum(
                "source_processing",
                "summary",
                "quiz",
                "portal_import",
                "weekly_planning",
                name="job_type",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "waiting",
                "running",
                "done",
                "failed",
                name="job_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("attempts", sa.SmallInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_jobs_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jobs")),
    )
    op.create_index(op.f("ix_jobs_user_id"), "jobs", ["user_id"], unique=False)
    op.create_table(
        "questions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("has_answer", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            name=op.f("fk_questions_course_id_courses"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_questions_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_questions")),
    )
    op.create_index(
        op.f("ix_questions_student_id_course_id_created_at"),
        "questions",
        ["student_id", "course_id", "created_at"],
        unique=False,
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_refresh_tokens_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refresh_tokens")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_refresh_tokens_token_hash")),
    )
    op.create_index(op.f("ix_refresh_tokens_user_id"), "refresh_tokens", ["user_id"], unique=False)
    op.create_table(
        "student_administrators",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("administrator_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["administrator_id"],
            ["users.id"],
            name=op.f("fk_student_administrators_administrator_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_student_administrators_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("student_id", name=op.f("pk_student_administrators")),
    )
    op.create_index(
        op.f("ix_student_administrators_administrator_id"),
        "student_administrators",
        ["administrator_id"],
        unique=False,
    )
    op.create_table(
        "student_teachers",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("teacher_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            name=op.f("fk_student_teachers_course_id_courses"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_student_teachers_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["users.id"],
            name=op.f("fk_student_teachers_teacher_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("student_id", "course_id", name=op.f("pk_student_teachers")),
    )
    op.create_index(
        op.f("ix_student_teachers_teacher_id"), "student_teachers", ["teacher_id"], unique=False
    )
    op.create_table(
        "study_plans",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "ready",
                "no_weak_topics",
                "no_grades",
                name="study_plan_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_study_plans_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_study_plans")),
        sa.UniqueConstraint(
            "student_id", "week_start", name=op.f("uq_study_plans_student_id_week_start")
        ),
    )
    op.create_table(
        "teacher_administrators",
        sa.Column("teacher_id", sa.Uuid(), nullable=False),
        sa.Column("administrator_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["administrator_id"],
            ["users.id"],
            name=op.f("fk_teacher_administrators_administrator_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["users.id"],
            name=op.f("fk_teacher_administrators_teacher_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("teacher_id", name=op.f("pk_teacher_administrators")),
    )
    op.create_index(
        op.f("ix_teacher_administrators_administrator_id"),
        "teacher_administrators",
        ["administrator_id"],
        unique=False,
    )
    op.create_table(
        "teaching_assignments",
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("class_id", sa.Uuid(), nullable=False),
        sa.Column("teacher_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["classes.id"],
            name=op.f("fk_teaching_assignments_class_id_classes"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            name=op.f("fk_teaching_assignments_course_id_courses"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["users.id"],
            name=op.f("fk_teaching_assignments_teacher_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("course_id", "class_id", name=op.f("pk_teaching_assignments")),
    )
    op.create_index(
        op.f("ix_teaching_assignments_teacher_id"),
        "teaching_assignments",
        ["teacher_id"],
        unique=False,
    )
    op.create_table(
        "units",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("portal_unit_id", sa.String(length=64), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            name=op.f("fk_units_course_id_courses"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_units")),
        sa.UniqueConstraint("course_id", "position", name=op.f("uq_units_course_id_position")),
        sa.UniqueConstraint("portal_unit_id", name=op.f("uq_units_portal_unit_id")),
    )
    op.create_table(
        "quizzes",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "score IS NULL OR (score >= 0 AND score <= 100)", name=op.f("ck_quizzes_score_range")
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            name=op.f("fk_quizzes_course_id_courses"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name=op.f("fk_quizzes_job_id_jobs"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_quizzes_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quizzes")),
    )
    op.create_index(
        op.f("ix_quizzes_student_id_course_id"),
        "quizzes",
        ["student_id", "course_id"],
        unique=False,
    )
    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column(
            "format",
            sa.Enum(
                "pdf",
                "docx",
                "pptx",
                name="source_format",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "processing",
                "ready",
                "failed",
                name="source_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("failure_code", sa.String(length=64), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("job_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "size_bytes > 0 AND size_bytes <= 20971520", name=op.f("ck_sources_size_limit")
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            name=op.f("fk_sources_course_id_courses"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name=op.f("fk_sources_job_id_jobs"), ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_sources_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sources")),
    )
    op.create_index(
        op.f("ix_sources_student_id_course_id"),
        "sources",
        ["student_id", "course_id"],
        unique=False,
    )
    op.create_table(
        "summaries",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("pdf_storage_key", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            name=op.f("fk_summaries_course_id_courses"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name=op.f("fk_summaries_job_id_jobs"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_summaries_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_summaries")),
    )
    op.create_index(
        op.f("ix_summaries_student_id_course_id"),
        "summaries",
        ["student_id", "course_id"],
        unique=False,
    )
    op.create_table(
        "token_usage",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=True),
        sa.Column(
            "purpose",
            sa.Enum(
                "question",
                "summary",
                "quiz",
                "study_plan",
                name="token_purpose",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), nullable=False),
        sa.Column("cost_usd", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "prompt_tokens >= 0 AND completion_tokens >= 0",
            name=op.f("ck_token_usage_tokens_not_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name=op.f("fk_token_usage_job_id_jobs"), ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_token_usage_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_token_usage")),
    )
    op.create_index(
        op.f("ix_token_usage_student_id_created_at"),
        "token_usage",
        ["student_id", "created_at"],
        unique=False,
    )
    op.create_table(
        "topics",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("portal_topic_id", sa.String(length=64), nullable=False),
        sa.Column("unit_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.ForeignKeyConstraint(
            ["unit_id"], ["units.id"], name=op.f("fk_topics_unit_id_units"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_topics")),
        sa.UniqueConstraint("portal_topic_id", name=op.f("uq_topics_portal_topic_id")),
        sa.UniqueConstraint("unit_id", "position", name=op.f("uq_topics_unit_id_position")),
    )
    op.create_table(
        "assessment_topics",
        sa.Column("assessment_id", sa.Uuid(), nullable=False),
        sa.Column("topic_id", sa.Uuid(), nullable=False),
        sa.Column("max_points", sa.Integer(), nullable=False),
        sa.CheckConstraint("max_points > 0", name=op.f("ck_assessment_topics_max_points_positive")),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            ["assessments.id"],
            name=op.f("fk_assessment_topics_assessment_id_assessments"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["topic_id"],
            ["topics.id"],
            name=op.f("fk_assessment_topics_topic_id_topics"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("assessment_id", "topic_id", name=op.f("pk_assessment_topics")),
    )
    op.create_table(
        "passages",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("slide", sa.Integer(), nullable=True),
        sa.Column("heading", sa.Text(), nullable=True),
        sa.Column("embedding", pgvector.sqlalchemy.vector.VECTOR(dim=1024), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("fk_passages_source_id_sources"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_passages")),
        sa.UniqueConstraint("source_id", "position", name=op.f("uq_passages_source_id_position")),
    )
    op.create_index(
        "ix_passages_embedding",
        "passages",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.create_table(
        "question_sources",
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            name=op.f("fk_question_sources_question_id_questions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("fk_question_sources_source_id_sources"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("question_id", "source_id", name=op.f("pk_question_sources")),
    )
    op.create_table(
        "quiz_sources",
        sa.Column("quiz_id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["quiz_id"],
            ["quizzes.id"],
            name=op.f("fk_quiz_sources_quiz_id_quizzes"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("fk_quiz_sources_source_id_sources"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("quiz_id", "source_id", name=op.f("pk_quiz_sources")),
    )
    op.create_table(
        "study_plan_items",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("topic_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column(
            "reason",
            sa.Enum(
                "below_threshold",
                "below_class_average",
                name="study_plan_reason",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("success_rate", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("class_average", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("hours", sa.SmallInteger(), nullable=False),
        sa.CheckConstraint(
            "class_average IS NULL OR class_average BETWEEN 0 AND 100",
            name=op.f("ck_study_plan_items_class_average_range"),
        ),
        sa.CheckConstraint("hours BETWEEN 1 AND 4", name=op.f("ck_study_plan_items_hours_range")),
        sa.CheckConstraint(
            "success_rate BETWEEN 0 AND 100", name=op.f("ck_study_plan_items_success_rate_range")
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], name=op.f("fk_study_plan_items_course_id_courses")
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["study_plans.id"],
            name=op.f("fk_study_plan_items_plan_id_study_plans"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["topic_id"], ["topics.id"], name=op.f("fk_study_plan_items_topic_id_topics")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_study_plan_items")),
        sa.UniqueConstraint(
            "plan_id", "position", name=op.f("uq_study_plan_items_plan_id_position")
        ),
    )
    op.create_table(
        "summary_sources",
        sa.Column("summary_id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("fk_summary_sources_source_id_sources"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["summary_id"],
            ["summaries.id"],
            name=op.f("fk_summary_sources_summary_id_summaries"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("summary_id", "source_id", name=op.f("pk_summary_sources")),
    )
    op.create_table(
        "grades",
        sa.Column("assessment_id", sa.Uuid(), nullable=False),
        sa.Column("topic_id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.CheckConstraint("points >= 0", name=op.f("ck_grades_points_not_negative")),
        sa.ForeignKeyConstraint(
            ["assessment_id", "topic_id"],
            ["assessment_topics.assessment_id", "assessment_topics.topic_id"],
            name=op.f("fk_grades_assessment_id_assessment_topics"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_grades_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("assessment_id", "topic_id", "student_id", name=op.f("pk_grades")),
    )
    op.create_index(
        op.f("ix_grades_student_id_topic_id"), "grades", ["student_id", "topic_id"], unique=False
    )
    op.create_table(
        "question_citations",
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("marker", sa.SmallInteger(), nullable=False),
        sa.Column("passage_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["passage_id"],
            ["passages.id"],
            name=op.f("fk_question_citations_passage_id_passages"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            name=op.f("fk_question_citations_question_id_questions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("question_id", "marker", name=op.f("pk_question_citations")),
    )
    op.create_index(
        op.f("ix_question_citations_passage_id"), "question_citations", ["passage_id"], unique=False
    )
    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("quiz_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("topic_id", sa.Uuid(), nullable=False),
        sa.Column("passage_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["passage_id"],
            ["passages.id"],
            name=op.f("fk_quiz_questions_passage_id_passages"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["quiz_id"],
            ["quizzes.id"],
            name=op.f("fk_quiz_questions_quiz_id_quizzes"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["topic_id"], ["topics.id"], name=op.f("fk_quiz_questions_topic_id_topics")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quiz_questions")),
        sa.UniqueConstraint("quiz_id", "position", name=op.f("uq_quiz_questions_quiz_id_position")),
    )
    op.create_index(
        op.f("ix_quiz_questions_topic_id"), "quiz_questions", ["topic_id"], unique=False
    )
    op.create_table(
        "study_plan_steps",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "review_topic",
                "practice_questions",
                name="study_step_kind",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["study_plan_items.id"],
            name=op.f("fk_study_plan_steps_item_id_study_plan_items"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_study_plan_steps")),
        sa.UniqueConstraint(
            "item_id", "position", name=op.f("uq_study_plan_steps_item_id_position")
        ),
    )
    op.create_table(
        "quiz_options",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["quiz_questions.id"],
            name=op.f("fk_quiz_options_question_id_quiz_questions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quiz_options")),
        sa.UniqueConstraint(
            "question_id", "position", name=op.f("uq_quiz_options_question_id_position")
        ),
    )
    op.create_index(
        "uq_quiz_options_one_correct",
        "quiz_options",
        ["question_id"],
        unique=True,
        postgresql_where=sa.text("is_correct"),
    )
    op.create_table(
        "quiz_answers",
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("option_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["option_id"],
            ["quiz_options.id"],
            name=op.f("fk_quiz_answers_option_id_quiz_options"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["quiz_questions.id"],
            name=op.f("fk_quiz_answers_question_id_quiz_questions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("question_id", name=op.f("pk_quiz_answers")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("quiz_answers")
    op.drop_index(
        "uq_quiz_options_one_correct",
        table_name="quiz_options",
        postgresql_where=sa.text("is_correct"),
    )
    op.drop_table("quiz_options")
    op.drop_table("study_plan_steps")
    op.drop_index(op.f("ix_quiz_questions_topic_id"), table_name="quiz_questions")
    op.drop_table("quiz_questions")
    op.drop_index(op.f("ix_question_citations_passage_id"), table_name="question_citations")
    op.drop_table("question_citations")
    op.drop_index(op.f("ix_grades_student_id_topic_id"), table_name="grades")
    op.drop_table("grades")
    op.drop_table("summary_sources")
    op.drop_table("study_plan_items")
    op.drop_table("quiz_sources")
    op.drop_table("question_sources")
    op.drop_index(
        "ix_passages_embedding",
        table_name="passages",
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.drop_table("passages")
    op.drop_table("assessment_topics")
    op.drop_table("topics")
    op.drop_index(op.f("ix_token_usage_student_id_created_at"), table_name="token_usage")
    op.drop_table("token_usage")
    op.drop_index(op.f("ix_summaries_student_id_course_id"), table_name="summaries")
    op.drop_table("summaries")
    op.drop_index(op.f("ix_sources_student_id_course_id"), table_name="sources")
    op.drop_table("sources")
    op.drop_index(op.f("ix_quizzes_student_id_course_id"), table_name="quizzes")
    op.drop_table("quizzes")
    op.drop_table("units")
    op.drop_index(op.f("ix_teaching_assignments_teacher_id"), table_name="teaching_assignments")
    op.drop_table("teaching_assignments")
    op.drop_index(
        op.f("ix_teacher_administrators_administrator_id"), table_name="teacher_administrators"
    )
    op.drop_table("teacher_administrators")
    op.drop_table("study_plans")
    op.drop_index(op.f("ix_student_teachers_teacher_id"), table_name="student_teachers")
    op.drop_table("student_teachers")
    op.drop_index(
        op.f("ix_student_administrators_administrator_id"), table_name="student_administrators"
    )
    op.drop_table("student_administrators")
    op.drop_index(op.f("ix_refresh_tokens_user_id"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index(op.f("ix_questions_student_id_course_id_created_at"), table_name="questions")
    op.drop_table("questions")
    op.drop_index(op.f("ix_jobs_user_id"), table_name="jobs")
    op.drop_table("jobs")
    op.drop_index(op.f("ix_assessments_class_id"), table_name="assessments")
    op.drop_table("assessments")
    op.drop_index(op.f("ix_users_class_id"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_courses_subject_id"), table_name="courses")
    op.drop_table("courses")
    op.drop_table("subjects")
    op.drop_table("classes")
    op.execute("DROP EXTENSION IF EXISTS vector")
