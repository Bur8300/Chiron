"""Generate the mock EBA portal data (WBS-3.1).

Run from the backend folder:

    uv run python -m app.services.portal.mock_data.generate_mock_data

The script uses a fixed random seed, so every run writes the same files.
It writes the JSON files next to this script. The design is in docs/design/portal-data.md.

All people, IDs and grades in this data are made up. Do not add real student data (NFR-05).
"""

import json
import random
from pathlib import Path

SEED = 411
AS_OF = "2026-11-12"
DATA_DIR = Path(__file__).resolve().parent

# Weak-topic rule of FR-28. The generator only uses it to keep grades away from the limits.
WEAK_BELOW = 60.0
CLASS_GAP = 15.0
MIN_GRADED = 5
# No success rate or class gap is closer than this to a limit, except the cases in BOUNDARY.
# The weak-topic result then does not depend on rounding or on small reading differences.
MARGIN = 2.0
# Study-hour bands of FR-29 (50-59% 1 hour, 40-49% 2, 30-39% 3, below 30% 4).
# No success rate is closer than BAND_MARGIN to a band edge.
BAND_EDGES = (30.0, 40.0, 50.0)
BAND_MARGIN = 1.0

SCHOOL = {
    "school_id": "OKUL-01",
    "name": "Chiron Deneme Anadolu Lisesi",
    "school_year": "2026-2027",
    "term": 1,
}

CLASSES = [
    {"class_id": "10-A", "name": "10-A", "grade_level": 10, "section": "A"},
    {"class_id": "10-B", "name": "10-B", "grade_level": 10, "section": "B"},
]

# Course -> units -> topics. Names follow the 10th-grade MEB curriculum headings.
CURRICULUM = [
    (
        "KIM10",
        "Kimya 10",
        "Kimya",
        [
            (
                "Kimyanın Temel Kanunları ve Kimyasal Hesaplamalar",
                [
                    "Kimyanın Temel Kanunları",
                    "Mol Kavramı",
                    "Kimyasal Tepkimeler ve Denklemler",
                    "Kimyasal Tepkimelerde Hesaplamalar",
                ],
            ),
            ("Karışımlar", ["Homojen ve Heterojen Karışımlar", "Ayırma ve Saflaştırma Teknikleri"]),
            (
                "Asitler, Bazlar ve Tuzlar",
                [
                    "Asitler ve Bazlar",
                    "Asitlerin ve Bazların Tepkimeleri",
                    "Hayatımızda Asitler ve Bazlar",
                    "Tuzlar",
                ],
            ),
            ("Kimya Her Yerde", ["Yaygın Günlük Hayat Kimyasalları", "Gıdalar"]),
        ],
    ),
    (
        "MAT10",
        "Matematik 10",
        "Matematik",
        [
            ("Sayma ve Olasılık", ["Sıralama ve Seçme", "Basit Olayların Olasılıkları"]),
            (
                "Fonksiyonlar",
                [
                    "Fonksiyon Kavramı ve Gösterimi",
                    "İki Fonksiyonun Bileşkesi ve Bir Fonksiyonun Tersi",
                ],
            ),
            (
                "Polinomlar",
                [
                    "Polinom Kavramı ve Polinomlarla İşlemler",
                    "Polinomlarda Çarpanlara Ayırma",
                    "Polinom İçeren Rasyonel İfadelerin Sadeleştirilmesi",
                ],
            ),
            ("İkinci Dereceden Denklemler", ["İkinci Dereceden Bir Bilinmeyenli Denklemler"]),
            (
                "Dörtgenler ve Çokgenler",
                ["Çokgenler", "Dörtgenler ve Özellikleri", "Özel Dörtgenler"],
            ),
            ("Uzay Geometri", ["Katı Cisimler"]),
        ],
    ),
    (
        "FIZ10",
        "Fizik 10",
        "Fizik",
        [
            (
                "Elektrik ve Manyetizma",
                [
                    "Elektrik Akımı, Potansiyel Farkı ve Direnç",
                    "Elektrik Devreleri",
                    "Mıknatıs ve Manyetik Alan",
                    "Akım ve Manyetik Alan",
                ],
            ),
            ("Basınç ve Kaldırma Kuvveti", ["Basınç", "Kaldırma Kuvveti"]),
            (
                "Dalgalar",
                [
                    "Dalgaların Temel Özellikleri",
                    "Yay Dalgası",
                    "Su Dalgası",
                    "Ses Dalgası",
                    "Deprem Dalgası",
                ],
            ),
            (
                "Optik",
                [
                    "Aydınlanma",
                    "Gölge",
                    "Yansıma ve Düzlem Ayna",
                    "Küresel Aynalar",
                    "Kırılma",
                    "Mercekler",
                    "Prizmalar ve Renk",
                ],
            ),
        ],
    ),
]

