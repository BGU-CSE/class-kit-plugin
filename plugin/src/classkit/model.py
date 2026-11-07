"""Locating and loading a course tree.

Layout, as created by `classkit scaffold course`:

    course/
      course.yaml
      LOG.md                the course log (D-036) — not loaded here; see log.py
      syllabus/syllabus.md
      units/
        01-slug/
          unit.md
          sessions/01.md 02.md ...
          in-class.md
      assessments/
        items/ quizzes/ homework/ exams/
        homework/HW01.md ...           a homework: its plan, its items, its approval
        item-classes.yaml              the homework's item classes      } created by
        homework-defaults.yaml         the teacher's homework defaults  } `scaffold homework`
        homework-document.yaml         how the homework documents look  } (all optional)
      materials/
      policies/
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .frontmatter import load, load_yaml


@dataclass
class Doc:
    """One parsed Markdown document: its front matter plus its prose body."""

    path: Path
    data: dict
    body: str = ""

    @property
    def id(self) -> str:
        return str(self.data.get("id", f"<no id: {self.path.name}>"))

    @property
    def accepted(self) -> list[dict]:
        """The teacher's accepted exceptions for this file (D-037): ``[{rule, reason}]``.

        Malformed entries are dropped here and reported by the schema layer instead.
        """
        entries = self.data.get("accepted") or []
        if not isinstance(entries, list):
            return []
        return [e for e in entries if isinstance(e, dict) and isinstance(e.get("rule"), str)]


@dataclass
class Unit:
    doc: Doc
    directory: Path
    sessions: list[Doc] = field(default_factory=list)
    in_class: Doc | None = None

    @property
    def id(self) -> str:
        return self.doc.id

    @property
    def objectives(self) -> list[dict]:
        return self.doc.data.get("objectives") or []

    def goals(self) -> list[dict]:
        """Every goal from every study session in this unit, in order."""
        return [g for s in self.sessions for g in (s.data.get("goals") or [])]


@dataclass
class Course:
    root: Path
    config: dict
    methodology: dict
    time_constants: dict
    #: The methodology file in use: the course's own (`course/methodologies/`) or the framework's.
    methodology_file: Path | None = None
    #: `syllabus/syllabus.md` — the course-level top layer (D-021). `None` when the file
    #: does not exist: the syllabus is scaffolded, but a course tree can be edited by hand
    #: and the loader reports what is there rather than assuming.
    syllabus: Doc | None = None
    units: list[Unit] = field(default_factory=list)
    items: list[Doc] = field(default_factory=list)
    #: `assessments/homework/HW*.md`, by id (homework module). Homework is optional (HW-D13).
    homework: list[Doc] = field(default_factory=list)
    #: the homework's configuration files, by name (`item-classes.yaml`, …): each one's parsed
    #: content — or, when it cannot be read, the reason, which `validate` reports. Absent: no file.
    homework_config: dict[str, dict | str] = field(default_factory=dict)

    def config_file(self, name: str) -> dict | None:
        """A homework configuration file's content, or None when it is absent or unreadable."""
        value = self.homework_config.get(name)
        return value if isinstance(value, dict) else None

    @property
    def item_classes(self) -> dict:
        """The item classes (`item-classes.yaml`), by name — {} when there is none."""
        return {k: v for k, v in (self.config_file(ITEM_CLASSES) or {}).items() if isinstance(v, dict)}

    def documents(self) -> list[Doc]:
        """Every front-matter document in the course — the files that may carry `accepted:`."""
        docs: list[Doc] = [self.syllabus] if self.syllabus is not None else []
        for unit in self.units:
            docs.append(unit.doc)
            docs.extend(unit.sessions)
            if unit.in_class is not None:
                docs.append(unit.in_class)
        docs.extend(self.items)
        docs.extend(self.homework)
        return docs

    @property
    def outcomes(self) -> list[dict]:
        """The Course Outcomes declared in the syllabus, in order."""
        if self.syllabus is None:
            return []
        return [o for o in (self.syllabus.data.get("outcomes") or []) if isinstance(o, dict)]


#: Where homework lives, and its configuration files (homework module, HW-D01, HW-D02, HW-D16, HW-D30).
HOMEWORK_DIR = Path("assessments") / "homework"
ITEM_CLASSES = "item-classes.yaml"
HOMEWORK_DEFAULTS = "homework-defaults.yaml"
HOMEWORK_DOCUMENT = "homework-document.yaml"
HOMEWORK_CONFIG = (ITEM_CLASSES, HOMEWORK_DEFAULTS, HOMEWORK_DOCUMENT)


def homework_files(course_root: Path) -> list[Path]:
    """The homework files, `assessments/homework/HW*.md`, in order."""
    directory = course_root / HOMEWORK_DIR
    return sorted(p for p in directory.glob("HW*.md") if p.is_file()) if directory.is_dir() else []


class LayoutError(Exception):
    """The framework or course tree is not where it was expected to be."""


def find_framework_root(start: Path | None = None) -> Path:
    """Walk upward looking for the framework repo (it holds schemas/ and methodologies/)."""
    candidates = []
    if start is not None:
        candidates.append(Path(start).resolve())
    candidates.append(Path.cwd().resolve())
    candidates.append(Path(__file__).resolve().parents[2])

    for candidate in candidates:
        for directory in [candidate, *candidate.parents]:
            if (directory / "schemas").is_dir() and (directory / "methodologies").is_dir():
                return directory
    raise LayoutError(
        "cannot find the framework root (a directory containing schemas/ and methodologies/)"
    )


