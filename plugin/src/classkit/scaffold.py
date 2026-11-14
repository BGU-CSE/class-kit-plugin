"""Scaffolding — create content skeletons in a course repo from framework templates.

Two properties, both decided deliberately (Q-008):

* **Create-only.** Nothing is ever overwritten. Re-running `scaffold unit 5` after you
  have edited unit 5 is safe: you get whatever files are missing and keep everything you
  wrote. Skipped files are reported, never silently passed over.
* **Templates are copied, not shipped.** The framework never places files in the course
  tree itself (D-009), so the course tree exists only because scaffold built it (D-015).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import frontmatter, log
from .model import (
    ANSWER_FIELDS,
    ANSWERS_DIR,
    HOMEWORK_CONFIG,
    HOMEWORK_DEFAULTS,
    HOMEWORK_DIR,
    HOMEWORK_DOCUMENT,
    ITEM_CLASSES,
    homework_files,
    load_methodology,
    load_yaml,
)
from .write import write

_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


@dataclass
class Result:
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)

    def merge(self, other: Result) -> Result:
        self.created.extend(other.created)
        self.skipped.extend(other.skipped)
        return self


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "untitled"


def render(template: str, values: dict) -> str:
    return _PLACEHOLDER.sub(lambda m: str(values.get(m.group(1), m.group(0))), template)


def write_new(path: Path, content: str, result: Result) -> None:
    """Write `content` to `path` unless something is already there.

    The create-only special case of the overwrite-safe write path (`write.write`):
    scaffolding never passes `overwrite`, so it has no way to replace a teacher's file
    at all. A path that already holds content — or already holds exactly this content —
    is recorded as skipped and reported, never silently passed over.
    """
    outcome = write(path, content, overwrite=False)
    (result.created if outcome.wrote else result.skipped).append(path)


def _template(framework_root: Path, *parts: str) -> str:
    return (framework_root.joinpath("templates", *parts)).read_text(encoding="utf-8")


def _methodology_values(methodology: dict) -> dict:
    home = methodology.get("home_study", {})
    in_class = methodology.get("in_class", {})
    objectives = (methodology.get("unit") or {}).get("objectives", {})
    goals = home.get("goals_per_session", {})
    return {
        "sessions_per_unit": home.get("sessions_per_unit", 4),
        "session_minutes": home.get("session_minutes", 25),
        "home_minutes": home.get("total_minutes", 100),
        "in_class_minutes": in_class.get("minutes", 50),
        "objectives_min": objectives.get("min", 2),
        "objectives_max": objectives.get("max", 4),
        "goals_min": goals.get("min", 3),
        "goals_max": goals.get("max", 5),
    }


# -- course ----------------------------------------------------------------

COURSE_DIRECTORIES = [
    "units",
    "assessments/items",
    "assessments/quizzes",
    "assessments/homework",
    "assessments/exams",
    "materials/ingested",
    # Created with the others, so the private option is visible from day one (the teacher's
    # request). It is gitignored, so its .gitkeep is never committed and a clone starts without
    # it — `classkit doctor` notes that, and re-running `scaffold course` creates it.
    "materials/source/private",
    "policies",
]

# `materials/source/` is where the teacher drops their existing course materials. It is the
# input to /class-kit:ingest, so it ships with a README explaining what belongs there — an empty
# unexplained directory gets ignored — and with `links.md`, the course's list of links (D-035).
# `materials/ingested/` is the derived layer `classkit ingest` writes into.
SOURCE_README = "materials/source/README.md"
SOURCE_LINKS = "materials/source/links.md"

# The syllabus is the course-level top layer (D-021), so it is part of the first thing a
# teacher sees rather than something a later command conjures. Scaffold writes the skeleton
# once into the reserved `syllabus/` slot and, being create-only, never touches it again.
SYLLABUS = "syllabus/syllabus.md"

# `course/.gitignore` keeps private material out of git (D-040, spec §8.7): the teacher's
# `materials/source/private/` (a published book, a solutions manual) and the full text ingest
# extracts from it, `materials/private-text/`. It lives in `course/`, so it belongs to the course
# and never conflicts with a framework update. Like everything scaffold writes, create-only — and
# so re-running `scaffold course` adds it to a course created before it existed.
GITIGNORE = ".gitignore"

# `course/.gitattributes` keeps every text file at LF in every clone. Git for Windows converts text
# to CRLF on checkout by default, which changes the bytes ingest hashed — every material and every
# ingested file would look changed, or "edited by hand", on a Windows machine. Create-only, like
# `.gitignore`, so a re-run adds it to an older course.
GITATTRIBUTES = ".gitattributes"


# The course repository's Claude Code settings, `.claude/settings.json` in the folder that holds
# `course/` — where a session starts, and the only place Claude Code reads them from (Phase 1,
# finding 11). It turns off the PowerShell tool, so that on Windows `classkit` always runs through
# Bash (finding 9), and lets the read-only `classkit` commands run without a permission prompt
# (D-045). Create-only like everything scaffold writes: a repository that already has settings keeps
# them, and a re-run adds the file to a course created before it existed. Not part of the course
# itself, so it is not in the course log.
CLAUDE_SETTINGS = ".claude/settings.json"


def course_settings_path(course_root: Path) -> Path:
    """Where the course repository's settings go: beside `course/`, or in the course folder itself
    when it is not called `course` (`--path` somewhere else, or `--path .`)."""
    top = course_root.parent if course_root.name == "course" else course_root
    return top / CLAUDE_SETTINGS


def scaffold_course(
    course_root: Path,
    framework_root: Path,
    *,
    code: str = "",
    title: str,
    institution: str,
    instructor: str,
    units: int,
    methodology: str,
    language: str = "en",
) -> Result:
    result = Result()
    log_existed = (course_root / log.LOG_FILE).is_file()

    # First, so the ignore rules are in place before anything private could be added.
    write_new(course_root / GITIGNORE, _template(framework_root, "course", "gitignore"), result)
    write_new(course_root / GITATTRIBUTES, _template(framework_root, "course", "gitattributes"), result)

    for directory in COURSE_DIRECTORIES:
        write_new(course_root / directory / ".gitkeep", "", result)

    write_new(
        course_root / SOURCE_README,
        _template(framework_root, "course", "materials-source-README.md"),
        result,
    )
    write_new(
        course_root / SOURCE_LINKS,
        _template(framework_root, "course", "links.md"),
        result,
    )

    write_new(
        course_root / SYLLABUS,
        _template(framework_root, "course", "syllabus.md"),
        result,
    )

    write_new(
        course_root / "course.yaml",
        render(
            _template(framework_root, "course", "course.yaml"),
            {
                # Optional (D-048): identity no tool reads; a teacher may scaffold before
                # finding it. Left as a commented placeholder, which `classkit status` reports.
                "code_line": (f"code: {json.dumps(code, ensure_ascii=False)}" if code.strip() else
                              '# code: ""   # the institution\'s course code — not set yet; '
                              "/class-kit:plan-syllabus asks for it"),
                "title": title,
                "institution": institution,
                # `[]` with no instructor, not a list holding one empty string.
                "instructors": (f"\n  - {json.dumps(instructor, ensure_ascii=False)}"
                                if instructor.strip() else " []"),
                "language": language,
                "units": units,
                "methodology": methodology,
            },
        ),
        result,
    )

    write_new(course_settings_path(course_root),
              _template(framework_root, "course", "claude-settings.json"), result)

    # The course log (D-036) is written last, so its first entry can say truthfully what
    # this run created — on a fresh course, everything; on an older course that predates
    # the log, only what was missing. Only files inside the course: not the repository's settings.
    created = [
        path.relative_to(course_root).as_posix()
        for path in result.created
        if path.name != ".gitkeep" and path.is_relative_to(course_root)
    ]
    if log_existed:
        # Re-run on a course that already has a log: what this run added is a change to the
        # course like any other, so it is an entry — typically `.gitignore`, added to a course
        # scaffolded before it existed.
        if created:
            log.append(course_root, log.Entry(
                title="classkit scaffold course",
                changed=f"created {', '.join(created)}; every other file already existed",
                why="re-run to add what a newer framework scaffolds",
                files=created,
            ))
        else:
            result.skipped.append(course_root / log.LOG_FILE)
        return result
    write_new(
        course_root / log.LOG_FILE,
        log.new_log(
            log.Entry(
                title="classkit scaffold course",
                changed=f"course log started; created {', '.join(created)}"
                if created
                else "course log started; every other file already existed",
                why=f"setting up {title}" + (f" ({code})" if code.strip() else ""),
                files=[*created, log.LOG_FILE],
            )
        ),
        result,
    )
    return result


# -- unit ------------------------------------------------------------------

def find_unit_directory(course_root: Path, number: int) -> Path | None:
    units_dir = course_root / "units"
    if not units_dir.is_dir():
        return None
    for candidate in sorted(units_dir.iterdir()):
        if candidate.is_dir() and candidate.name.startswith(f"{number:02d}-"):
            return candidate
    return None


def scaffold_unit(
    course_root: Path,
    framework_root: Path,
    number: int,
    title: str | None = None,
) -> Result:
    methodology = _course_methodology(course_root, framework_root)
    values = _methodology_values(methodology)

    unit_id = f"U{number:02d}"
    unit_title = title or f"Unit {number}"

    directory = find_unit_directory(course_root, number)
    if directory is None:
        directory = course_root / "units" / f"{number:02d}-{slugify(unit_title)}"

    values |= {"unit_id": unit_id, "unit_number": number, "unit_title": unit_title}

    result = Result()
    write_new(
        directory / "unit.md",
        render(_template(framework_root, "unit", "unit.md"), values),
        result,
    )

    for index in range(1, int(values["sessions_per_unit"]) + 1):
        result.merge(
            scaffold_session(course_root, framework_root, unit_id, index, directory=directory)
        )

    write_new(
        directory / "in-class.md",
        render(_template(framework_root, "unit", "in-class.md"), values),
        result,
    )

    # A new unit is a change to the course, so it is logged like `scaffold course` (teacher
    # test); a re-run that created nothing is not an entry.
    if result.created:
        files = [path.relative_to(course_root).as_posix() for path in result.created]
        log.append(course_root, log.Entry(
            title=f"classkit scaffold unit {number}",
            changed=f"{unit_id} \"{unit_title}\": {len(files)} placeholder "
                    f"file{'s' if len(files) != 1 else ''} created (listed below)",
            why="placeholders for /class-kit:plan-units and /class-kit:build-unit to fill",
            files=files,
        ))
    return result


# -- study session ---------------------------------------------------------

def scaffold_session(
    course_root: Path,
    framework_root: Path,
    unit_id: str,
    number: int,
    title: str | None = None,
    directory: Path | None = None,
) -> Result:
    methodology = _course_methodology(course_root, framework_root)
    values = _methodology_values(methodology)

    unit_number = int(unit_id[1:])
    if directory is None:
        directory = find_unit_directory(course_root, unit_number)
        if directory is None:
            raise FileNotFoundError(
                f"no directory for unit {unit_id}. Run `classkit scaffold unit {unit_number}` first."
            )

    values |= {
        "unit_id": unit_id,
        "session_id": f"{unit_id}-S{number:02d}",
        "session_number": number,
        "session_title": title or f"Study session {number}",
    }

    result = Result()
    write_new(
        directory / "sessions" / f"{number:02d}.md",
        render(_template(framework_root, "unit", "session.md"), values),
        result,
    )
    return result


# -- assessment item -------------------------------------------------------

#: The item formats, each with its template `templates/assessment/item-<format>.md`.
ITEM_FORMATS = ("multiple-choice", "multiple-select", "true-false", "open", "numeric", "code")


def scaffold_item(
    course_root: Path,
    framework_root: Path,
    unit_id: str,
    item_format: str = "multiple-choice",
    item_class: str | None = None,
) -> Result:
    """A new assessment item, `assessments/items/UNN-INN.md`, with the next free number. With an
    item class (homework module) the item is a homework item — `item_class` set, `usage:
    [homework]` — and the homework's configuration files are created if they are missing, since
    the class is defined in one of them."""
    if item_format not in ITEM_FORMATS:
        raise ValueError(f"unknown item format {item_format!r} (one of: {', '.join(ITEM_FORMATS)})")
    items_dir = course_root / "assessments" / "items"
    existing = {p.stem for p in items_dir.glob(f"{unit_id}-I*.md")} if items_dir.is_dir() else set()

    number = 1
    while f"{unit_id}-I{number:02d}" in existing:
        number += 1
    item_id = f"{unit_id}-I{number:02d}"

    text = render(
        _template(framework_root, "assessment", f"item-{item_format}.md"),
        {"item_id": item_id, "unit_id": unit_id},
    )
    result = Result()
    if item_class:
        config = scaffold_homework_config(course_root, framework_root)
        _log_config(course_root, config, f"classkit scaffold item {unit_id} --class {item_class}")
        result.merge(config)
        text = re.sub(r"^format: .*$", lambda m: f"{m.group(0)}\nitem_class: {json.dumps(item_class)}", text,
                      count=1, flags=re.M)
        text = re.sub(r"^usage: .*$", "usage: [homework]", text, count=1, flags=re.M)
        text = _fit_class(text, _item_class(course_root, item_class))
        text, answers = split_answers(text, item_id)
        write_new(course_root / ANSWERS_DIR / f"{item_id}.md", answers, result)
    write_new(items_dir / f"{item_id}.md", text, result)
    return result


def split_answers(text: str, item_id: str) -> tuple[str, str]:
    """A homework item's template split in two (HW-D35): the question, to be committed, and its
    answers — which choices are correct and why each is picked, the model answer, rubric,
    reference solution and tests — for `assessments/answers/`, which git ignores. The question
    keeps the template's own notes; the answers file gets a short header of its own."""
    data, body = frontmatter.parse(text)
    answers: dict = {"id": item_id}
    choices = data.get("choices")
    if isinstance(choices, list):
        answers["correct"] = [c["label"] for c in choices if isinstance(c, dict) and c.get("correct")]
        answers["rationales"] = {c["label"]: c["rationale"] for c in choices
                                 if isinstance(c, dict) and c.get("rationale")}
        data["choices"] = [{k: v for k, v in c.items() if k not in ("correct", "rationale")}
                           if isinstance(c, dict) else c for c in choices]
    for key in ANSWER_FIELDS:
        if key in data:
            answers[key] = data.pop(key)
    dump = lambda d: yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=100)  # noqa: E731
    question = (f"---\n# A homework item: the question, committed. Its answers are in "
                f"{(ANSWERS_DIR / (item_id + '.md')).as_posix()},\n# which git ignores (HW-D35).\n"
                f"{dump(data)}---\n{body}")
    answer = (f"---\n# The answers to {item_id} — never committed: assessments/answers/ is gitignored, so\n"
              "# they are only on this computer. Back them up yourself (HW-D35).\n"
              f"{dump(answers)}---\n")
    return question, answer