# Staff. Murat Ercan and Ayşe Tunç match the personas P-02 and P-03 of the Requirements Spec.
TEACHERS = [
    ("OGT-2001", "Murat", "Ercan"),
    ("OGT-2002", "Gülşen", "Tekin"),
    ("OGT-2003", "Hakan", "Özer"),
    ("OGT-2004", "Nurcan", "Bulut"),
]
ADMINS = [
    ("YON-3001", "Ayşe", "Tunç"),
    ("YON-3002", "Kemal", "Ersoy"),
]

# Teacher -> course and class. Each teacher teaches one subject.
TEACHING = [
    ("OGT-2001", "KIM10", "10-A"),
    ("OGT-2002", "KIM10", "10-B"),
    ("OGT-2003", "MAT10", "10-A"),
    ("OGT-2003", "MAT10", "10-B"),
    ("OGT-2004", "FIZ10", "10-A"),
    ("OGT-2004", "FIZ10", "10-B"),
]
TEACHER_ADMIN = [
    ("OGT-2001", "YON-3001"),
    ("OGT-2002", "YON-3001"),
    ("OGT-2003", "YON-3002"),
    ("OGT-2004", "YON-3001"),
]
CLASS_ADMIN = {"10-A": "YON-3001", "10-B": "YON-3002"}

STUDENTS_PER_CLASS = 15
# Elif matches the persona P-01. Her grades match scenario SC-04.
FIXED_STUDENTS = {"OGR-1001": ("Elif", "Aksoy")}

FEMALE_NAMES = [
    "Zeynep", "Defne", "Ecrin", "Azra", "Nehir", "Eylül", "Ela", "Asya", "Duru", "Ada",
    "Melis", "Ceren", "Yağmur", "Irmak", "Nisa", "Berra", "İpek", "Selin", "Buse", "Derin",
]  # fmt: skip
MALE_NAMES = [
    "Yusuf", "Eymen", "Ömer", "Mustafa", "Emir", "Kerem", "Alp", "Aras", "Mert", "Arda",
    "Efe", "Can", "Deniz", "Kaan", "Berk", "Onur", "Tuna", "Batuhan", "Barış", "Yiğit",
]  # fmt: skip
SURNAMES = [
    "Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Yıldız", "Yıldırım", "Öztürk", "Aydın",
    "Özdemir", "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özkan",
    "Şimşek", "Erdem", "Korkmaz", "Güneş", "Acar", "Keskin", "Uçar", "Taş", "Erdoğan",
    "Bozkurt", "Karaca", "Çakır", "Sarı", "Aktaş", "Kaplan", "Avcı", "Tuncer",
]  # fmt: skip

