"""Checks for the mock portal data (WBS-3.1, docs/design/portal-data.md).

The tests prove that the data has the cases the study planner tests need (FR-28, FR-29).
They use their own copy of the weak-topic rule, so they do not depend on the planner code.

Print a report of the cases (from the backend folder):

    uv run python ../tests/backend/test_portal_mock_data.py
"""

import json
from fractions import Fraction
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "backend/app/services/portal/mock_data"
FILES = ["school", "users", "curriculum", "assignments", "grades", "term_update"]

# FR-28 and the study-hour note of FR-29 in the Requirements Spec.
WEAK_BELOW = 60
CLASS_GAP = 15
MIN_GRADED = 5


def load() -> dict[str, dict]:
    return {name: json.loads((DATA_DIR / f"{name}.json").read_text("utf-8")) for name in FILES}


def updated_snapshot(data: dict[str, dict]) -> dict[str, dict]:
    """Return the portal data after the term update (what a later import reads)."""
    update = data["term_update"]
    users = data["users"]["users"] + update["users_added"]
    student_teacher = {
        (r["student_id"], r["course_id"]): r for r in data["assignments"]["student_teacher"]
    }
    for r in update["student_teacher"]:
        student_teacher[(r["student_id"], r["course_id"])] = r
    changed = {
        (g["assessment_id"], g["student_id"], g["topic_id"]): g for g in update["grades_changed"]
    }
    grades = [
        changed.get((g["assessment_id"], g["student_id"], g["topic_id"]), g)
        for g in data["grades"]["grades"]
    ]
    return {
        **data,
        "users": {"users": users},
        "assignments": {
            **data["assignments"],
            "student_teacher": list(student_teacher.values()),
            "student_admin": data["assignments"]["student_admin"] + update["student_admin"],
        },
        "grades": {
            "assessments": data["grades"]["assessments"] + update["assessments_added"],
            "grades": grades + update["grades_added"],
        },
    }


def success_rates(data: dict[str, dict]) -> dict[tuple[str, str], Fraction]:
    """(student, topic) -> success rate in % = 100 x points earned / points possible."""
    max_points = {
        (a["assessment_id"], t["topic_id"]): t["max_points"]
        for a in data["grades"]["assessments"]
        for t in a["topics"]
    }
    totals: dict[tuple[str, str], list[int]] = {}
    for g in data["grades"]["grades"]:
        pm = totals.setdefault((g["student_id"], g["topic_id"]), [0, 0])
        pm[0] += g["points"]
        pm[1] += max_points[(g["assessment_id"], g["topic_id"])]
    return {key: Fraction(100 * p, m) for key, (p, m) in totals.items()}


def analyse(data: dict[str, dict], include_self: bool = True) -> list[dict]:
    """Apply FR-28 to every graded (student, topic).

    include_self=True follows the Requirements Spec: the class average and the count of
    5 graded students include the student. include_self=False is the other reading
    ("5 classmates", average of the classmates); the data must give the same result.
    """
    class_of = {u["portal_id"]: u["class_id"] for u in data["users"]["users"]}
    rates = success_rates(data)
    groups: dict[tuple[str, str], dict[str, Fraction]] = {}
    for (sid, tid), rate in rates.items():
        groups.setdefault((class_of[sid], tid), {})[sid] = rate
    cases = []
    for (cls, tid), members in sorted(groups.items()):
        for sid, rate in sorted(members.items()):
            others = [r for s, r in members.items() if s != sid]
            pool = [*others, rate] if include_self else others
            n = len(pool)
            average = sum(pool, Fraction(0)) / n if n else None
            class_rule = n >= MIN_GRADED
            below = rate < WEAK_BELOW
            far_below = class_rule and average - rate >= CLASS_GAP
            cases.append(
                {
                    "student": sid,
                    "class": cls,
                    "topic": tid,
                    "rate": rate,
                    "graded": len(members),
                    "average": average,
                    "class_rule": class_rule,
                    "below": below,
                    "far_below": far_below,
                    "weak": below or far_below,
                }
            )
    return cases


def hours(rate: Fraction) -> int:
    """Study hours for a topic below 60% (FR-29 note)."""
    if rate >= 50:
        return 1
    if rate >= 40:
        return 2
    if rate >= 30:
        return 3
    return 4


def users_by_role(data: dict[str, dict], role: str) -> list[dict]:
    return [u for u in data["users"]["users"] if u["role"] == role]