def _item_class(course_root: Path, name: str) -> dict | None:
    try:
        classes = load_yaml(course_root / "assessments" / ITEM_CLASSES)
    except (OSError, ValueError, yaml.YAMLError):
        return None
    found = classes.get(name)
    return found if isinstance(found, dict) else None


def _fit_class(text: str, item_class: dict | None) -> str:
    """A classed placeholder within its class: its Bloom level one the class works at, its minutes
    the class's typical midpoint — so a placeholder does not start out drifting from its class."""
    if item_class is None:
        return text
    blooms = [b for b in item_class.get("typical_bloom") or [] if isinstance(b, str)]
    found = re.search(r"^bloom: (\S+)", text, flags=re.M)
    if blooms and found and found.group(1) not in blooms:
        text = text[:found.start()] + f"bloom: {blooms[0]}" + text[found.end():]
    span = item_class.get("typical_minutes") if isinstance(item_class.get("typical_minutes"), dict) else {}
    low, high = span.get("min"), span.get("max")
    found = re.search(r"^est_minutes: (\d+(?:\.\d+)?)", text, flags=re.M)
    if found and isinstance(low, (int, float)) and isinstance(high, (int, float)) \
            and not low <= float(found.group(1)) <= high:
        text = text[:found.start()] + f"est_minutes: {round((low + high) / 2):g}" + text[found.end():]
    return text


