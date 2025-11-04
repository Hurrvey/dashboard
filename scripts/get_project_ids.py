"""Resolve configured projects to their registry IDs."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable


def _prepare_environment(project_root: str) -> None:
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def _resolve_project_ids(projects: Iterable[str]) -> list[str]:
    from app.services.project_registry import project_registry

    ids: list[str] = []

    for project in projects:
        project = project.strip()
        if not project:
            continue

        entry = project_registry.get_entry(project)
        if entry:
            ids.append(entry.project_id)
        else:
            ids.append(project_registry.generate_project_id(project))

    # Deduplicate while preserving order
    seen = set()
    unique_ids: list[str] = []
    for project_id in ids:
        if project_id and project_id not in seen:
            seen.add(project_id)
            unique_ids.append(project_id)

    return unique_ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Get project IDs for dashboard query")
    parser.add_argument(
        "--projects",
        help="Comma-separated project identifiers. Default: read from DEFAULT_PROJECTS",
        default="",
    )

    args = parser.parse_args(argv)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _prepare_environment(project_root)

    from get_default_projects import load_default_projects

    if args.projects:
        projects = [item.strip() for item in args.projects.split(',') if item.strip()]
    else:
        projects = load_default_projects()

    project_ids = _resolve_project_ids(projects)
    sys.stdout.write(','.join(project_ids))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

