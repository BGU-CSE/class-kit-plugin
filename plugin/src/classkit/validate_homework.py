"""The homework rules of `classkit validate` (homework module; HOMEWORK-SPEC §7.2).

Mixed into `validate.Validator`, so every rule reports through the one `report()` — the course's
`rules:`, a file's `accepted:` and the severity table work exactly as for the rest of the course.

**Homework is optional** (HW-D13). Every rule here is a *consistency* rule: it judges only the
homework files, item classes and defaults that exist, and says nothing about a course that has
none — a fresh scaffold has no homework findings. Configuration rules run whenever their file
exists (after an abandoned first homework, say), and still report a malformed file.

**A homework is judged in the state it is in.** Before it is built it has a plan but no items: the
rules about items are silent, and the coverage and budget rules judge the plan's slots instead —
so a plan that leaves a unit out is reported at its gate, not after the build. A scaffolded
placeholder, with neither slots nor items, is judged on its settings alone.
"""

from __future__ import annotations

from pathlib import Path

from .approve import homework_items
from .model import HOMEWORK_DEFAULTS, ITEM_CLASSES, Doc

#: Formats whose answer is graded against a rubric (`graded_requires_rubric`).
RUBRIC_FORMATS = ("open", "code")


def _strings(value) -> list[str]:
    """`value` as a list of strings — whatever is not one is the schema's to report."""
    return [str(v) for v in value if isinstance(v, (str, int))] if isinstance(value, list) else []


def _dicts(value) -> list[dict]:
    return [v for v in value if isinstance(v, dict)] if isinstance(value, list) else []


def unit_of(guiding_question: str) -> str:
    """The unit a Guiding Question id belongs to: `U03-S02-G1` → `U03`."""
    return guiding_question.split("-", 1)[0]


def midpoint(item_class: dict | None) -> float | None:
    """The middle of a class's `typical_minutes` range, or None when it has none (HW-D06)."""
    span = item_class.get("typical_minutes") if isinstance(item_class, dict) else None
    if not isinstance(span, dict):
        return None
    low, high = span.get("min"), span.get("max")
    if isinstance(low, (int, float)) and isinstance(high, (int, float)):
        return (low + high) / 2
    return None


def class_of(entry: dict, classes: dict) -> dict | None:
    """The class an item or a slot names, or None — whatever its `item_class` is (a list, a number:
    the schema reports that; nothing here may crash on it)."""
    name = entry.get("item_class")
    return classes.get(name) if isinstance(name, str) else None


def minutes(entry: dict, classes: dict) -> float | None:
    """An item's or a slot's minutes: its own `est_minutes`, else its class's midpoint (HW-D06)."""
    own = entry.get("est_minutes")
    if isinstance(own, (int, float)) and not isinstance(own, bool):
        return float(own)
    return midpoint(class_of(entry, classes))


def strategy(item: dict, classes: dict) -> str | None:
    """How item-solver checks an item: its own `evaluation_strategy`, else its class's (HW-D07)."""
    own = item.get("evaluation_strategy")
    if isinstance(own, str):
        return own
    evaluation = (class_of(item, classes) or {}).get("evaluation")
    return evaluation.get("strategy") if isinstance(evaluation, dict) else None