def _log_config(course_root: Path, config: Result, title: str) -> None:
    """Log the configuration files a scaffold created — they are the course's from then on."""
    if config.created:
        files = [path.relative_to(course_root).as_posix() for path in config.created]
        log.append(course_root, log.Entry(
            title=title,
            changed=f"the homework's configuration created from the plugin's templates: {', '.join(files)}",
            why="the item classes, homework defaults and document settings homework works from (HW-D13)",
            files=files,
        ))


def undeclared_class_tools(course_root: Path) -> list[str]:
    """The tools the course's item classes name that `course.yaml`'s `tools` does not declare —
    what `class_tools_declared` will report, said when the classes are created."""
    try:
        classes = load_yaml(course_root / "assessments" / ITEM_CLASSES)
        tools = load_yaml(course_root / "course.yaml").get("tools")
    except (OSError, ValueError, yaml.YAMLError):
        return []
    declared = set(tools) if isinstance(tools, dict) else set()
    named = [tool for c in classes.values() if isinstance(c, dict)
             for tool in c.get("default_tools") or [] if isinstance(tool, str)]
    return [tool for tool in dict.fromkeys(named) if tool not in declared]


# -- homework (homework module) --------------------------------------------

#: Languages written right to left — the homework documents' default direction for them.
RTL_LANGUAGES = ("he", "ar", "fa", "ur", "yi")


