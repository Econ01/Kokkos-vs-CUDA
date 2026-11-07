#!/usr/bin/env python3
"""Update the generated project-progress section in README.md."""

import argparse
import re
import sys
from pathlib import Path

from generate_progress_svg import load_status


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "docs" / "project_status.json"
DEFAULT_README = ROOT / "README.md"
START = "<!-- PROGRESS_DASHBOARD:START -->"
END = "<!-- PROGRESS_DASHBOARD:END -->"

ICONS = {
    "complete": "✅",
    "in_progress": "🔄",
    "not_started": "⬜",
    "blocked": "🔒",
    "needs_attention": "⚠️",
}
LABELS = {
    "complete": "Complete",
    "in_progress": "In progress",
    "not_started": "Not started",
    "blocked": "Blocked",
    "needs_attention": "Needs attention",
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="status JSON path")
    parser.add_argument("--readme", type=Path, default=DEFAULT_README, help="README path")
    parser.add_argument(
        "--check",
        action="store_true",
        help="check that the dashboard is current without rewriting it",
    )
    return parser.parse_args()


def status_text(status):
    return f"{ICONS[status]} {LABELS[status]}"


def render_dashboard(data):
    current_phase = data.get("current_phase")
    if current_phase is None:
        focus = "Project complete"
        current_status = "complete"
    elif current_phase < len(data["phases"]):
        current_item = data["phases"][current_phase]
        focus = f"Phase {current_phase} — {current_item['name']}"
        current_status = current_item["status"]
    elif current_phase < 10:
        current_item = data["kernels"][current_phase - 7]
        focus = f"Phase {current_phase} — {current_item['name']}"
        current_status = current_item["status"]
    else:
        current_item = data["final"]
        focus = f"Phase 10 — {current_item['name']}"
        current_status = current_item["status"]
    alt = f"Project pipeline progress: {focus} is {LABELS[current_status].lower()}"

    lines = [
        START,
        f"**Current focus:** {focus}<br>",
        f"**Next milestone:** {data['next_milestone']}",
        "",
        "**Status legend:** ✅ Complete · 🔄 In progress · ⬜ Not started · 🔒 Blocked · ⚠️ Needs attention",
        "",
        f"[![{alt}](docs/assets/project-progress.svg)](docs/PIPELINE.md)",
        "",
        "Update this dashboard with `python3 scripts/update_progress_dashboard.py` and the visual with `python3 scripts/generate_progress_svg.py`.",
        "",
        "### Environment readiness",
        "",
        "| Phase | Milestone | Status | Evidence or next step |",
        "| --- | --- | --- | --- |",
    ]

    for phase in data["phases"]:
        lines.append(
            f"| {phase['number']} | {phase['name']} | {status_text(phase['status'])} | {phase['detail']} |"
        )

    lines.extend(
        [
            "",
            "### Kernel progress",
            "",
            "| Kernel | Baseline | Tuned | Analysis | Overall status |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for kernel in data["kernels"]:
        lines.append(
            f"| {kernel['name']} | {ICONS[kernel['baseline']]} | {ICONS[kernel['tuned']]} | "
            f"{ICONS[kernel['analysis']]} | {kernel['detail']} |"
        )

    final = data["final"]
    lines.extend(
        [
            "",
            f"**Final instructor reproduction:** {status_text(final['status'])}<br>",
            f"**Final cross-kernel analysis:** {status_text(final['cross_kernel_analysis'])}",
            END,
        ]
    )
    return "\n".join(lines) + "\n"


def replace_dashboard(readme_text, rendered):
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.DOTALL)
    matches = list(pattern.finditer(readme_text))
    if len(matches) != 1:
        raise ValueError("README must contain exactly one progress-dashboard marker pair")
    return pattern.sub(lambda _: rendered, readme_text, count=1)


def main():
    args = parse_args()
    try:
        data = load_status(args.input)
        original = args.readme.read_text(encoding="utf-8")
        updated = replace_dashboard(original, render_dashboard(data))
        if args.check:
            if original != updated:
                print(f"Outdated dashboard: {args.readme}", file=sys.stderr)
                return 1
            print(f"Dashboard is current: {args.readme}")
            return 0

        args.readme.write_text(updated, encoding="utf-8")
        print(f"Updated {args.readme}")
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
