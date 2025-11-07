"""项目存储与映射管理"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import shutil
from dataclasses import dataclass
from threading import RLock
from typing import Dict, Optional


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProjectEntry:
    """项目注册信息"""

    identifier: str
    project_id: str
    path: str


class ProjectRegistry:
    """负责记录项目标识与本地存储路径的映射, 并在需要时创建本地副本"""

    def __init__(self, workspace_dir: str = './repos') -> None:
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.mirror_dir = os.path.join(self.workspace_dir, '_mirror')
        self.registry_path = os.path.join(self.workspace_dir, '_registry.json')

        os.makedirs(self.workspace_dir, exist_ok=True)
        os.makedirs(self.mirror_dir, exist_ok=True)

        self._lock = RLock()
        self._registry: Dict[str, Dict[str, str]] = self._load_registry()

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------
    def get_local_path(self, identifier: str) -> Optional[str]:
        entry = self.get_entry(identifier)
        return entry.path if entry else None

    def get_entry(self, identifier: str) -> Optional[ProjectEntry]:
        if not identifier:
            return None
        normalized = self._normalize(identifier)
        with self._lock:
            data = self._registry.get(normalized)
            if not data:
                return None
            path = data.get('path')
            project_id = data.get('id')
            if not path or not project_id:
                return None
            return ProjectEntry(normalized, project_id, path)

    def generate_project_id(self, seed: str) -> str:
        """
        生成项目唯一ID（12位哈希值）
        
        Args:
            seed: 用于生成哈希的种子（通常是项目URL或路径）
            
        Returns:
            12位MD5哈希值，例如: 59c55330e4d2
        """
        seed = seed.strip()
        digest = hashlib.md5(seed.encode('utf-8')).hexdigest()[:12]
        return digest

    def register_identifier(self, identifier: str, local_path: str, project_id: Optional[str] = None) -> None:
        if not identifier or not local_path:
            return

        normalized = self._normalize(identifier)
        if not normalized:
            return

        local_path = os.path.abspath(local_path)
        project_id = project_id or self._find_project_id_by_path(local_path) or self.generate_project_id(normalized)

        with self._lock:
            need_save = False

            current = self._registry.get(normalized)
            if not (current and current.get('path') == local_path and current.get('id') == project_id):
                self._registry[normalized] = {'path': local_path, 'id': project_id}
                need_save = True
                logger.debug("项目映射: %s -> %s (%s)", normalized, local_path, project_id)

            if project_id and project_id != normalized:
                alias_current = self._registry.get(project_id)
                if not (alias_current and alias_current.get('path') == local_path and alias_current.get('id') == project_id):
                    self._registry[project_id] = {'path': local_path, 'id': project_id}
                    need_save = True
                    logger.debug("项目别名映射: %s -> %s", project_id, local_path)

            if need_save:
                self._save_registry()

    def ensure_local_copy(
        self,
        identifier: str,
        source_path: str,
        force_refresh: bool = False,
        project_id: Optional[str] = None,
        aliases: Optional[list[str]] = None,
    ) -> ProjectEntry:
        """确保项目在工作目录内有一份完整副本, 返回本地路径及唯一标识"""

        source_abs = os.path.abspath(source_path)
        project_id = project_id or self._find_project_id_by_path(source_abs) or self.generate_project_id(identifier or source_abs)

        if source_abs.startswith(self.workspace_dir):
            target_path = source_abs
        else:
            target_name = project_id
            target_path = os.path.join(self.mirror_dir, target_name)

            if force_refresh and os.path.exists(target_path):
                shutil.rmtree(target_path, ignore_errors=True)

            if not os.path.exists(target_path):
                logger.info("复制项目到本地缓存: %s -> %s", source_abs, target_path)
                shutil.copytree(
                    source_abs,
                    target_path,
                    dirs_exist_ok=False,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store')
                )

        self.register_identifier(identifier, target_path, project_id)

        if aliases:
            for alias in aliases:
                self.register_identifier(alias, target_path, project_id)

        return ProjectEntry(identifier=self._normalize(identifier), project_id=project_id, path=os.path.abspath(target_path))

    def prepare_repo_workspace(self, identifier: str) -> ProjectEntry:
        """为远程仓库分配或获取本地工作目录"""

        normalized = self._normalize(identifier)

        with self._lock:
            data = self._registry.get(normalized)
            if data and data.get('path') and os.path.exists(data['path']):
                return ProjectEntry(identifier=normalized, project_id=data['id'], path=data['path'])

        project_id = self.generate_project_id(identifier)
        repo_path = os.path.abspath(os.path.join(self.workspace_dir, project_id))
        return ProjectEntry(identifier=normalized, project_id=project_id, path=repo_path)

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    def _normalize(self, identifier: str) -> str:
        return identifier.strip()

    def _load_registry(self) -> Dict[str, Dict[str, str]]:
        if not os.path.exists(self.registry_path):
            return {}
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
        except Exception as exc:
            logger.warning("加载项目映射文件失败: %s", exc)
            return {}

        if not isinstance(data, dict):
            return {}

        registry: Dict[str, Dict[str, str]] = {}
        for key, value in data.items():
            normalized = self._normalize(key)
            if not normalized:
                continue

            path: Optional[str] = None
            project_id: Optional[str] = None

            if isinstance(value, dict):
                path = value.get('path') or value.get('local_path')
                project_id = value.get('id') or value.get('project_id')
            elif isinstance(value, str):
                path = value

            if not path:
                continue

            abs_path = os.path.abspath(path)
            if not project_id:
                project_id = self.generate_project_id(normalized)

            registry[normalized] = {'path': abs_path, 'id': project_id}

        return registry

    def _save_registry(self) -> None:
        try:
            with open(self.registry_path, 'w', encoding='utf-8') as fp:
                json.dump(self._registry, fp, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.error("保存项目映射文件失败: %s", exc)

    def _find_project_id_by_path(self, local_path: str) -> Optional[str]:
        local_path = os.path.abspath(local_path)
        with self._lock:
            for data in self._registry.values():
                if os.path.abspath(data.get('path', '')) == local_path and data.get('id'):
                    return data['id']
        return None


# 全局实例, 供其它模块直接使用
project_registry = ProjectRegistry()


