"""项目文件收集工具"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Iterator, List


logger = logging.getLogger(__name__)

DEFAULT_IGNORE_DIRS = {
    '.git', '.hg', '.svn', '.idea', '.vscode', '__pycache__', 'node_modules', 'dist', 'build', '.mypy_cache'
}

TEXT_FILE_EXTS = {
    '.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.yml', '.yaml', '.md', '.txt', '.html', '.css', '.scss',
    '.vue', '.java', '.rb', '.go', '.rs', '.swift', '.kt', '.kts', '.c', '.cc', '.cpp', '.h', '.hpp'
}

CODE_FILE_EXTS = {
    '.c', '.cc', '.cpp', '.cxx', '.h', '.hh', '.hpp', '.hxx',
    '.m', '.mm', '.swift', '.go', '.rs', '.kt', '.kts', '.java', '.scala', '.groovy',
    '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.vue', '.svelte',
    '.py', '.pyw', '.rb', '.php', '.pl', '.pm', '.lua', '.sql', '.r', '.jl', '.dart', '.cs', '.fs', '.fsx', '.vb',
    '.sh', '.bash', '.zsh', '.fish', '.ps1', '.psm1', '.coffee', '.clj', '.cljs'
}

EXTENSIONLESS_ALLOW = {'dockerfile', 'makefile', 'router_rule'}


@dataclass
class ProjectFile:
    path: str
    content: str
    line_count: int
    size: int


def collect_project_files(
    project_root: str,
    max_files: int | None = 30,
    max_file_size: int | None = 200 * 1024,
    max_characters: int | None = 6000,
    include_exts: set[str] | None = None,
    ignore_dirs: set[str] | None = None
) -> List[ProjectFile]:
    project_root = os.path.abspath(project_root)
    include_exts = include_exts or CODE_FILE_EXTS
    ignore_dirs = ignore_dirs or DEFAULT_IGNORE_DIRS

    files: List[ProjectFile] = []

    try:
        for file_path in _iter_files(project_root, ignore_dirs):
            if max_files is not None and len(files) >= max_files:
                break

            try:
                rel_path = os.path.relpath(file_path, project_root)
                if not _should_include(rel_path, include_exts):
                    continue

                size = os.path.getsize(file_path)
                if max_file_size is not None and size > max_file_size:
                    continue

                with open(file_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read(max_characters or -1)

                if not content.strip():
                    continue

                line_count = content.count('\n') + 1
                files.append(ProjectFile(rel_path, content, line_count, size))
            except Exception as exc:
                logger.debug("读取文件失败 %s: %s", file_path, exc)
                continue
    except FileNotFoundError:
        logger.warning("项目路径不存在: %s", project_root)

    return files


def _iter_files(root: str, ignore_dirs: set[str]) -> Iterator[str]:
    for current_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for filename in files:
            yield os.path.join(current_dir, filename)


def _should_include(relative_path: str, include_exts: set[str]) -> bool:
    _, ext = os.path.splitext(relative_path)
    if ext.lower() in include_exts:
        return True
    if not ext:
        base = os.path.basename(relative_path).lower()
        return base in EXTENSIONLESS_ALLOW
    return False


