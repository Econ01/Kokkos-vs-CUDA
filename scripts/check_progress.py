#!/usr/bin/env python3
"""Validate project-status sources and generated progress artifacts."""

import argparse
import json
import re
import sys
from pathlib import Path

from generate_progress_svg import DEFAULT_FONT, DEFAULT_OUTPUT, generate_svg, load_status
from update_progress_dashboard import DEFAULT_README, render_dashboard, replace_dashboard


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "docs" / "PIPELINE.md"
PHASE_HEADING = re.compile(r"^## Phase (\d+) — .+$", re.MULTILINE)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "docs" / "project_status.json")
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="validate JSON and checklist consistency without requiring current generated files",
    )
    return parser.parse_args()


def phase_sections(text):
    matches = list(PHASE_HEADING.finditer(text))
    sections = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[int(match.group(1))] = text[match.end() : end]
    return sections


def checkbox_counts(section):
    checked = len(re.findall(r"^- \[x\]", section, re.MULTILINE))
    unchecked = len(re.findall(r"^- \[ \]", section, re.MULTILINE))
    return checked, unchecked


def expected_kernel_status(kernel):
    stages = [kernel["baseline"], kernel["tuned"], kernel["analysis"]]
    if all(status == "complete" for status in stages):
        return "complete"
    if all(status == "not_started" for status in stages):
        return "not_started"
    if all(status == "blocked" for status in stages):
        return "blocked"
    if "needs_attention" in stages:
        return "needs_attention"
    if all(status in {"blocked", "not_started"} for status in stages) and "blocked" in stages:
        return "blocked"
    return "in_progress"


def validate_checklist_completion(section, status, context, errors):
    checked, unchecked = checkbox_counts(section)
    if checked == 0 and unchecked == 0:
        errors.append(f"{context}: no checklist items found")
    elif unchecked == 0 and status != "complete":
        errors.append(f"{context}: all items are checked but JSON status is {status}")
    elif status == "complete" and unchecked:
        errors.append(f"{context}: JSON status is complete with {unchecked} unchecked items")
    elif checked and status == "not_started":
        errors.append(f"{context}: checked items exist but JSON status is not_started")


def validate_sources(data):
    errors = []
    text = PIPELINE.read_text(encoding="utf-8")
    sections = phase_sections(text)
    phases = data["phases"]
    current_phase = data.get("current_phase")

    current_matches = re.findall(r"^- Current phase: \*\*Phase (\d+),", text, re.MULTILINE)
    if current_phase is None:
        if current_matches:
            errors.append("Pipeline declares a current phase after project completion")
        incomplete = [phase["status"] != "complete" for phase in phases]
        incomplete.extend(kernel["status"] != "complete" for kernel in data["kernels"])
        incomplete.extend(
            [final["status"] != "complete", final["cross_kernel_analysis"] != "complete"]
        )
        if any(incomplete):
            errors.append("JSON current_phase is null before all project phases are complete")
    elif len(current_matches) != 1:
        errors.append("Pipeline must declare exactly one current phase")
    elif int(current_matches[0]) != current_phase:
        errors.append("Pipeline current phase does not match JSON current_phase")

    for phase in phases:
        number = phase["number"]
        if number not in sections:
            errors.append(f"Phase {number}: missing pipeline section")
            continue
        validate_checklist_completion(sections[number], phase["status"], f"Phase {number}", errors)
        if phase["status"] == "in_progress" and number != current_phase:
            errors.append(f"Phase {number}: in_progress but is not the current phase")
        if number and phase["status"] in {"complete", "in_progress"}:
            if phases[number - 1]["status"] != "complete":
                errors.append(f"Phase {number}: previous phase is not complete")

    if phases[6]["status"] == "complete" and any(
        phases[index]["status"] != "complete" for index in range(1, 6)
    ):
        errors.append("Pre-STREAM gate cannot be complete before Phases 1-5")

    for index, kernel in enumerate(data["kernels"]):
        expected = expected_kernel_status(kernel)
        if kernel["status"] != expected:
            errors.append(
                f"{kernel['name']}: overall status {kernel['status']} does not match stage statuses ({expected})"
            )
        if kernel["tuned"] in {"complete", "in_progress"} and kernel["baseline"] != "complete":
            errors.append(f"{kernel['name']}: tuning started before baseline completion")
        if kernel["analysis"] in {"complete", "in_progress"} and kernel["tuned"] != "complete":
            errors.append(f"{kernel['name']}: analysis started before tuning completion")
        if kernel["status"] == "in_progress" and current_phase != index + 7:
            errors.append(f"{kernel['name']}: in_progress but is not the current kernel")
        if index and kernel["status"] in {"complete", "in_progress"}:
            if data["kernels"][index - 1]["status"] != "complete":
                errors.append(f"{kernel['name']}: previous kernel is not complete")

    for phase_number, kernel in zip((7, 8, 9), data["kernels"]):
        if phase_number in sections:
            validate_checklist_completion(sections[phase_number], kernel["status"], kernel["name"], errors)

    final = data["final"]
    if final["cross_kernel_analysis"] == "complete" and any(
        kernel["status"] != "complete" for kernel in data["kernels"]
    ):
        errors.append("Cross-kernel analysis cannot be complete before all kernels")
    if final["status"] == "complete" and final["cross_kernel_analysis"] != "complete":
        errors.append("Instructor reproduction cannot be complete before cross-kernel analysis")
    if final["status"] == "in_progress" and current_phase != 10:
        errors.append("Instructor reproduction is in_progress but is not the current phase")
    if final["cross_kernel_analysis"] == "in_progress" and current_phase != 10:
        errors.append("Cross-kernel analysis is in_progress but Phase 10 is not current")
    if 10 in sections:
        checked, unchecked = checkbox_counts(sections[10])
        if checked == 0 and unchecked == 0:
            errors.append("Instructor reproduction: no checklist items found")
        elif unchecked == 0 and (
            final["status"] != "complete" or final["cross_kernel_analysis"] != "complete"
        ):
            errors.append("Phase 10 is fully checked but final statuses are not complete")
        elif final["status"] == "complete" and unchecked:
            errors.append("Instructor reproduction is complete with unchecked Phase 10 items")

    return errors


def validate_generated(data):
    errors = []
    readme = DEFAULT_README.read_text(encoding="utf-8")
    if replace_dashboard(readme, render_dashboard(data)) != readme:
        errors.append("README dashboard is outdated")

    font_data = DEFAULT_FONT.read_bytes()
    expected_svg = generate_svg(data, font_data)
    if not DEFAULT_OUTPUT.exists() or DEFAULT_OUTPUT.read_text(encoding="utf-8") != expected_svg:
        errors.append("Project-progress SVG is outdated")
    return errors


def main():
    args = parse_args()
    try:
        data = load_status(args.input)
        errors = validate_sources(data)
        if not args.source_only:
            errors.extend(validate_generated(data))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    if args.source_only:
        print("Progress source checks passed.")
    else:
        print("Progress source and generated-file checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