# Assessments: (course, code, title, type, date per class, [(topic, max points)]).
ASSESSMENTS = [
    ("KIM10", "KS1", "1. Kısa Sınav", "quiz", {"10-A": "2026-10-09", "10-B": "2026-10-08"},
     [("KIM10-U1-T1", 15), ("KIM10-U1-T2", 15)]),
    ("KIM10", "Y1", "1. Yazılı Sınav", "exam", {"10-A": "2026-11-04", "10-B": "2026-11-04"},
     [("KIM10-U1-T1", 25), ("KIM10-U1-T2", 25), ("KIM10-U1-T3", 25), ("KIM10-U1-T4", 25)]),
    ("KIM10", "KS2", "2. Kısa Sınav", "quiz", {"10-A": "2026-11-11", "10-B": "2026-11-11"},
     [("KIM10-U2-T1", 20)]),
    ("MAT10", "KS1", "1. Kısa Sınav", "quiz", {"10-A": "2026-10-06", "10-B": "2026-10-07"},
     [("MAT10-U1-T1", 20)]),
    ("MAT10", "Y1", "1. Yazılı Sınav", "exam", {"10-A": "2026-11-03", "10-B": "2026-11-03"},
     [("MAT10-U1-T1", 40), ("MAT10-U1-T2", 30), ("MAT10-U2-T1", 30)]),
    ("FIZ10", "KS1", "1. Kısa Sınav", "quiz", {"10-A": "2026-10-14", "10-B": "2026-10-15"},
     [("FIZ10-U1-T1", 10)]),
    ("FIZ10", "Y1", "1. Yazılı Sınav", "exam", {"10-A": "2026-11-05", "10-B": "2026-11-05"},
     [("FIZ10-U1-T1", 40), ("FIZ10-U1-T2", 40), ("FIZ10-U1-T3", 20)]),
]  # fmt: skip

# Mean success rate (%) of each class in each graded topic.
TOPIC_MEAN = {
    ("10-A", "KIM10-U1-T1"): 90, ("10-B", "KIM10-U1-T1"): 78,
    ("10-A", "KIM10-U1-T2"): 74, ("10-B", "KIM10-U1-T2"): 70,
    ("10-A", "KIM10-U1-T3"): 78, ("10-B", "KIM10-U1-T3"): 75,
    ("10-A", "KIM10-U1-T4"): 66, ("10-B", "KIM10-U1-T4"): 64,
    ("10-A", "KIM10-U2-T1"): 84, ("10-B", "KIM10-U2-T1"): 90,
    ("10-A", "MAT10-U1-T1"): 76, ("10-B", "MAT10-U1-T1"): 72,
    ("10-A", "MAT10-U1-T2"): 70, ("10-B", "MAT10-U1-T2"): 68,
    ("10-A", "MAT10-U2-T1"): 88, ("10-B", "MAT10-U2-T1"): 80,
    ("10-A", "FIZ10-U1-T1"): 77, ("10-B", "FIZ10-U1-T1"): 79,
    ("10-A", "FIZ10-U1-T2"): 72, ("10-B", "FIZ10-U1-T2"): 74,
    ("10-A", "FIZ10-U1-T3"): 86, ("10-B", "FIZ10-U1-T3"): 88,
    ("10-A", "FIZ10-U1-T4"): 75,
}  # fmt: skip

# Planner test cases (FR-28, FR-29): (student, topic) -> success rate (%) set by hand.
DESIGNED = {
    # SC-04: Elif has two topics below 60% and one 70% topic under a class average of about 88%.
    ("OGR-1001", "KIM10-U1-T1"): 70,  # class rule: 70% and far below the class average
    ("OGR-1001", "KIM10-U1-T2"): 45,  # below 60%: 40-49% band
    ("OGR-1001", "KIM10-U1-T4"): 56,  # below 60%: 50-59% band
    ("OGR-1001", "KIM10-U1-T3"): 80,
    ("OGR-1001", "KIM10-U2-T1"): 85,
    ("OGR-1004", "FIZ10-U1-T2"): 35,  # 30-39% band
    ("OGR-1004", "MAT10-U1-T2"): 25,  # below 30% band
    ("OGR-1007", "KIM10-U1-T4"): 60,  # boundary: exactly 60% is not weak
    ("OGR-1009", "MAT10-U2-T1"): 67,  # class rule
    ("OGR-1016", "KIM10-U1-T1"): 48,  # 40-49% band; corrected upward in term_update.json
    ("OGR-1016", "KIM10-U1-T2"): 38,  # 30-39% band
    ("OGR-1020", "FIZ10-U1-T3"): 65,  # class rule
    ("OGR-1029", "MAT10-U1-T1"): 28,  # below 30% band
    # 10-B, 2. Kısa Sınav: only 4 students are graded, so the class rule cannot apply.
    # OGR-1027 is 70%, about 18 points under the other three, and must not be weak.
    ("OGR-1018", "KIM10-U2-T1"): 95,
    ("OGR-1022", "KIM10-U2-T1"): 90,
    ("OGR-1025", "KIM10-U2-T1"): 95,
    ("OGR-1027", "KIM10-U2-T1"): 70,
}
# Cases that stay exactly on a limit. The margin repair does not change them.
BOUNDARY = {("OGR-1007", "KIM10-U1-T4")}
# Ability offsets (points) set by hand. OGR-1011 is a strong student with no weak topics.
ABILITY = {
    ("OGR-1001", "KIM10"): 0, ("OGR-1001", "MAT10"): 8, ("OGR-1001", "FIZ10"): 8,
    ("OGR-1011", "KIM10"): 14, ("OGR-1011", "MAT10"): 14, ("OGR-1011", "FIZ10"): 14,
}  # fmt: skip
# Only these students have a grade in the assessment (the teacher has not entered the rest).
GRADED_ONLY = {"KIM10-10B-KS2": ["OGR-1018", "OGR-1022", "OGR-1025", "OGR-1027"]}
# The student missed the assessment and has no grade in it.
ABSENT = {("OGR-1012", "FIZ10-10A-KS1"), ("OGR-1013", "KIM10-10A-KS2")}