def check_references(data: dict[str, dict]) -> None:
    users = {u["portal_id"]: u for u in data["users"]["users"]}
    assert len(users) == len(data["users"]["users"]), "duplicate portal_id"
    assert {u["role"] for u in users.values()} <= {"student", "teacher", "administrator"}
    classes = {c["class_id"] for c in data["school"]["classes"]}
    cur = data["curriculum"]
    courses = {c["course_id"]: c for c in cur["courses"]}
    units = {u["unit_id"]: u for u in cur["units"]}
    topics = {t["topic_id"]: t for t in cur["topics"]}
    assert all(u["course_id"] in courses for u in units.values())
    assert all(t["unit_id"] in units for t in topics.values())
    assert all(c["topic_id"] in topics for c in cur["contents"])
    for u in users.values():
        if u["role"] != "student":
            assert u["class_id"] is None
        elif u["class_id"] is not None:
            assert u["class_id"] in classes

    def role(pid: str) -> str:
        return users[pid]["role"]

    a = data["assignments"]
    teaching = {(r["course_id"], r["class_id"]): r["teacher_id"] for r in a["teaching"]}
    assert len(teaching) == len(a["teaching"]), "two teachers for one course in one class"
    for (course_id, class_id), teacher_id in teaching.items():
        assert course_id in courses and class_id in classes and role(teacher_id) == "teacher"
    subjects: dict[str, set[str]] = {}
    for (course_id, _), teacher_id in teaching.items():
        subjects.setdefault(teacher_id, set()).add(courses[course_id]["subject"])
    assert all(len(s) == 1 for s in subjects.values()), "a teacher teaches one subject (UT-02)"

    st = {(r["student_id"], r["course_id"]): r["teacher_id"] for r in a["student_teacher"]}
    assert len(st) == len(a["student_teacher"])
    for (sid, course_id), teacher_id in st.items():
        assert role(sid) == "student" and role(teacher_id) == "teacher"
        assert courses[course_id]["subject"] in subjects[teacher_id]
    for u in users.values():
        if u["role"] == "student" and u["class_id"] is not None:
            for course_id, class_id in teaching:
                if class_id == u["class_id"]:
                    assert (u["portal_id"], course_id) in st, "student without a teacher"
    ta = {r["teacher_id"]: r["admin_id"] for r in a["teacher_admin"]}
    assert set(ta) == {u["portal_id"] for u in users_by_role(data, "teacher")}
    assert all(role(x) == "administrator" for x in ta.values())
    sa = {r["student_id"]: r["admin_id"] for r in a["student_admin"]}
    assert len(sa) == len(a["student_admin"])
    assert set(sa) == {u["portal_id"] for u in users_by_role(data, "student")}
    assert all(role(x) == "administrator" for x in sa.values())

    max_points = {}
    for x in data["grades"]["assessments"]:
        assert teaching[(x["course_id"], x["class_id"])] == x["teacher_id"]
        for t in x["topics"]:
            assert units[topics[t["topic_id"]]["unit_id"]]["course_id"] == x["course_id"]
            max_points[(x["assessment_id"], t["topic_id"])] = (x["class_id"], t["max_points"])
    keys = set()
    for g in data["grades"]["grades"]:
        key = (g["assessment_id"], g["student_id"], g["topic_id"])
        assert key not in keys, f"duplicate grade {key}"
        keys.add(key)
        class_id, top = max_points[(g["assessment_id"], g["topic_id"])]
        assert users[g["student_id"]]["class_id"] == class_id
        assert 0 <= g["points"] <= top


def test_minimum_sizes() -> None:
    data = load()
    assert len(data["school"]["classes"]) >= 2
    assert len(users_by_role(data, "teacher")) >= 3
    assert len(users_by_role(data, "administrator")) >= 1
    assert len(users_by_role(data, "student")) >= 30


def test_references_resolve() -> None:
    data = load()
    check_references(data)
    check_references(updated_snapshot(data))


def test_topics_below_60_percent_in_every_hour_band() -> None:
    below = [c for c in analyse(load()) if c["below"]]
    assert below
    assert {hours(c["rate"]) for c in below} == {1, 2, 3, 4}


def test_topics_weak_only_by_class_rule() -> None:
    cases = [c for c in analyse(load()) if c["far_below"] and not c["below"]]
    assert cases, "need a topic at 60% or more that is 15+ points under the class average"


def test_topic_with_fewer_than_5_graded_students() -> None:
    small = [c for c in analyse(load()) if 0 < c["graded"] < MIN_GRADED]
    assert small
    # One of them would be weak if the class rule applied, so the case really tests the rule.
    tricky = [c for c in small if not c["below"] and c["average"] - c["rate"] >= CLASS_GAP]
    assert tricky and not any(c["weak"] for c in tricky)


def test_exactly_60_percent_is_not_weak() -> None:
    cases = [c for c in analyse(load()) if c["rate"] == WEAK_BELOW]
    assert cases and not any(c["weak"] for c in cases)


def test_student_without_weak_topics() -> None:
    data = load()
    weak = {c["student"] for c in analyse(data) if c["weak"]}
    students = {u["portal_id"] for u in users_by_role(data, "student")}
    assert students - weak


def test_result_does_not_depend_on_class_average_reading() -> None:
    for data in (load(), updated_snapshot(load())):
        with_self = {(c["student"], c["topic"]) for c in analyse(data, True) if c["weak"]}
        without = {(c["student"], c["topic"]) for c in analyse(data, False) if c["weak"]}
        assert with_self == without
        assert not any(c["graded"] == MIN_GRADED for c in analyse(data))