def _document_values(course_root: Path) -> dict:
    """What `homework-document.yaml` starts from: the course's own title and language
    (`course.yaml`), so a course in English does not get Hebrew, right-to-left documents."""
    try:
        config = load_yaml(course_root / "course.yaml")
    except (OSError, ValueError, yaml.YAMLError):
        config = {}
    language = str(config.get("language") or "en").split("-")[0].lower()
    rtl = language in RTL_LANGUAGES
    return {
        "course_title": json.dumps(str(config.get("title") or "Course name"), ensure_ascii=False),
        "language": language,
        "direction": "rtl" if rtl else "ltr",
        "font": "David" if language == "he" else "Calibri",
    }


def scaffold_homework_config(course_root: Path, framework_root: Path) -> Result:
    """The homework's configuration files — `item-classes.yaml`, `homework-defaults.yaml`,
    `homework-document.yaml` in `assessments/` — from their templates, each only if it is missing.
    Homework is optional (HW-D13): `scaffold course` does not create them; the first homework does.
    The document settings start from the course's title and language."""
    result = Result()
    for name in HOMEWORK_CONFIG:
        text = _template(framework_root, "course", name)
        if name == HOMEWORK_DOCUMENT:
            text = render(text, _document_values(course_root))
        write_new(course_root / "assessments" / name, text, result)
    return result


