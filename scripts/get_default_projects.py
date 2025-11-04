"""Utility to read DEFAULT_PROJECTS from .env and emit a comma-separated list."""

from __future__ import annotations

import json
import os
import sys
from typing import Iterable

from dotenv import load_dotenv


def load_default_projects() -> list[str]:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    env_path = os.path.join(project_root, '.env')

    # load_dotenv silently ignores missing files; keep existing env vars intact
    load_dotenv(env_path)

    raw_value = os.getenv('DEFAULT_PROJECTS', '')
    if not raw_value:
        projects = _load_from_projects_config(project_root)
        return projects

    projects: list[str] = []

    try:
        decoded = json.loads(raw_value)
    except json.JSONDecodeError:
        decoded = None

    if isinstance(decoded, dict):
        projects = [str(v).strip() for v in decoded.values() if str(v).strip()]
    elif isinstance(decoded, (list, tuple)):
        projects = [str(item).strip() for item in decoded if str(item).strip()]
    elif isinstance(decoded, str) and decoded.strip():
        projects = [decoded.strip()]
    else:
        projects = [item.strip() for item in raw_value.split(',') if item.strip()]

    projects = [project for project in projects if project]

    # Deduplicate while preserving order
    seen = set()
    unique_projects: list[str] = []
    for project in projects:
        if project and project not in seen:
            seen.add(project)
            unique_projects.append(project)

    if not unique_projects:
        unique_projects = _load_from_projects_config(project_root)

    return unique_projects


def _load_from_projects_config(project_root: str) -> list[str]:
    try:
        from app.config.projects import projects_config
    except Exception:
        return []

    projects: list[str] = []
    for name, value in projects_config.list_projects().items():
        value = value.strip()
        if not value:
            continue

        lower_value = value.lower()
        if lower_value.startswith(('http://', 'https://', 'git@', 'ssh://', 'git://')):
            projects.append(value)
            continue

        candidate = value
        if not os.path.isabs(candidate):
            candidate = os.path.normpath(os.path.join(project_root, candidate))

        if os.path.exists(candidate):
            projects.append(name)

    return projects


def main() -> int:
    projects = load_default_projects()
    sys.stdout.write(','.join(projects))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