def find_course_root(start: Path | None = None) -> Path:
    """Walk upward looking for the course tree (the directory holding course.yaml)."""
    base = Path(start).resolve() if start else Path.cwd().resolve()

    if (base / "course.yaml").is_file():
        return base
    for directory in [base, *base.parents]:
        if (directory / "course" / "course.yaml").is_file():
            return directory / "course"
    raise LayoutError(
        "cannot find a course (no course/course.yaml found here or above). "
        "Run `classkit scaffold course` first, or pass an explicit path."
    )


def methodology_path(framework_root: Path, name: str, course_root: Path | None = None) -> Path:
    """The methodology file a course uses: its own, `course/methodologies/<name>.yaml`, when it has
    one by that name, else the framework's. A teacher's own methodology lives in the course, which
    an update of the plugin never touches (plugin migration, Phase 4; assessment §6.5; D-011)."""
    if course_root is not None:
        own = course_root / "methodologies" / f"{name}.yaml"
        if own.is_file():
            return own
    return framework_root / "methodologies" / f"{name}.yaml"


def load_methodology(framework_root: Path, name: str, course_root: Path | None = None) -> dict:
    path = methodology_path(framework_root, name, course_root)
    if not path.is_file():
        folders = [framework_root / "methodologies"]
        if course_root is not None:
            folders.insert(0, course_root / "methodologies")
        available = sorted({p.stem for folder in folders for p in folder.glob("*.yaml")})
        raise LayoutError(
            f"unknown methodology {name!r}. Available: {', '.join(available) or '(none)'}"
        )
    return load_yaml(path)


def load_time_constants(framework_root: Path, overrides: dict | None) -> dict:
    constants = load_yaml(framework_root / "defaults" / "time-constants.yaml")
    constants.update(overrides or {})
    return constants


def normalize_rules(block: dict) -> None:
    """Read a bare ``off`` in a ``rules:`` block as the severity it was meant to be.

    YAML 1.1 — which PyYAML implements — parses an unquoted ``off`` (and ``no``) as the
    boolean ``False``. ``rules: {session_count: off}`` is exactly what the spec tells a
    teacher to write, so it must mean ``"off"``, not fail the schema.
    """
    rules = block.get("rules")
    if isinstance(rules, dict):
        block["rules"] = {code: ("off" if level is False else level) for code, level in rules.items()}


#: A unit's stage `built` was called this until 0.3.0 (D-050); it is still read, as `built`.
OLD_BUILT = "designed"


def normalize_approved(data: dict) -> None:
    """Read an `approved: {date: 2026-10-05}` record as it was meant (D-043, spec §8.9) — the
    syllabus's, and a unit's (D-046).

    An unquoted date parses as a ``datetime.date``; it becomes an ISO string, which is what the
    schema and `classkit status` expect. The key was ``on`` until D-044 — but YAML 1.1 reads a bare
    ``on`` as the boolean ``True`` (the same trap as ``off``), so it was renamed; a record written
    with ``on:`` is still read, as ``date``. A unit's stage ``built`` was called ``designed`` until
    0.3.0 (D-050, with the command's rename to /class-kit:build-unit); a record with the old name is read as
    ``built``.
    """
    record = data.get("approved")
    if not isinstance(record, dict):
        return
    if True in record and "date" not in record:
        record["date"] = record.pop(True)
    if isinstance(record.get("date"), datetime.date):
        record["date"] = record["date"].isoformat()
    if record.get("stage") == OLD_BUILT:
        record["stage"] = "built"


def load_course(course_root: Path, framework_root: Path) -> Course:
    config = load_yaml(course_root / "course.yaml")
    methodology_name = config.get("methodology", "question-driven-25")
    methodology = load_methodology(framework_root, methodology_name, course_root)
    normalize_rules(config)
    normalize_rules(methodology)
    constants = load_time_constants(framework_root, config.get("time_constants"))

    course = Course(
        root=course_root,
        config=config,
        methodology=methodology,
        time_constants=constants,
        methodology_file=methodology_path(framework_root, methodology_name, course_root),
    )

    syllabus_file = course_root / "syllabus" / "syllabus.md"
    if syllabus_file.is_file():
        s_data, s_body = load(syllabus_file)
        normalize_approved(s_data)
        course.syllabus = Doc(syllabus_file, s_data, s_body)

    units_dir = course_root / "units"
    if units_dir.is_dir():
        for unit_dir in sorted(p for p in units_dir.iterdir() if p.is_dir()):
            unit_file = unit_dir / "unit.md"
            if not unit_file.is_file():
                continue
            data, body = load(unit_file)
            normalize_approved(data)
            unit = Unit(doc=Doc(unit_file, data, body), directory=unit_dir)

            sessions_dir = unit_dir / "sessions"
            if sessions_dir.is_dir():
                for session_file in sorted(sessions_dir.glob("*.md")):
                    s_data, s_body = load(session_file)
                    unit.sessions.append(Doc(session_file, s_data, s_body))

            in_class_file = unit_dir / "in-class.md"
            if in_class_file.is_file():
                ic_data, ic_body = load(in_class_file)
                unit.in_class = Doc(in_class_file, ic_data, ic_body)

            course.units.append(unit)

    items_dir = course_root / "assessments" / "items"
    if items_dir.is_dir():
        for item_file in sorted(items_dir.glob("*.md")):
            i_data, i_body = load(item_file)
            course.items.append(Doc(item_file, i_data, i_body))

    for homework_file in homework_files(course_root):
        h_data, h_body = load(homework_file)
        normalize_approved(h_data)
        course.homework.append(Doc(homework_file, h_data, h_body))

    for name in HOMEWORK_CONFIG:
        path = course_root / "assessments" / name
        if path.is_file():
            try:
                course.homework_config[name] = load_yaml(path) or {}
            except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError) as exc:
                course.homework_config[name] = str(exc).strip()

    return course
