"""Database models of Chiron (WBS-1.2). See docs/design/database.md."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    MetaData,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# bge-m3 dense vectors have 1024 dimensions. WBS-4.1 confirms the embedding model.
EMBEDDING_DIMENSIONS = 1024
MAX_SOURCE_BYTES = 20 * 1024 * 1024

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def choice(*values: str, name: str) -> Enum:
    """A text column with a CHECK constraint. No native PostgreSQL enum type."""
    return Enum(*values, name=name, native_enum=False, create_constraint=True, length=32)


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(
        primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )


def created_at() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now())


def user_fk(ondelete: str = "CASCADE", **kwargs) -> Mapped:
    return mapped_column(ForeignKey("users.id", ondelete=ondelete), **kwargs)


ROLE = choice("student", "teacher", "administrator", name="role")
JOB_STATUS = choice("waiting", "running", "done", "failed", name="job_status")


# ---------------------------------------------------------------- portal data


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(100), unique=True)


class SchoolClass(Base):
    __tablename__ = "classes"

    id: Mapped[uuid.UUID] = uuid_pk()
    portal_class_id: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    grade_level: Mapped[int] = mapped_column(SmallInteger)
    section: Mapped[str] = mapped_column(String(16))


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "(password_hash IS NULL) = (activated_at IS NULL)", name="password_with_activation"
        ),
        CheckConstraint("role = 'teacher' OR subject_id IS NULL", name="subject_only_for_teacher"),
        CheckConstraint("role = 'student' OR class_id IS NULL", name="class_only_for_student"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    portal_id: Mapped[str] = mapped_column(String(64), unique=True)
    role: Mapped[str] = mapped_column(ROLE)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    class_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("classes.id", ondelete="SET NULL"), index=True
    )
    subject_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("subjects.id"))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    grades_read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = created_at()


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = uuid_pk()
    portal_course_id: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), index=True)
    grade_level: Mapped[int] = mapped_column(SmallInteger)


class Unit(Base):
    __tablename__ = "units"
    __table_args__ = (UniqueConstraint("course_id", "position"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    portal_unit_id: Mapped[str] = mapped_column(String(64), unique=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(SmallInteger)
    name: Mapped[str] = mapped_column(String(200))


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("unit_id", "position"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    portal_topic_id: Mapped[str] = mapped_column(String(64), unique=True)
    unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(SmallInteger)
    name: Mapped[str] = mapped_column(String(200))


class TeachingAssignment(Base):
    """The teacher teaches the course to the class. A student takes the courses of the class."""

    __tablename__ = "teaching_assignments"

    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True
    )
    class_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("classes.id", ondelete="CASCADE"), primary_key=True
    )
    teacher_id: Mapped[uuid.UUID | None] = user_fk(ondelete="SET NULL", index=True)


class StudentTeacher(Base):
    """The teacher of a student in a course (FR-07, FR-08)."""

    __tablename__ = "student_teachers"

    student_id: Mapped[uuid.UUID] = user_fk(primary_key=True)
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True
    )
    teacher_id: Mapped[uuid.UUID] = user_fk(index=True)


class TeacherAdministrator(Base):
    __tablename__ = "teacher_administrators"

    teacher_id: Mapped[uuid.UUID] = user_fk(primary_key=True)
    administrator_id: Mapped[uuid.UUID] = user_fk(index=True)


class StudentAdministrator(Base):
    __tablename__ = "student_administrators"

    student_id: Mapped[uuid.UUID] = user_fk(primary_key=True)
    administrator_id: Mapped[uuid.UUID] = user_fk(index=True)


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = uuid_pk()
    portal_assessment_id: Mapped[str] = mapped_column(String(64), unique=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    class_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("classes.id", ondelete="CASCADE"), index=True
    )
    teacher_id: Mapped[uuid.UUID | None] = user_fk(ondelete="SET NULL")
    title: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(choice("exam", "quiz", name="assessment_type"))
    date: Mapped[date] = mapped_column(Date)


class AssessmentTopic(Base):
    __tablename__ = "assessment_topics"
    __table_args__ = (CheckConstraint("max_points > 0", name="max_points_positive"),)

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), primary_key=True
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True
    )
    max_points: Mapped[int] = mapped_column(Integer)


class Grade(Base):
    """Points of one student in one topic of one assessment (FR-11, FR-27)."""

    __tablename__ = "grades"
    __table_args__ = (
        ForeignKeyConstraint(
            ["assessment_id", "topic_id"],
            ["assessment_topics.assessment_id", "assessment_topics.topic_id"],
            ondelete="CASCADE",
        ),
        CheckConstraint("points >= 0", name="points_not_negative"),
        Index(None, "student_id", "topic_id"),
    )

    assessment_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    topic_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    student_id: Mapped[uuid.UUID] = user_fk(primary_key=True)
    points: Mapped[int] = mapped_column(Integer)


# ---------------------------------------------------------------- sessions and jobs


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = user_fk(index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = created_at()


class Job(Base):
    """A background job (FR-01). `user_id` is null for system jobs such as the weekly run."""

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID | None] = user_fk(index=True)
    type: Mapped[str] = mapped_column(
        choice(
            "source_processing",
            "summary",
            "quiz",
            "portal_import",
            "weekly_planning",
            name="job_type",
        )
    )
    status: Mapped[str] = mapped_column(JOB_STATUS)
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(Text)
    attempts: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = created_at()
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ---------------------------------------------------------------- sources and answers


class Source(Base):
    __tablename__ = "sources"
    __table_args__ = (
        CheckConstraint(f"size_bytes > 0 AND size_bytes <= {MAX_SOURCE_BYTES}", name="size_limit"),
        Index(None, "student_id", "course_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    student_id: Mapped[uuid.UUID] = user_fk()
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    file_name: Mapped[str] = mapped_column(String(255))
    format: Mapped[str] = mapped_column(choice("pdf", "docx", "pptx", name="source_format"))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    storage_key: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(
        choice("processing", "ready", "failed", name="source_status")
    )
    failure_code: Mapped[str | None] = mapped_column(String(64))
    failure_message: Mapped[str | None] = mapped_column(Text)
    job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("jobs.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = created_at()


class Passage(Base):
    """A chunk of a source with its location and embedding (FR-18)."""

    __tablename__ = "passages"
    __table_args__ = (
        UniqueConstraint("source_id", "position"),
        Index(
            "ix_passages_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    page: Mapped[int | None] = mapped_column(Integer)
    slide: Mapped[int | None] = mapped_column(Integer)
    heading: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIMENSIONS))


class Question(Base):
    """A question and its answer in the course history (FR-18 to FR-20)."""

    __tablename__ = "questions"
    __table_args__ = (Index(None, "student_id", "course_id", "created_at"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    student_id: Mapped[uuid.UUID] = user_fk()
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    has_answer: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = created_at()


class QuestionSource(Base):
    __tablename__ = "question_sources"

    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True
    )


class QuestionCitation(Base):
    __tablename__ = "question_citations"

    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True
    )
    marker: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    passage_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("passages.id", ondelete="CASCADE"), index=True
    )


# ---------------------------------------------------------------- summaries and quizzes


class Summary(Base):
    __tablename__ = "summaries"
    __table_args__ = (Index(None, "student_id", "course_id"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    student_id: Mapped[uuid.UUID] = user_fk()
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    pdf_storage_key: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = created_at()


class SummarySource(Base):
    __tablename__ = "summary_sources"

    summary_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("summaries.id", ondelete="CASCADE"), primary_key=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True
    )


class Quiz(Base):
    __tablename__ = "quizzes"
    __table_args__ = (
        CheckConstraint("score IS NULL OR (score >= 0 AND score <= 100)", name="score_range"),
        Index(None, "student_id", "course_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    student_id: Mapped[uuid.UUID] = user_fk()
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = created_at()


class QuizSource(Base):
    __tablename__ = "quiz_sources"

    quiz_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), primary_key=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    __table_args__ = (UniqueConstraint("quiz_id", "position"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(SmallInteger)
    text: Mapped[str] = mapped_column(Text)
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"), index=True)
    passage_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("passages.id", ondelete="SET NULL")
    )


class QuizOption(Base):
    __tablename__ = "quiz_options"
    __table_args__ = (
        UniqueConstraint("question_id", "position"),
        Index(
            "uq_quiz_options_one_correct",
            "question_id",
            unique=True,
            postgresql_where=text("is_correct"),
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quiz_questions.id", ondelete="CASCADE")
    )
    position: Mapped[int] = mapped_column(SmallInteger)
    text: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean)


class QuizAnswer(Base):
    """The option that the student chose (FR-24). Null means no answer."""

    __tablename__ = "quiz_answers"

    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quiz_questions.id", ondelete="CASCADE"), primary_key=True
    )
    option_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("quiz_options.id", ondelete="CASCADE")
    )


# ---------------------------------------------------------------- study plans


class StudyPlan(Base):
    __tablename__ = "study_plans"
    __table_args__ = (UniqueConstraint("student_id", "week_start"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    student_id: Mapped[uuid.UUID] = user_fk()
    week_start: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        choice("ready", "no_weak_topics", "no_grades", name="study_plan_status")
    )
    created_at: Mapped[datetime] = created_at()


class StudyPlanItem(Base):
    __tablename__ = "study_plan_items"
    __table_args__ = (
        UniqueConstraint("plan_id", "position"),
        CheckConstraint("hours BETWEEN 1 AND 4", name="hours_range"),
        CheckConstraint("success_rate BETWEEN 0 AND 100", name="success_rate_range"),
        CheckConstraint(
            "class_average IS NULL OR class_average BETWEEN 0 AND 100",
            name="class_average_range",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("study_plans.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(SmallInteger)
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"))
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id"))
    reason: Mapped[str] = mapped_column(
        choice("below_threshold", "below_class_average", name="study_plan_reason")
    )
    success_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    class_average: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    hours: Mapped[int] = mapped_column(SmallInteger)


class StudyPlanStep(Base):
    __tablename__ = "study_plan_steps"
    __table_args__ = (UniqueConstraint("item_id", "position"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("study_plan_items.id", ondelete="CASCADE")
    )
    position: Mapped[int] = mapped_column(SmallInteger)
    kind: Mapped[str] = mapped_column(
        choice("review_topic", "practice_questions", name="study_step_kind")
    )
    text: Mapped[str] = mapped_column(Text)


# ---------------------------------------------------------------- AI usage


class TokenUsage(Base):
    """One AI request of a student (FR-35). The dashboards and the monthly limit use it."""

    __tablename__ = "token_usage"
    __table_args__ = (
        CheckConstraint(
            "prompt_tokens >= 0 AND completion_tokens >= 0", name="tokens_not_negative"
        ),
        Index(None, "student_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    student_id: Mapped[uuid.UUID] = user_fk()
    job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("jobs.id", ondelete="SET NULL"))
    purpose: Mapped[str] = mapped_column(
        choice("question", "summary", "quiz", "study_plan", name="token_purpose")
    )
    provider: Mapped[str] = mapped_column(String(64))
    model: Mapped[str] = mapped_column(String(128))
    prompt_tokens: Mapped[int] = mapped_column(Integer)
    completion_tokens: Mapped[int] = mapped_column(Integer)
    cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    created_at: Mapped[datetime] = created_at()
