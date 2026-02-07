"""Generate docs from command/help and API source-of-truth."""

from __future__ import annotations

import argparse
import platform
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI
from fastapi.routing import APIRoute

from dashboard_api.server import create_app

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE_OUTPUT = REPO_ROOT / "docs" / "GENERATED_REFERENCE.md"
DEFAULT_DIAGRAM_OUTPUT = REPO_ROOT / "docs" / "GENERATED_API_DIAGRAMS.md"

HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}

DOMAIN_LABELS: dict[str, str] = {
    "chat": "Chat Experience",
    "agent_surface": "Agent Surface",
    "runtime_ops": "Runtime Operations",
    "diagnostics": "Diagnostics & Verification",
    "usage": "Usage & Quotas",
    "telemetry": "Telemetry",
    "health": "Health",
    "other": "Other",
}


@dataclass(frozen=True)
class RouteRow:
    methods: str
    path: str
    handler: str
    tags: str


@dataclass(frozen=True)
class OpenAPIOperation:
    method: str
    path: str
    operation_id: str
    tags: tuple[str, ...] = ()
    handler: str = "-"


def _normalize_output(text: str) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    normalized: list[str] = []
    for line in lines:
        stripped = line.strip()
        if len(stripped) >= 2 and stripped.startswith('"') and stripped.endswith('"'):
            normalized.append(stripped[1:-1])
        else:
            normalized.append(line.rstrip())
    return "\n".join(normalized).strip() + "\n"