class HomeworkChecks:
    """The homework rules. Expects `self.course`, `self.report` and `self.course_goal_ids`."""

    def check_homework(self) -> None:
        self._classes = self.course.item_classes
        config_tools = self.course.config.get("tools")
        self._tools = set(config_tools) if isinstance(config_tools, dict) else set()
        self._items = {item.id: item for item in self.course.items}
        self._unit_ids = {unit.id for unit in self.course.units}
        # An unreadable item-classes.yaml is reported once, as a `schema` error; the classes it may
        # define are then unknown, so nothing is reported as undefined in it.
        self._classes_known = not isinstance(self.course.homework_config.get(ITEM_CLASSES), str)

        self.check_item_classes_file()
        self.check_homework_defaults()
        for homework in self.course.homework:
            self.check_one_homework(homework)
        self.check_items_against_classes()

    # -- the configuration files ---------------------------------------------

    def _config_path(self, name: str) -> Path:
        return self.course.root / "assessments" / name

    def check_item_classes_file(self) -> None:
        """`class_tools_declared`, `item_class_evaluation_declared`, `item_class_guide_reference`."""
        if self.course.config_file(ITEM_CLASSES) is None:
            return
        where = self._config_path(ITEM_CLASSES)
        for name, item_class in self._classes.items():
            for tool in _strings(item_class.get("default_tools")):
                if tool not in self._tools:
                    self.report(
                        "class_tools_declared", where,
                        f"item class {name!r} names the tool {tool!r}, which course.yaml's `tools` "
                        "does not declare. Declare it there, or take it out of the class.",
                        item=None)
            evaluation = item_class.get("evaluation")
            if not isinstance(evaluation, dict) or not evaluation.get("strategy"):
                self.report(
                    "item_class_evaluation_declared", where,
                    f"item class {name!r} has no `evaluation.strategy`, so item-solver falls back to "
                    "attempting an item when it has a model answer or rubric, and skipping it "
                    "otherwise. Say which: persona_attempt, execute, skip or custom.",
                    item=None)
            guides = [("writing_guide", item_class.get("writing_guide"))]
            if isinstance(evaluation, dict):
                guides.append(("evaluation.custom_guide", evaluation.get("custom_guide")))
            for key, guide in guides:
                if not isinstance(guide, str) or not guide.strip():
                    continue
                root = self.course.root.resolve()
                target = (self.course.root / guide.strip()).resolve()
                if not target.is_relative_to(root):
                    self.report(
                        "item_class_guide_reference", where,
                        f"item class {name!r}: its `{key}` is {guide!r}, which is outside course/. "
                        "A guide is a course file: give its path relative to course/.",
                        item=None)
                elif not target.is_file():
                    self.report(
                        "item_class_guide_reference", where,
                        f"item class {name!r}: its `{key}` is {guide!r}, but there is no such file "
                        "in course/. Correct the path, or write the guide "
                        "(/class-kit:new-item-class drafts one).",
                        item=None)

    def check_homework_defaults(self) -> None:
        """`homework_defaults_class_reference` and `homework_defaults_consistent` (HW-D16, HW-D27)."""
        defaults = self.course.config_file(HOMEWORK_DEFAULTS)
        if defaults is None:
            return
        where = self._config_path(HOMEWORK_DEFAULTS)
        counts = defaults.get("default_class_counts")
        if not isinstance(counts, dict):
            return
        counts = {str(k): v for k, v in counts.items() if isinstance(v, int) and not isinstance(v, bool)}
        for name in counts:
            if self._classes_known and name not in self._classes:
                where_classes = "item-classes.yaml" if self.course.config_file(ITEM_CLASSES) is not None \
                    else "item-classes.yaml (which does not exist)"
                self.report(
                    "homework_defaults_class_reference", where,
                    f"`default_class_counts` names the item class {name!r}, which is not in "
                    f"{where_classes}. Add the class (/class-kit:new-item-class), or remove its count.",
                    item=None)
        if not any(count > 0 for count in counts.values()):
            self.report(
                "homework_defaults_consistent", where,
                "`default_class_counts` has no count above 0, so a homework planned from the "
                "defaults would have no items. Give at least one class a count.",
                item=None)
            return
        total = defaults.get("total_minutes")
        if not isinstance(total, (int, float)):
            return
        estimated = 0.0
        for name, count in counts.items():
            middle = midpoint(self._classes.get(name))
            if middle is None:
                return  # a class without a range cannot be estimated; reported above if unknown
            estimated += count * middle
        tolerance = self._budget_tolerance()
        if tolerance is not None and abs(estimated - total) > tolerance:
            self.report(
                "homework_defaults_consistent", where,
                f"the default counts come to about {estimated:.0f} min (count × each class's "
                f"typical-minutes midpoint), but `total_minutes` is {total} (tolerance ±{tolerance:g}). "
                "Change the counts or the budget, so a homework planned from them fits.",
                item=None)

    def _budget_tolerance(self) -> float | None:
        """How far a homework's minutes may drift from its budget: the teacher's
        `budget_tolerance_minutes`, else the plugin's default (`defaults/time-constants.yaml`)."""
        defaults = self.course.config_file(HOMEWORK_DEFAULTS) or {}
        for value in (defaults.get("budget_tolerance_minutes"),
                      self.course.time_constants.get("homework_budget_tolerance_minutes")):
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return float(value)
        return None

    # -- one homework ----------------------------------------------------------

    def check_one_homework(self, homework: Doc) -> None:
        data, where, hw = homework.data, homework.path, homework.id

        if hw != homework.path.stem:
            self.report("id_consistency", where,
                        f"{hw}: the file is {homework.path.name}, so its id should be "
                        f"{homework.path.stem!r}.", item=hw)

        units = _strings(data.get("units"))
        for unit in units:
            if unit not in self._unit_ids:
                self.report("homework_unit_reference", where,
                            f"{hw} covers {unit}, which does not exist in this course.", item=hw)

        versions = _dicts(data.get("versions"))
        labels = [str(v.get("label")) for v in versions if v.get("label") is not None]
        slots = _dicts((data.get("plan") or {}).get("slots")) if isinstance(data.get("plan"), dict) else []
        listed = homework_items(data)
        shared = _strings(data.get("items"))

        self._check_references(homework, units, versions, labels, slots, listed)
        self._check_source(homework)
        self._check_tools(homework, slots, listed)
        self._check_usage_and_units(homework, units, slots, listed)
        self._check_coverage(homework, units, slots, listed)
        self._check_budget(homework, versions, slots, shared)
        self._check_versions(homework, units, versions, shared)
        self._check_graded(homework, listed)

    def _check_references(self, homework: Doc, units, versions, labels, slots, listed) -> None:
        data, where, hw = homework.data, homework.path, homework.id
        # Items it lists, items its slots were built from or name, and item_tools' keys.
        for item_id in listed:
            if item_id not in self._items:
                self.report("homework_item_reference", where,
                            f"{item_id}: {hw} lists it, but there is no such item in "
                            "assessments/items/.", item=item_id)
        for slot in slots:
            for key in ("from", "item"):
                item_id = slot.get(key)
                if isinstance(item_id, str) and item_id not in self._items:
                    self.report("homework_item_reference", where,
                                f"{item_id}: slot {slot.get('slot')} of {hw} names it as its "
                                f"`{key}`, but there is no such item.", item=item_id)
        item_tools = data.get("item_tools")
        for item_id in (item_tools if isinstance(item_tools, dict) else {}):
            if item_id not in listed:
                self.report("homework_item_reference", where,
                            f"{item_id}: {hw}'s `item_tools` names it, but it is not an item of "
                            "this homework.", item=str(item_id))

        # The plan's slot numbers, Guiding Questions and version labels.
        numbers: set = set()
        for slot in slots:
            number = slot.get("slot")
            if number is not None and number in numbers:
                self.report("homework_plan_reference", where,
                            f"{hw}: two slots are numbered {number} — a slot's number must be unique, "
                            "so the teacher can name it.", item=hw)
            numbers.add(number)
        for slot in slots:
            for gq in _strings(slot.get("guiding_questions")):
                if gq not in self.course_goal_ids:
                    self.report("homework_plan_reference", where,
                                f"{gq}: slot {slot.get('slot')} of {hw} tests it, but it is not a "
                                "Guiding Question anywhere in this course.", item=gq)
            label = slot.get("version")
            if label is not None and str(label) not in labels:
                self.report("homework_plan_reference", where,
                            f"{hw}: slot {slot.get('slot')} belongs to version {label!r}, which "
                            "`versions` does not define.", item=hw)

        # Versions: unique labels, targets that exist (HW-D26).
        seen: set[str] = set()
        for label in labels:
            if label in seen:
                self.report("homework_version_reference", where,
                            f"{hw}: two versions are labelled {label!r} — a label must be unique.",
                            item=hw)
            seen.add(label)
        for version in versions:
            for gq in _strings(version.get("targets")):
                if gq not in self.course_goal_ids:
                    self.report("homework_version_reference", where,
                                f"{gq}: version {version.get('label')!r} of {hw} targets it, but it "
                                "is not a Guiding Question anywhere in this course.", item=gq)

    def _check_source(self, homework: Doc) -> None:
        """`homework_source_quiz_exists`: a quiz report's `ref` is the unit whose entry quiz it is."""
        source = homework.data.get("source")
        if not isinstance(source, dict) or source.get("kind") != "quiz_report":
            return
        unit = source.get("ref")
        if not isinstance(unit, str):
            return  # the schema requires it
        quiz = [item for item in self.course.items if item.data.get("unit") == unit
                and "in-class-quiz" in _strings(item.data.get("usage"))]
        if quiz:
            return
        why = "it does not exist in this course" if unit not in self._unit_ids \
            else "it has no entry-quiz items (`usage: in-class-quiz`)"
        self.report("homework_source_quiz_exists", homework.path,
                    f"{homework.id} comes from the entry quiz of {unit}, but {why}.", item=homework.id)

    def _check_tools(self, homework: Doc, slots, listed) -> None:
        """`homework_tools_declared` (HW-D03, HW-D28) and `item_class_declared` for the slots."""
        data, where, hw = homework.data, homework.path, homework.id
        named = [("`allowed_tools`", tool) for tool in _strings(data.get("allowed_tools"))]
        item_tools = data.get("item_tools")
        for item_id, tools in (item_tools.items() if isinstance(item_tools, dict) else []):
            named += [(f"`item_tools` for {item_id}", tool) for tool in _strings(tools)]
        for slot in slots:
            named += [(f"slot {slot.get('slot')}", tool) for tool in _strings(slot.get("tools"))]
        for place, tool in named:
            if tool not in self._tools:
                self.report("homework_tools_declared", where,
                            f"{hw}: {place} names the tool {tool!r}, which course.yaml's `tools` "
                            "does not declare. Declare it there, or remove it.", item=hw)
        for slot in slots:
            name = slot.get("item_class")
            if isinstance(name, str) and self._classes_known and name not in self._classes:
                self.report("item_class_declared", where,
                            f"{hw}: slot {slot.get('slot')} is of the item class {name!r}, which "
                            f"{self._classes_file()} does not define.", item=hw)

    def _classes_file(self) -> str:
        return "item-classes.yaml" if self.course.config_file(ITEM_CLASSES) is not None \
            else "item-classes.yaml (which does not exist)"

    def _check_usage_and_units(self, homework: Doc, units, slots, listed) -> None:
        """`homework_item_usage` and `homework_units_declared`."""
        where, hw = homework.path, homework.id
        for item_id in listed:
            item = self._items.get(item_id)
            if item is None:
                continue
            if "homework" not in _strings(item.data.get("usage")):
                self.report("homework_item_usage", where,
                            f"{item_id}: {hw} lists it, but its `usage` does not include "
                            "`homework`.", item=item_id)
            unit = item.data.get("unit")
            if units and unit not in units:
                self.report("homework_units_declared", where,
                            f"{item_id}: {hw} lists it, but it belongs to {unit}, which is not one "
                            f"of the homework's units ({', '.join(units)}).", item=item_id)
        for slot in slots:
            for gq in _strings(slot.get("guiding_questions")):
                if units and gq in self.course_goal_ids and unit_of(gq) not in units:
                    self.report("homework_units_declared", where,
                                f"{gq}: slot {slot.get('slot')} of {hw} tests it, but it belongs to "
                                f"{unit_of(gq)}, which is not one of the homework's units "
                                f"({', '.join(units)}).", item=gq)

    def _check_coverage(self, homework: Doc, units, slots, listed) -> None:
        """`homework_coverage` (alert): every unit the homework covers has an item — or, before
        the build, a slot."""
        if listed:
            covered = {self._items[i].data.get("unit") for i in listed if i in self._items}
            what = "item"
        elif slots:
            covered = {unit_of(gq) for slot in slots for gq in _strings(slot.get("guiding_questions"))}
            what = "planned slot"
        else:
            return
        for unit in units:
            if unit in self._unit_ids and unit not in covered:
                self.report("homework_coverage", homework.path,
                            f"{homework.id} covers {unit}, but no {what} of it tests {unit}.",
                            item=homework.id)

    def _check_budget(self, homework: Doc, versions, slots, shared) -> None:
        """`homework_budget_fits` (HW-D06): a student's minutes — the shared items, plus a version's
        own — against `total_minutes`. Before the build, the plan's slots."""
        total = homework.data.get("total_minutes")
        tolerance = self._budget_tolerance()
        if not isinstance(total, (int, float)) or tolerance is None:
            return
        if shared or any(_strings(v.get("items")) for v in versions):
            entries = {item_id: self._items[item_id].data for item_id in shared if item_id in self._items}
            groups = [("", list(entries.values()))]
            for version in versions:
                own = [self._items[i].data for i in _strings(version.get("items")) if i in self._items]
                if own:
                    groups.append((f"version {version.get('label')!r}: ", list(entries.values()) + own))
            what = "items"
        elif slots:
            shared_slots = [s for s in slots if s.get("version") is None]
            groups = [("", shared_slots)]
            for version in versions:
                own = [s for s in slots if s.get("version") is not None
                       and str(s.get("version")) == str(version.get("label"))]
                if own:
                    groups.append((f"version {version.get('label')!r}: ", shared_slots + own))
            what = "planned slots"
        else:
            return
        if len(groups) > 1:
            # With versions, every student gets the shared part plus a version's: no student does the
            # shared part alone, so it is not judged alone.
            groups = groups[1:]
        for prefix, entries in groups:
            known = [m for m in (minutes(e, self._classes) for e in entries) if m is not None]
            unknown = len(entries) - len(known)
            if not entries or not known:
                continue
            spent = sum(known)
            if abs(spent - total) > tolerance:
                note = f" ({unknown} with no estimate, not counted)" if unknown else ""
                self.report("homework_budget_fits", homework.path,
                            f"{homework.id}: {prefix}the {what} take about {spent:.0f} min{note}, but "
                            f"`total_minutes` is {total} (tolerance ±{tolerance:g}).",
                            item=homework.id)

    def _check_versions(self, homework: Doc, units, versions, shared) -> None:
        """`homework_versions_targeted` (HW-D26): each version targets Guiding Questions of the
        homework's units, covers each target, and its items test its targets and nothing else."""
        where, hw = homework.path, homework.id
        for version in versions:
            label = version.get("label")
            targets = _strings(version.get("targets"))
            for gq in targets:
                if units and gq in self.course_goal_ids and unit_of(gq) not in units:
                    self.report("homework_versions_targeted", where,
                                f"{gq}: version {label!r} of {hw} targets it, but it belongs to "
                                f"{unit_of(gq)}, which is not one of the homework's units.", item=gq)
            own = _strings(version.get("items"))
            if not own:
                continue  # not built yet
            tested: set[str] = set()
            for item_id in own:
                item = self._items.get(item_id)
                if item is None:
                    continue
                if item_id in shared:
                    self.report("homework_versions_targeted", where,
                                f"{item_id}: it is both a shared item of {hw} and an item of version "
                                f"{label!r} — a student of that version would get it twice.",
                                item=item_id)
                gqs = set(_strings(item.data.get("guiding_questions")))
                tested |= gqs
                if not gqs & set(targets):
                    self.report("homework_versions_targeted", where,
                                f"{item_id}: an item of version {label!r} of {hw}, it tests none of "
                                "the version's targets.", item=item_id)
                outside = sorted(gqs - set(targets))
                if outside and gqs & set(targets):
                    self.report("homework_versions_targeted", where,
                                f"{item_id}: an item of version {label!r} of {hw}, it also tests "
                                f"{', '.join(outside)}, outside the version's targets — put what "
                                "everyone should practise in the shared items.", item=item_id)
            for gq in targets:
                if gq not in tested:
                    self.report("homework_versions_targeted", where,
                                f"{gq}: version {label!r} of {hw} targets it, but none of the "
                                "version's items tests it.", item=gq)

    def _check_graded(self, homework: Doc, listed) -> None:
        """`graded_requires_rubric`: a graded homework's open and code items have a rubric."""
        if homework.data.get("purpose") != "graded":
            return
        for item_id in listed:
            item = self._items.get(item_id)
            if item is not None and item.data.get("format") in RUBRIC_FORMATS \
                    and not item.data.get("rubric"):
                self.report("graded_requires_rubric", homework.path,
                            f"{item_id}: {homework.id} is graded, but this {item.data.get('format')} "
                            "item has no rubric to grade it by.", item=item_id)

    # -- items against their classes -------------------------------------------

    def check_items_against_classes(self) -> None:
        """`item_class_declared`, `item_class_bundle_drift`, `item_source_resolvable` and
        `code_execution_reference_present` — on every item that uses the homework fields."""
        for item in self.course.items:
            data = item.data
            name = data.get("item_class")
            item_class = self._classes.get(name) if isinstance(name, str) else None
            if isinstance(name, str) and item_class is None and self._classes_known:
                self.report("item_class_declared", item.path,
                            f"{item.id} is of the item class {name!r}, which "
                            f"{self._classes_file()} does not define. Add the class "
                            "(/class-kit:new-item-class), or correct the name — class names are "
                            "case-sensitive.")
            if item_class is not None:
                bloom, typical = data.get("bloom"), _strings(item_class.get("typical_bloom"))
                if bloom and typical and bloom not in typical:
                    self.report("item_class_bundle_drift", item.path,
                                f"{item.id}: Bloom level {bloom!r} is outside its class {name!r} "
                                f"({', '.join(typical)}). Fine if deliberate — a class is a hint, "
                                "not a lock.")
                own = data.get("est_minutes")
                span = item_class.get("typical_minutes")
                if isinstance(own, (int, float)) and isinstance(span, dict) \
                        and isinstance(span.get("min"), (int, float)) and isinstance(span.get("max"), (int, float)) \
                        and not span["min"] <= own <= span["max"]:
                    self.report("item_class_bundle_drift", item.path,
                                f"{item.id}: {own:g} min is outside its class {name!r} "
                                f"({span['min']:g}–{span['max']:g} min). Fine if deliberate.")
            source = data.get("source_ref")
            if isinstance(source, str) and source not in self._items:
                self.report("item_source_resolvable", item.path,
                            f"{item.id} was adapted from {source}, which does not exist.")
            if data.get("format") == "code" and strategy(data, self._classes) == "execute":
                missing = [key for key in ("expected_solution", "tests") if not data.get(key)]
                if missing:
                    self.report("code_execution_reference_present", item.path,
                                f"{item.id} is checked by running its tests (strategy `execute`), but "
                                f"it has no {' and no '.join(missing)} to run. Add "
                                f"{'them' if len(missing) > 1 else 'it'}, or set "
                                "`evaluation_strategy: persona_attempt` on the item.")
