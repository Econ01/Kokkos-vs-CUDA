#!/usr/bin/env python3
"""Generate the README project-progress SVG using only the standard library."""

import argparse
import base64
import html
import json
import sys
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "docs" / "project_status.json"
DEFAULT_OUTPUT = ROOT / "docs" / "assets" / "project-progress.svg"
DEFAULT_FONT = ROOT / "docs" / "assets" / "fonts" / "GoogleSansFlex-Rounded100-Latin.woff2"

TEXT = "#202124"
SECONDARY_TEXT = "#5F6368"
CONNECTOR = "#DADCE0"
PRIMARY_TEAL = "#00796B"

STATUSES = {
    "complete": {"label": "Complete", "color": "#1E8E3E"},
    "in_progress": {"label": "In progress", "color": PRIMARY_TEAL},
    "not_started": {"label": "Not started", "color": SECONDARY_TEXT},
    "blocked": {"label": "Blocked", "color": "#B06000"},
    "needs_attention": {"label": "Needs attention", "color": "#D93025"},
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="status JSON path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="generated SVG path")
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT, help="embedded WOFF2 font path")
    parser.add_argument(
        "--check",
        action="store_true",
        help="check that the output is current without rewriting it",
    )
    return parser.parse_args()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_item(item, context):
    require(isinstance(item.get("name"), str) and item["name"].strip(), f"{context}: missing name")
    require(item.get("status") in STATUSES, f"{context}: invalid status {item.get('status')!r}")
    require(isinstance(item.get("detail"), str) and item["detail"].strip(), f"{context}: missing detail")


def load_status(path):
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    require(data.get("schema_version") == 1, "Unsupported status schema")
    require(
        isinstance(data.get("next_milestone"), str) and data["next_milestone"].strip(),
        "Missing next milestone",
    )
    phases = data.get("phases")
    kernels = data.get("kernels")
    require(isinstance(phases, list) and len(phases) == 7, "Expected seven environment phases")
    require(isinstance(kernels, list) and len(kernels) == 3, "Expected three kernels")

    for index, phase in enumerate(phases):
        require(phase.get("number") == index, f"Phase {index}: unexpected phase number")
        validate_item(phase, f"Phase {index}")
    for index, kernel in enumerate(kernels, start=1):
        validate_item(kernel, f"Kernel {index}")
        for field in ("baseline", "tuned", "analysis"):
            require(kernel.get(field) in STATUSES, f"Kernel {index}: invalid {field} status")

    final = data.get("final")
    require(isinstance(final, dict), "Missing final reproduction status")
    validate_item(final, "Final reproduction")
    require(final.get("cross_kernel_analysis") in STATUSES, "Invalid cross-kernel analysis status")

    current_phase = data.get("current_phase")
    if current_phase is not None:
        require(isinstance(current_phase, int) and 0 <= current_phase <= 10, "Invalid current phase")
        if current_phase < len(phases):
            current_status = phases[current_phase]["status"]
        elif current_phase < 10:
            current_status = kernels[current_phase - 7]["status"]
        else:
            current_status = final["status"]
        require(current_status == "in_progress", "The current phase must have in_progress status")

    return data


def fmt(value):
    return f"{value:.2f}".rstrip("0").rstrip(".")


def esc(value):
    return html.escape(str(value), quote=True)


def add_connector(parts, start_x, end_x, y, completed):
    color = STATUSES["complete"]["color"] if completed else CONNECTOR
    parts.append(
        f'<line x1="{fmt(start_x)}" y1="{y}" x2="{fmt(end_x)}" y2="{y}" '
        f'stroke="{color}" stroke-width="4" stroke-linecap="round"/>'
    )