def test_elif_matches_scenario_sc04() -> None:
    weak = [c for c in analyse(load()) if c["weak"] and c["student"] == "OGR-1001"]
    assert sum(c["below"] for c in weak) == 2
    by_class = [c for c in weak if not c["below"]]
    assert len(by_class) == 1 and by_class[0]["rate"] == 70
    assert 86 <= by_class[0]["average"] <= 90  # SC-04: "her class average is 88%"


def test_term_update() -> None:
    data = load()
    update = data["term_update"]
    base_ids = {u["portal_id"] for u in data["users"]["users"]}
    new_ids = {u["portal_id"] for u in update["users_added"]}
    assert new_ids and not new_ids & base_ids
    # UC-03 A1: a new student without a class. UC-08 E1: new students have no grades.
    assert any(u["class_id"] is None for u in update["users_added"])
    graded = {g["student_id"] for g in data["grades"]["grades"] + update["grades_added"]}
    assert not new_ids & graded
    # FR-12: the update changes an assignment of an existing student; the import must ignore it.
    base_st = {
        (r["student_id"], r["course_id"]): r["teacher_id"]
        for r in data["assignments"]["student_teacher"]
    }
    moved = [
        r
        for r in update["student_teacher"]
        if r["student_id"] in base_ids
        and base_st[(r["student_id"], r["course_id"])] != r["teacher_id"]
    ]
    assert len(moved) == 1
    # FR-11: a changed grade exists in the base data with another value.
    base_points = {
        (g["assessment_id"], g["student_id"], g["topic_id"]): g["points"]
        for g in data["grades"]["grades"]
    }
    for g in update["grades_changed"]:
        key = (g["assessment_id"], g["student_id"], g["topic_id"])
        assert key in base_points and base_points[key] != g["points"]


def test_files_match_the_generator() -> None:
    from app.services.portal.mock_data import generate_mock_data as gen

    for name, content in gen.build().items():
        assert (DATA_DIR / name).read_text("utf-8") == gen.dump(content), f"{name} is out of date"


def report() -> None:
    data = load()
    cases = analyse(data)
    names = {u["portal_id"]: f"{u['first_name']} {u['last_name']}" for u in data["users"]["users"]}
    topic_names = {t["topic_id"]: t["name"] for t in data["curriculum"]["topics"]}

    def line(c: dict) -> str:
        avg = f"{float(c['average']):.1f}" if c["average"] is not None else "-"
        return (
            f"  {c['student']} {names[c['student']]:<16} {c['class']} {c['topic']:<12} "
            f"{topic_names[c['topic']][:38]:<38} rate {float(c['rate']):5.1f}  avg {avg:>5}  "
            f"graded {c['graded']:>2}"
        )

    counts = {r: len(users_by_role(data, r)) for r in ("student", "teacher", "administrator")}
    print(
        f"classes {len(data['school']['classes'])}, students {counts['student']}, "
        f"teachers {counts['teacher']}, administrators {counts['administrator']}"
    )
    cur = data["curriculum"]
    graded_topics = {t["topic_id"] for a in data["grades"]["assessments"] for t in a["topics"]}
    print(
        f"courses {len(cur['courses'])}, units {len(cur['units'])}, topics {len(cur['topics'])} "
        f"({len(graded_topics)} graded), contents {len(cur['contents'])}"
    )
    print(
        f"assessments {len(data['grades']['assessments'])}, grade rows "
        f"{len(data['grades']['grades'])}, graded (student, topic) pairs {len(cases)}"
    )
    below = [c for c in cases if c["below"]]
    print(f"\nWeak: below 60% ({len(below)})")
    for h in (1, 2, 3, 4):
        print(f" {h} hour(s):")
        for c in below:
            if hours(c["rate"]) == h:
                print(line(c))
    print("\nWeak only by the class rule (60% or more, 15+ points under the class average)")
    for c in cases:
        if c["far_below"] and not c["below"]:
            print(line(c))
    print("\nFewer than 5 graded students in the class (class rule cannot apply)")
    for c in cases:
        if c["graded"] < MIN_GRADED:
            print(line(c) + ("  WEAK" if c["weak"] else "  not weak"))
    print("\nBoundary: exactly 60%")
    for c in cases:
        if c["rate"] == WEAK_BELOW:
            print(line(c) + ("  WEAK" if c["weak"] else "  not weak"))
    weak_students = {c["student"] for c in cases if c["weak"]}
    none = sorted({u["portal_id"] for u in users_by_role(data, "student")} - weak_students)
    print(f"\nStudents with no weak topic ({len(none)}): {', '.join(none)}")
    updated = analyse(updated_snapshot(data))
    before = {(c["student"], c["topic"]) for c in cases if c["weak"]}
    after = {(c["student"], c["topic"]) for c in updated if c["weak"]}
    print(f"\nAfter term_update.json: weak pairs {len(before)} -> {len(after)}")
    print(f"  no longer weak: {sorted(before - after)}")
    print(f"  newly weak: {sorted(after - before)}")


if __name__ == "__main__":
    report()
