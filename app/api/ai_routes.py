"""AI 代码分析相关 API"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, TYPE_CHECKING

from flask import Blueprint, jsonify, request

from app.api.responses import success_response, error_response
from app.settings import Config
from app.services.project_registry import project_registry
from app.services.project_file_collector import collect_project_files, TEXT_FILE_EXTS
CONFIG_FILE_EXTS = {
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.config', '.env', '.lock'
}

CONFIG_FILE_BASENAMES = {
    '.env', '.env.example', '.env.local', 'package.json', 'package-lock.json', 'pnpm-lock.yaml',
    'yarn.lock', 'composer.json', 'composer.lock', 'requirements.txt', 'poetry.lock',
    'pyproject.toml', 'tsconfig.json', 'vite.config.ts', 'webpack.config.js', 'babel.config.js',
    'angular.json', 'rush.json', 'lerna.json', 'nx.json', 'config.json', 'tailwind.config.js',
    'postcss.config.js', 'eslintrc.js', '.eslintrc', '.eslintrc.json', '.prettierrc',
    '.prettierrc.json'
}

CONFIG_DIR_KEYWORDS = ('/config/', '\\config\\', '/configs/', '\\configs\\')


logger = logging.getLogger('code996.api.ai_ratio')

ai_bp = Blueprint('ai', __name__, url_prefix='/api')

if TYPE_CHECKING:  # pragma: no cover
    from app.services.stats_service import StatsService
    from app.services.cache_service import CacheService
    from app.services.ai_analyzer import AIAnalyzer


stats_service: Optional['StatsService'] = None
cache_service: Optional['CacheService'] = None
ai_analyzer: Optional['AIAnalyzer'] = None


def init_ai_services(
    stats_svc: 'StatsService',
    cache_svc: 'CacheService',
    analyzer: 'AIAnalyzer'
) -> None:
    """在应用启动时注入依赖服务"""
    global stats_service, cache_service, ai_analyzer
    stats_service = stats_svc
    cache_service = cache_svc
    ai_analyzer = analyzer
    logger.info("AI Ratio 服务已初始化")


@ai_bp.route('/ai-ratio', methods=['GET'])
def get_ai_ratio():
    """获取 AI 代码比例接口"""
    if stats_service is None:
        logger.error("AI Ratio 服务未初始化")
        return error_response(500, "AI Ratio 服务未初始化")

    repo = request.args.get('repo', '').strip()
    if not repo:
        logger.warning("AI ratio 请求缺少 repo 参数")
        return error_response(400, "参数 repo 不能为空")

    force_refresh = request.args.get('force_refresh', '').lower() in ('1', 'true', 'yes', 'y')

    cache_key = f"ai_ratio:{repo}"
    if cache_service:
        if force_refresh:
            cache_service.delete(cache_key)
        else:
            cached = cache_service.get(cache_key)
            if cached:
                logger.debug("AI ratio 缓存命中: %s", repo)
                return jsonify(cached), 200

    logger.info("AI analyzer status [%s]: %s", repo, ai_analyzer.enabled if ai_analyzer else None)

    try:
        stats_service.get_commits_for_project(repo, force_refresh=force_refresh)
    except FileNotFoundError as exc:
        logger.warning("AI ratio 仓库不存在: %s", exc)
        return error_response(404, str(exc))
    except Exception as exc:  # pragma: no cover
        logger.error("获取仓库 commit 失败 [%s]: %s", repo, exc, exc_info=True)
        return error_response(500, f"获取仓库失败: {exc}")

    entry = project_registry.get_entry(repo)
    if not entry or not os.path.exists(entry.path):
        logger.warning("未找到项目本地映射, 使用默认比例: %s", repo)
        return _return_default_ratio(cache_key)
    local_path = entry.path

    max_files = None
    if ai_analyzer and ai_analyzer.config and ai_analyzer.config.max_files is not None:
        max_files = ai_analyzer.config.max_files
    elif Config.AI_ANALYZER_MAX_FILES is not None:
        max_files = Config.AI_ANALYZER_MAX_FILES

    max_file_size = (ai_analyzer.config.max_file_size if ai_analyzer and ai_analyzer.config else None)
    if max_file_size is None:
        max_file_size = Config.AI_ANALYZER_MAX_FILE_SIZE
    if max_file_size is None:
        max_file_size = 200 * 1024

    max_characters = (ai_analyzer.config.max_characters if ai_analyzer and ai_analyzer.config else None)
    if max_characters is None:
        max_characters = Config.AI_ANALYZER_MAX_CHARACTERS
    if max_characters is None:
        max_characters = 6000

    samples = collect_project_files(
        local_path,
        max_files=max_files,
        max_file_size=max_file_size,
        max_characters=max_characters,
    )
    samples = _filter_samples(samples)
    initial_count = len(samples)
    logger.info("AI ratio initial samples [%s]: %s", repo, initial_count)

    desired_sample_min = min(max_files or 30, 10)

    if len(samples) < desired_sample_min:
        extra_samples = collect_project_files(
            local_path,
            max_files=max_files,
            max_file_size=max_file_size,
            max_characters=max_characters,
            include_exts=TEXT_FILE_EXTS,
        )
        extra_samples = _filter_samples(extra_samples)
        samples = _merge_samples(samples, extra_samples)
        logger.info(
            "AI ratio augmented samples [%s]: initial=%s extra=%s total=%s",
            repo,
            initial_count,
            len(extra_samples),
            len(samples),
        )

    if not samples:
        logger.warning("未能收集到项目文件用于 AI 分析: %s", repo)
        return _return_default_ratio(cache_key)

    ratios = []
    analyzed_files = 0

    if ai_analyzer and ai_analyzer.enabled:
        max_workers = max(1, int(Config.AI_ANALYZER_CONCURRENCY or 5))
        logger.info(
            "开始进行 AI 代码检测: files=%s, concurrency=%s, size_limit=%s, char_limit=%s",
            len(samples),
            max_workers,
            max_file_size,
            max_characters,
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(ai_analyzer.analyze_content, sample.path, sample.content): sample
                for sample in samples
            }

            for future in as_completed(future_map):
                sample = future_map[future]
                try:
                    percentage = future.result()
                except Exception as exc:  # pragma: no cover
                    logger.error("AI 分析执行异常 [%s]: %s", sample.path, exc)
                    continue

                if percentage is None:
                    logger.debug("AI 分析无结果 [%s]", sample.path)
                    continue

                analyzed_files += 1
                ratios.append(percentage)
                logger.debug("AI 分析结果 [%s]: %.2f%%", sample.path, percentage)
    else:
        logger.warning("AIAnalyzer 未启用, 使用默认比例 50%%")

    if ratios:
        avg_ratio = sum(ratios) / len(ratios)
        ai_lines = round(avg_ratio, 2)
        human_lines = round(max(0.0, 100.0 - ai_lines), 2)
    else:
        logger.info("未获得有效 AI 分析结果, 使用默认 50%%")
        return _return_default_ratio(cache_key)

    result = {
        "ai_lines": ai_lines,
        "human_lines": human_lines,
        "projects": 1,
        "total_files": len(samples),
        "sampled_files": len(ratios),
        "analyzed_files": analyzed_files,
        "failed_files": len(samples) - len(ratios),
        "average_ratio": round(avg_ratio, 2),
        "total_weight": len(ratios),
    }

    if cache_service:
        cache_service.set(cache_key, result, ttl=Config.AI_RATIO_CACHE_TTL)

    logger.info(
        "AI 代码比例 [%s]: ai=%s human=%s total=%s analyzed=%s",
        repo,
        ai_lines,
        human_lines,
        result["total_files"],
        result["sampled_files"],
    )
    return jsonify(result), 200


def _return_default_ratio(cache_key: str):
    result = {
        "ai_lines": 50.0,
        "human_lines": 50.0,
        "projects": 1,
        "sampled_files": 0,
        "average_ratio": 50.0,
        "total_weight": 0,
    }

    return jsonify(result), 200


def _filter_samples(samples):
    filtered = []
    skipped = 0

    for sample in samples:
        path_lower = sample.path.lower()
        base_name = os.path.basename(path_lower)
        _, ext = os.path.splitext(base_name)

        if base_name in CONFIG_FILE_BASENAMES:
            skipped += 1
            continue

        if ext in CONFIG_FILE_EXTS:
            skipped += 1
            continue

        if any(keyword in path_lower for keyword in CONFIG_DIR_KEYWORDS):
            skipped += 1
            continue

        filtered.append(sample)

    if skipped:
        logger.debug("AI ratio 过滤配置类文件: total=%s skipped=%s", len(samples), skipped)

    return filtered


def _merge_samples(primary, extra):
    if not extra:
        return primary

    seen = {sample.path for sample in primary}
    merged = list(primary)

    for sample in extra:
        if sample.path in seen:
            continue
        merged.append(sample)
        seen.add(sample.path)

    return merged