def next_homework_number(course_root: Path) -> int:
    numbers = [int(p.stem[2:]) for p in homework_files(course_root) if p.stem[2:].isdigit()]
    return max(numbers, default=0) + 1


def scaffold_homework(
    course_root: Path,
    framework_root: Path,
    units: list[str],
    number: int | None = None,
) -> Result:
    """A new homework, `assessments/homework/HWNN.md` — with the next free number unless one is
    given — as a placeholder for /class-kit:plan-homework to fill: the units it covers, the budget
    from the teacher's homework defaults, an empty plan and no items. Creates the homework's
    configuration files if they are missing. Create-only, and logged like `scaffold unit`."""
    unit_ids = []
    for unit in units:
        text = str(unit).strip().upper().lstrip("U")
        if not text.isdigit():
            raise ValueError(f"not a unit: {unit!r} (write U03, or 3)")
        unit_ids.append(f"U{int(text):02d}")
    if not unit_ids:
        raise ValueError("which units does the homework cover? (--units U03 U04)")
    number = number or next_homework_number(course_root)
    homework_id = f"HW{number:02d}"

    result = scaffold_homework_config(course_root, framework_root)
    try:
        defaults = load_yaml(course_root / "assessments" / HOMEWORK_DEFAULTS)
    except (OSError, ValueError, yaml.YAMLError):
        defaults = {}  # unreadable: `classkit validate` reports it
    total = defaults.get("total_minutes")
    if not isinstance(total, int):
        total = load_yaml(framework_root / "templates" / "course" / HOMEWORK_DEFAULTS).get("total_minutes")
    write_new(
        course_root / HOMEWORK_DIR / f"{homework_id}.md",
        render(_template(framework_root, "assessment", "homework.md"), {
            "homework_id": homework_id,
            "homework_number": number,
            "units": ", ".join(dict.fromkeys(unit_ids)),
            "total_minutes": total,
        }),
        result,
    )
    if result.created:
        files = [path.relative_to(course_root).as_posix() for path in result.created]
        log.append(course_root, log.Entry(
            title=f"classkit scaffold homework {number}",
            changed=f"{homework_id} ({', '.join(unit_ids)}): {len(files)} placeholder "
                    f"file{'s' if len(files) != 1 else ''} created (listed below)",
            why="placeholders for /class-kit:plan-homework to fill",
            files=files,
        ))
    return result


# -- helpers ---------------------------------------------------------------

def _course_methodology(course_root: Path, framework_root: Path) -> dict:
    config_path = course_root / "course.yaml"
    name = "question-driven-25"
    if config_path.is_file():
        name = load_yaml(config_path).get("methodology", name)
    return load_methodology(framework_root, name, course_root)