# Later import (FR-12, UC-02 A2): what the portal shows after setup.
NEW_STUDENTS = [
    ("OGR-1031", "10-A"),  # joins 10-A during the term
    ("OGR-1032", None),  # transfer student, the school has not given a class yet
]
# The portal moves an existing student to another chemistry teacher.
# The later import must not apply this change (FR-12).
PORTAL_MOVE = ("OGR-1005", "KIM10", "OGT-2002")
# Exam re-check: a corrected grade (FR-11).
GRADE_CHANGE = ("KIM10-10B-Y1", "OGR-1016", "KIM10-U1-T1", 20)
NEW_ASSESSMENT = (
    "FIZ10", "KS2", "2. Kısa Sınav", "quiz", {"10-A": "2026-11-18"}, [("FIZ10-U1-T4", 20)],
)  # fmt: skip


def assessment_id(course_id: str, class_id: str, code: str) -> str:
    return f"{course_id}-{class_id.replace('-', '')}-{code}"


def build_curriculum() -> dict:
    courses, units, topics, contents = [], [], [], []
    for course_id, name, subject, course_units in CURRICULUM:
        courses.append(
            {"course_id": course_id, "name": name, "subject": subject, "grade_level": 10}
        )
        for u, (unit_name, topic_names) in enumerate(course_units, start=1):
            unit_id = f"{course_id}-U{u}"
            units.append(
                {"unit_id": unit_id, "course_id": course_id, "position": u, "name": unit_name}
            )
            for t, topic_name in enumerate(topic_names, start=1):
                topic_id = f"{unit_id}-T{t}"
                topics.append(
                    {"topic_id": topic_id, "unit_id": unit_id, "position": t, "name": topic_name}
                )
                items = [("video", "Konu Anlatımı"), ("document", "Çalışma Yaprağı")]
                if u == 1:
                    items.append(("practice_test", "Konu Tarama Testi"))
                for c, (kind, label) in enumerate(items, start=1):
                    content_id = f"{topic_id}-C{c}"
                    contents.append(
                        {
                            "content_id": content_id,
                            "topic_id": topic_id,
                            "title": f"{topic_name} - {label}",
                            "type": kind,
                            "url": f"https://portal.example/icerik/{content_id}",
                        }
                    )
    return {"courses": courses, "units": units, "topics": topics, "contents": contents}