def _run_command(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return _normalize_output(result.stdout)


def _capture_make_help() -> str:
    return _run_command(["make", "help"])


def _capture_powershell_help() -> str:
    candidates: list[list[str]] = []

    if platform.system() == "Windows":
        candidates.append(["pwsh", "-File", "./make.ps1", "help"])
        candidates.append(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", "./make.ps1", "help"]
        )
    else:
        candidates.append(["pwsh", "-File", "./make.ps1", "help"])

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            return _run_command(candidate)
        except Exception as exc:  # pragma: no cover - fallback chain
            last_error = exc

    raise RuntimeError("Failed to capture make.ps1 help output") from last_error


def _route_rows() -> list[RouteRow]:
    app = create_app()
    rows: list[RouteRow] = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        if not (route.path.startswith("/api") or route.path == "/health"):
            continue

        methods = sorted(method for method in route.methods if method not in {"HEAD", "OPTIONS"})
        method_text = ", ".join(methods)
        tags = ", ".join(str(tag) for tag in route.tags) if route.tags else "-"
        rows.append(RouteRow(method_text, route.path, route.name, tags))

    rows.sort(key=lambda row: (row.path, row.methods))
    return rows


def _openapi_operations() -> list[OpenAPIOperation]:
    app = create_app()
    schema = app.openapi()
    operations: list[OpenAPIOperation] = []
    handler_lookup = _route_handler_lookup(app)

    for path, entry in schema.get("paths", {}).items():
        if not isinstance(entry, dict):
            continue

        if not (path.startswith("/api") or path == "/health"):
            continue

        for method, details in entry.items():
            method_upper = method.upper()
            if method_upper not in HTTP_METHODS:
                continue
            if not isinstance(details, dict):
                continue

            operation_id = str(details.get("operationId", "-"))
            tags = tuple(str(tag) for tag in details.get("tags", []))
            operations.append(
                OpenAPIOperation(
                    method=method_upper,
                    path=path,
                    operation_id=operation_id,
                    tags=tags,
                    handler=handler_lookup.get((method_upper, path), "-"),
                )
            )

    operations.sort(key=lambda item: (item.path, item.method))
    return operations


def _domain_id_for_path(path: str) -> str:
    if path == "/health":
        return "health"

    parts = path.split("/")
    if len(parts) < 3:
        return "other"

    segment = parts[2]
    if segment in {"agents", "skills"}:
        return "agent_surface"
    if segment == "chat":
        return "chat"
    if segment in {"docker", "logs", "artifacts"}:
        return "runtime_ops"
    if segment in {"status", "verify", "system", "models", "diagnostics", "benchmark"}:
        return "diagnostics"
    if segment == "usage":
        return "usage"
    if segment == "telemetry":
        return "telemetry"
    return "other"


def _escape_mermaid_label(value: str) -> str:
    return value.replace('"', "'")


def _normalize_path(path: str) -> str:
    return re.sub(r"{([^}:]+):[^}]+}", r"{\1}", path)


def _route_handler_lookup(app: FastAPI) -> dict[tuple[str, str], str]:
    lookup: dict[tuple[str, str], str] = {}
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        normalized_path = _normalize_path(route.path)
        for method in route.methods:
            if method in {"HEAD", "OPTIONS"}:
                continue
            lookup[(method, normalized_path)] = route.name
    return lookup


def _group_by_domain(
    operations: list[OpenAPIOperation],
) -> dict[str, list[OpenAPIOperation]]:
    grouped: dict[str, list[OpenAPIOperation]] = defaultdict(list)
    for operation in operations:
        grouped[_domain_id_for_path(operation.path)].append(operation)
    return dict(sorted(grouped.items(), key=lambda item: DOMAIN_LABELS.get(item[0], item[0])))


def _render_domain_surface_diagram(
    grouped_operations: dict[str, list[OpenAPIOperation]],
) -> list[str]:
    lines: list[str] = ["```mermaid", "flowchart LR"]
    endpoint_index = 0

    for domain_index, (domain_id, operations) in enumerate(grouped_operations.items()):
        domain_node = f"D{domain_index}"
        domain_label = _escape_mermaid_label(DOMAIN_LABELS.get(domain_id, DOMAIN_LABELS["other"]))
        lines.append(f'    {domain_node}["{domain_label}"]')

        for operation in operations:
            endpoint_node = f"E{endpoint_index}"
            endpoint_index += 1
            endpoint_label = _escape_mermaid_label(f"{operation.method} {operation.path}")
            lines.append(f'    {domain_node} --> {endpoint_node}["{endpoint_label}"]')

    lines.append("```")
    return lines


def _render_reference_markdown(make_help: str, ps_help: str) -> str:
    route_rows = _route_rows()

    lines: list[str] = [
        "# Generated Reference",
        "",
        "> Generated by `scripts/generate_reference_docs.py`. Do not edit manually.",
        "",
        "## API Endpoint Table",
        "",
        "| Methods | Path | Handler | Tags |",
        "| --- | --- | --- | --- |",
    ]

    for row in route_rows:
        lines.append(f"| `{row.methods}` | `{row.path}` | `{row.handler}` | `{row.tags}` |")

    lines.extend(
        [
            "",
            "## Make Help Output",
            "",
            "```text",
            make_help.rstrip("\n"),
            "```",
            "",
            "## PowerShell Help Output",
            "",
            "```text",
            ps_help.rstrip("\n"),
            "```",
            "",
        ]
    )

    return "\n".join(lines)


def _render_api_diagram_markdown(operations: list[OpenAPIOperation]) -> str:
    grouped_operations = _group_by_domain(operations)

    lines: list[str] = [
        "# Generated API Diagrams",
        "",
        "> Generated from `dashboard_api.server.create_app().openapi()` by `scripts/generate_reference_docs.py`. Do not edit manually.",
        "",
        "## Domain -> Endpoint Surface",
        "",
    ]
    lines.extend(_render_domain_surface_diagram(grouped_operations))
    lines.extend(["", "## Domain Summary", "", "| Domain | Operations | Methods |", "| --- | ---: | --- |"])

    for domain_id, domain_operations in grouped_operations.items():
        methods = sorted({item.method for item in domain_operations})
        method_text = ", ".join(methods)
        lines.append(
            f"| `{DOMAIN_LABELS.get(domain_id, DOMAIN_LABELS['other'])}` | {len(domain_operations)} | `{method_text}` |"
        )

    lines.extend(
        [
            "",
            "## Operation Matrix",
            "",
            "| Domain | Method | Path | Handler | Operation ID | Tags |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )

    for domain_id, domain_operations in grouped_operations.items():
        domain_label = DOMAIN_LABELS.get(domain_id, DOMAIN_LABELS["other"])
        for operation in domain_operations:
            tags = ", ".join(operation.tags) if operation.tags else "-"
            lines.append(
                f"| `{domain_label}` | `{operation.method}` | `{operation.path}` | `{operation.handler}` | `{operation.operation_id}` | `{tags}` |"
            )

    lines.append("")
    return "\n".join(lines)


def _resolve_output(output: Path) -> Path:
    return output if output.is_absolute() else REPO_ROOT / output


def _check_artifact(path: Path, rendered: str, label: str) -> int:
    if not path.exists():
        print(f"Generated {label} missing: {path}")
        return 1

    current = path.read_text(encoding="utf-8")
    if current != rendered:
        print(f"Generated {label} is stale: {path}")
        print("Run: uv run python scripts/generate_reference_docs.py")
        return 1

    print(f"Generated {label} is up to date: {path}")
    return 0


def generate(check: bool, reference_output: Path, diagram_output: Path) -> int:
    make_help = _capture_make_help()
    ps_help = _capture_powershell_help()
    reference_rendered = _render_reference_markdown(make_help=make_help, ps_help=ps_help)
    diagram_rendered = _render_api_diagram_markdown(_openapi_operations())

    if check:
        return max(
            _check_artifact(reference_output, reference_rendered, "reference docs"),
            _check_artifact(diagram_output, diagram_rendered, "API diagrams"),
        )

    reference_output.write_text(reference_rendered, encoding="utf-8")
    diagram_output.write_text(diagram_rendered, encoding="utf-8")
    print(f"Wrote generated reference docs: {reference_output}")
    print(f"Wrote generated API diagrams: {diagram_output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or validate docs reference artifacts.")
    parser.add_argument("--check", action="store_true", help="Fail if generated output is stale.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REFERENCE_OUTPUT,
        help=f"Reference output file path (default: {DEFAULT_REFERENCE_OUTPUT})",
    )
    parser.add_argument(
        "--diagram-output",
        type=Path,
        default=DEFAULT_DIAGRAM_OUTPUT,
        help=f"API diagram output file path (default: {DEFAULT_DIAGRAM_OUTPUT})",
    )
    args = parser.parse_args()

    return generate(
        check=args.check,
        reference_output=_resolve_output(args.output),
        diagram_output=_resolve_output(args.diagram_output),
    )


if __name__ == "__main__":
    sys.exit(main())