def add_step(parts, x, y, number, name, status_key, wrap_width):
    status = STATUSES[status_key]
    color = status["color"]
    radius = 20

    if status_key in {"complete", "in_progress", "needs_attention"}:
        parts.append(f'<circle cx="{fmt(x)}" cy="{y}" r="{radius}" fill="{color}"/>')
    else:
        parts.append(
            f'<circle cx="{fmt(x)}" cy="{y}" r="{radius}" fill="#FFFFFF" '
            f'stroke="{color if status_key == "blocked" else CONNECTOR}" stroke-width="3"/>'
        )

    if status_key == "complete":
        parts.append(
            f'<path d="M {fmt(x - 7)} {y} l 4.5 4.5 l 8.5 -9" fill="none" '
            'stroke="#FFFFFF" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    else:
        number_color = "#FFFFFF" if status_key in {"in_progress", "needs_attention"} else color
        parts.append(
            f'<text x="{fmt(x)}" y="{y + 5}" text-anchor="middle" class="step-number" '
            f'fill="{number_color}">{number}</text>'
        )

    lines = textwrap.wrap(name, width=wrap_width, break_long_words=False, break_on_hyphens=False)
    if len(lines) > 2:
        lines = [lines[0], " ".join(lines[1:])]
    for index, line in enumerate(lines):
        parts.append(
            f'<text x="{fmt(x)}" y="{y + 46 + index * 18}" text-anchor="middle" '
            f'class="step-name">{esc(line)}</text>'
        )

    parts.append(
        f'<text x="{fmt(x)}" y="{y + 88}" text-anchor="middle" class="step-status" '
        f'fill="{color}">{status["label"]}</text>'
    )


def generate_svg(data, font_data):
    width = 1440
    height = 440
    margin = 96
    usable_width = width - 2 * margin
    encoded_font = base64.b64encode(font_data).decode("ascii")
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="pipeline-title pipeline-desc">',
        '<title id="pipeline-title">Project pipeline progress</title>',
    ]

    descriptions = [
        f"Phase {phase['number']} {phase['name']}: {STATUSES[phase['status']]['label'].lower()}"
        for phase in data["phases"]
    ]
    descriptions.extend(
        f"{kernel['name']}: {STATUSES[kernel['status']]['label'].lower()}"
        for kernel in data["kernels"]
    )
    descriptions.append(
        f"{data['final']['name']}: {STATUSES[data['final']['status']]['label'].lower()}"
    )
    parts.append(f'<desc id="pipeline-desc">{esc("; ".join(descriptions))}</desc>')
    parts.extend(
        [
            "<style>",
            "/* Embedded instance: ROND 100, opsz 18, wdth 100, slnt 0; weight axis retained. */",
            "@font-face {",
            '  font-family: "Google Sans Flex";',
            f'  src: url("data:font/woff2;base64,{encoded_font}") format("woff2");',
            "  font-style: normal;",
            "  font-weight: 1 1000;",
            "}",
            "text {",
            '  font-family: "Google Sans Flex", Arial, Helvetica, sans-serif;',
            '  font-variation-settings: "ROND" 100, "opsz" 18;',
            "}",
            f".title {{ font-size: 30px; font-weight: 600; fill: {TEXT}; }}",
            f".section {{ font-size: 20px; font-weight: 600; fill: {SECONDARY_TEXT}; }}",
            ".step-number { font-size: 16px; font-weight: 600; }",
            f".step-name {{ font-size: 17px; font-weight: 500; fill: {TEXT}; }}",
            ".step-status { font-size: 15px; font-weight: 500; }",
            "</style>",
            f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>',
            '<text x="48" y="44" class="title">Project pipeline</text>',
            '<text x="48" y="82" class="section">Environment readiness</text>',
        ]
    )

    env_y = 136
    env_centers = [margin + index * usable_width / 6 for index in range(7)]
    for index in range(6):
        add_connector(
            parts,
            env_centers[index] + 25,
            env_centers[index + 1] - 25,
            env_y,
            completed=data["phases"][index]["status"] == "complete",
        )
    for phase, x in zip(data["phases"], env_centers):
        add_step(parts, x, env_y, phase["number"], phase["name"], phase["status"], wrap_width=19)

    parts.append('<text x="48" y="294" class="section">Kernels and reproduction</text>')
    kernel_y = 330
    kernel_items = list(data["kernels"]) + [data["final"]]
    kernel_centers = [margin + index * usable_width / 3 for index in range(4)]
    for index in range(3):
        add_connector(
            parts,
            kernel_centers[index] + 25,
            kernel_centers[index + 1] - 25,
            kernel_y,
            completed=kernel_items[index]["status"] == "complete",
        )
    for index, (item, x) in enumerate(zip(kernel_items, kernel_centers)):
        add_step(parts, x, kernel_y, index + 1, item["name"], item["status"], wrap_width=25)

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    args = parse_args()
    try:
        data = load_status(args.input)
        font_data = args.font.read_bytes()
        require(font_data.startswith(b"wOF2"), f"Not a WOFF2 font: {args.font}")
        svg = generate_svg(data, font_data)
        if args.check:
            if not args.output.exists() or args.output.read_text(encoding="utf-8") != svg:
                print(f"Outdated SVG: {args.output}", file=sys.stderr)
                return 1
            print(f"SVG is current: {args.output}")
            return 0

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(svg, encoding="utf-8")
        print(f"Generated {args.output}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