def build_people(rng: random.Random) -> tuple[list, list]:
    """Return (students, staff) as user records. New students for the later import are last."""
    fixed_surnames = {last for _, _, last in TEACHERS + ADMINS}
    fixed_surnames |= {last for _, last in FIXED_STUDENTS.values()}
    first_names = [n for n in FEMALE_NAMES + MALE_NAMES if n not in {"Elif"}]
    surnames = [s for s in SURNAMES if s not in fixed_surnames]
    rng.shuffle(first_names)
    rng.shuffle(surnames)

    students = []
    count = 2 * STUDENTS_PER_CLASS + len(NEW_STUDENTS)
    new_classes = dict(NEW_STUDENTS)
    for i in range(count):
        portal_id = f"OGR-{1001 + i}"
        if portal_id in FIXED_STUDENTS:
            first, last = FIXED_STUDENTS[portal_id]
        else:
            first, last = first_names.pop(), surnames.pop()
        if portal_id in new_classes:
            class_id = new_classes[portal_id]
        else:
            class_id = CLASSES[i // STUDENTS_PER_CLASS]["class_id"]
        students.append(
            {
                "portal_id": portal_id,
                "role": "student",
                "first_name": first,
                "last_name": last,
                "class_id": class_id,
            }
        )
    staff = [
        {"portal_id": p, "role": "teacher", "first_name": f, "last_name": la, "class_id": None}
        for p, f, la in TEACHERS
    ]
    staff += [
        {
            "portal_id": p,
            "role": "administrator",
            "first_name": f,
            "last_name": la,
            "class_id": None,
        }
        for p, f, la in ADMINS
    ]
    return students, staff


def student_assignments(students: list) -> tuple[list, list]:
    student_teacher, student_admin = [], []
    for s in students:
        if s["class_id"] is None:
            continue
        for teacher_id, course_id, class_id in TEACHING:
            if class_id == s["class_id"]:
                student_teacher.append(
                    {"student_id": s["portal_id"], "course_id": course_id, "teacher_id": teacher_id}
                )
    for s in students:
        admin = CLASS_ADMIN.get(s["class_id"], "YON-3002")
        student_admin.append({"student_id": s["portal_id"], "admin_id": admin})
    return student_teacher, student_admin


def build_assessments(specs: list) -> list:
    teacher_of = {(course, cls): t for t, course, cls in TEACHING}
    result = []
    for course_id, code, title, kind, dates, topics in specs:
        for class_id, date in dates.items():
            result.append(
                {
                    "assessment_id": assessment_id(course_id, class_id, code),
                    "course_id": course_id,
                    "class_id": class_id,
                    "teacher_id": teacher_of[(course_id, class_id)],
                    "title": title,
                    "type": kind,
                    "date": date,
                    "topics": [{"topic_id": t, "max_points": m} for t, m in topics],
                }
            )
    return result


def split_points(rate: float, maxima: list[int]) -> list[int]:
    """Split a success rate into whole points for each assessment of a topic."""
    total = int(rate * sum(maxima) / 100 + 0.5)
    parts, left, left_max = [], total, sum(maxima)
    for m in maxima[:-1]:
        p = min(m, int(left * m / left_max + 0.5))
        parts.append(p)
        left -= p
        left_max -= m
    parts.append(max(0, min(maxima[-1], left)))
    return parts


def build_ability(rng: random.Random, students: list) -> dict[tuple[str, str], float]:
    """Return an ability offset (points) for each student in each course."""
    ability = {}
    for s in students:
        for course_id, *_ in CURRICULUM:
            value = rng.gauss(0, 8)
            ability[(s["portal_id"], course_id)] = ABILITY.get((s["portal_id"], course_id), value)
    return ability


def build_grades(
    rng: random.Random, students: list, assessments: list, ability: dict[tuple[str, str], float]
) -> list:
    """Create grade rows from class means, ability and noise, then add the designed cases."""
    class_of = {s["portal_id"]: s["class_id"] for s in students}

    # (student, topic) -> list of (assessment, max points), in date order.
    taken: dict[tuple[str, str], list[tuple[str, int]]] = {}
    for a in sorted(assessments, key=lambda a: (a["date"], a["assessment_id"])):
        graded = GRADED_ONLY.get(a["assessment_id"])
        for s in students:
            sid = s["portal_id"]
            if class_of[sid] != a["class_id"] or (sid, a["assessment_id"]) in ABSENT:
                continue
            if graded is not None and sid not in graded:
                continue
            for t in a["topics"]:
                taken.setdefault((sid, t["topic_id"]), []).append(
                    (a["assessment_id"], t["max_points"])
                )

    grades = []
    for (sid, topic_id), parts in sorted(taken.items()):
        course_id = topic_id.split("-")[0]
        noise = rng.gauss(0, 6)
        rate = TOPIC_MEAN[(class_of[sid], topic_id)] + ability[(sid, course_id)] + noise
        rate = DESIGNED.get((sid, topic_id), max(5.0, min(100.0, rate)))
        points = split_points(rate, [m for _, m in parts])
        for (aid, _), p in zip(parts, points, strict=True):
            grades.append(
                {"assessment_id": aid, "student_id": sid, "topic_id": topic_id, "points": p}
            )
    return grades


def find_borderline(grades: list, assessments: list, class_of: dict) -> list:
    """Return (student, topic, direction) for rates or class gaps too close to a limit."""
    max_of = {(a["assessment_id"], t["topic_id"]): t["max_points"] for a in assessments
              for t in a["topics"]}  # fmt: skip
    totals: dict[tuple[str, str], list[int]] = {}
    for g in grades:
        pm = totals.setdefault((g["student_id"], g["topic_id"]), [0, 0])
        pm[0] += g["points"]
        pm[1] += max_of[(g["assessment_id"], g["topic_id"])]
    groups: dict[tuple[str, str], list[tuple[str, float]]] = {}
    for (sid, topic_id), (p, m) in sorted(totals.items()):
        groups.setdefault((class_of[sid], topic_id), []).append((sid, 100 * p / m))

    issues = []
    for (_, topic_id), entries in sorted(groups.items()):
        n = len(entries)
        if n == MIN_GRADED:
            raise ValueError(f"{topic_id}: exactly {MIN_GRADED} graded students is ambiguous")
        total = sum(r for _, r in entries)
        for sid, r in entries:
            if (sid, topic_id) in BOUNDARY:
                continue
            if abs(r - WEAK_BELOW) < MARGIN:
                issues.append((sid, topic_id, -1 if r < WEAK_BELOW else 1))
                continue
            if any(abs(r - edge) < BAND_MARGIN for edge in BAND_EDGES):
                issues.append((sid, topic_id, -1))
                continue
            if r < WEAK_BELOW or n < MIN_GRADED:
                continue
            # Two readings of "class average": with and without the student.
            gap_with = total / n - r
            gap_without = (total - r) / (n - 1) - r
            gaps = [gap_with, gap_without]
            if any(abs(g - CLASS_GAP) < MARGIN for g in gaps) or (gap_with >= CLASS_GAP) != (
                gap_without >= CLASS_GAP
            ):
                # Always move up. A move down can reach the 60% limit and bounce back.
                issues.append((sid, topic_id, 1))
    return issues


def apply_change(grades: list, change: tuple[str, str, str, int]) -> list:
    """Return a copy of the grades with one grade replaced."""
    aid, sid, tid, points = change
    result = [dict(g) for g in grades]
    for g in result:
        if (g["assessment_id"], g["student_id"], g["topic_id"]) == (aid, sid, tid):
            g["points"] = points
    return result


def repair(
    grades: list,
    assessments: list,
    class_of: dict,
    fixed: set | None = None,
    change: tuple[str, str, str, int] | None = None,
) -> None:
    """Move grades one point at a time until no case is close to a limit.

    Rows whose (assessment, student, topic) key is in `fixed` are not changed.
    With `change`, the grades must also stay clear of the limits after that grade change.
    """
    max_of = {(a["assessment_id"], t["topic_id"]): t["max_points"] for a in assessments
              for t in a["topics"]}  # fmt: skip
    fixed = set(fixed or ())
    if change is not None:
        fixed.add(change[:3])
    for _ in range(1000):
        issues = find_borderline(grades, assessments, class_of)
        if change is not None:
            issues += find_borderline(apply_change(grades, change), assessments, class_of)
        issues = list(dict.fromkeys(issues))
        if not issues:
            return
        for sid, topic_id, direction in issues:
            rows = [
                g
                for g in grades
                if g["student_id"] == sid
                and g["topic_id"] == topic_id
                and (g["assessment_id"], sid, topic_id) not in fixed
                and 0 <= g["points"] + direction <= max_of[(g["assessment_id"], topic_id)]
            ]
            if not rows:
                raise ValueError(f"cannot move {sid} {topic_id} away from a limit")
            row = max(rows, key=lambda g: max_of[(g["assessment_id"], topic_id)])
            row["points"] += direction
    raise ValueError("margin repair did not finish")


def build() -> dict[str, dict]:
    """Return the content of every data file, by file name."""
    rng = random.Random(SEED)
    curriculum = build_curriculum()
    all_students, staff = build_people(rng)
    new_ids = {sid for sid, _ in NEW_STUDENTS}
    students = [s for s in all_students if s["portal_id"] not in new_ids]
    new_students = [s for s in all_students if s["portal_id"] in new_ids]

    student_teacher, student_admin = student_assignments(students)
    assessments = build_assessments(ASSESSMENTS)
    ability = build_ability(rng, students)
    grades = build_grades(rng, students, assessments, ability)
    class_of = {s["portal_id"]: s["class_id"] for s in all_students}
    repair(grades, assessments, class_of, change=GRADE_CHANGE)

    # Later import: new students, one portal-side move, a corrected grade and a new quiz.
    new_teacher, new_admin = student_assignments(new_students)
    student_id, course_id, teacher_id = PORTAL_MOVE
    new_teacher.append({"student_id": student_id, "course_id": course_id, "teacher_id": teacher_id})
    new_assessments = build_assessments([NEW_ASSESSMENT])
    new_grades = build_grades(rng, students, new_assessments, ability)
    aid, sid, tid, points = GRADE_CHANGE
    changed = [{"assessment_id": aid, "student_id": sid, "topic_id": tid, "points": points}]
    updated = apply_change(grades, GRADE_CHANGE)
    old_keys = {(g["assessment_id"], g["student_id"], g["topic_id"]) for g in updated}
    repair(updated + new_grades, assessments + new_assessments, class_of, fixed=old_keys)

    dataset = {
        "generator": "generate_mock_data.py",
        "seed": SEED,
        "as_of": AS_OF,
        "note": "Fake data for development and tests. No real people. Do not add real data.",
    }
    return {
        "school.json": {"dataset": dataset, "school": SCHOOL, "classes": CLASSES},
        "users.json": {"users": students + staff},
        "curriculum.json": curriculum,
        "assignments.json": {
            "teaching": [{"teacher_id": t, "course_id": c, "class_id": k} for t, c, k in TEACHING],
            "student_teacher": student_teacher,
            "teacher_admin": [{"teacher_id": t, "admin_id": a} for t, a in TEACHER_ADMIN],
            "student_admin": student_admin,
        },
        "grades.json": {"assessments": assessments, "grades": grades},
        "term_update.json": {
            "users_added": new_students,
            "student_teacher": new_teacher,
            "student_admin": new_admin,
            "assessments_added": new_assessments,
            "grades_added": new_grades,
            "grades_changed": changed,
        },
    }


def dump(data: dict) -> str:
    """Write JSON with one list item on each line, so that the files are easy to read and diff."""
    lines = ["{"]
    for i, (key, value) in enumerate(data.items()):
        comma = "," if i < len(data) - 1 else ""
        if isinstance(value, list) and value:
            lines.append(f"  {json.dumps(key)}: [")
            for j, item in enumerate(value):
                item_comma = "," if j < len(value) - 1 else ""
                lines.append(f"    {json.dumps(item, ensure_ascii=False)}{item_comma}")
            lines.append(f"  ]{comma}")
        else:
            lines.append(f"  {json.dumps(key)}: {json.dumps(value, ensure_ascii=False)}{comma}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    for name, data in build().items():
        (DATA_DIR / name).write_text(dump(data), encoding="utf-8")
        print(f"wrote {name}")


if __name__ == "__main__":
    main()
