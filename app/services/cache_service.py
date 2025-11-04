"""
缓存服务
"""

import redis
import json
import logging
import time
from typing import Any, Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class CacheService:
    """Redis 缓存服务（支持降级到内存缓存）"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        初始化缓存服务
        
        Args:
            host: Redis主机
            port: Redis端口
            db: Redis数据库
        """
        self.memory_cache: Dict[str, Tuple[Any, float]] = {}

        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis_client.ping()
            self.use_redis = True
            logger.info(f"Redis 连接成功: {host}:{port}")
        except Exception as e:
            logger.info(f"Redis 不可用 ({str(e)}), 将使用内存缓存，设置 REDIS_HOST/PORT 可启用 Redis")
            self.redis_client = None
            self.use_redis = False
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值，不存在返回None
        """
        try:
            if self.use_redis and self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    logger.debug(f"Redis缓存命中: {key}")
                    return json.loads(value)
                return None
            else:
                record = self.memory_cache.get(key)
                if not record:
                    return None
                value, expire_at = record
                if expire_at and expire_at < time.time():
                    logger.debug(f"内存缓存过期: {key}")
                    self.memory_cache.pop(key, None)
                    return None
                logger.debug(f"内存缓存命中: {key}")
                return value
        except Exception as e:
            logger.error(f"缓存读取失败: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
        """
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
                logger.debug(f"Redis缓存设置: {key}")
            else:
                expire_at = time.time() + ttl if ttl else 0
                self.memory_cache[key] = (value, expire_at)
                logger.debug(f"内存缓存设置: {key} (ttl={ttl}s)")
        except Exception as e:
            logger.error(f"缓存写入失败: {str(e)}")
    
    def delete(self, key: str):
        """
        删除缓存
        
        Args:
            key: 缓存键
        """
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
        except Exception as e:
            logger.error(f"缓存删除失败: {str(e)}")
    
    def clear_all(self):
        """清空所有缓存"""
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.flushdb()
                logger.info("Redis缓存已清空")
            else:
                self.memory_cache.clear()
                logger.info("内存缓存已清空")
        except Exception as e:
            logger.error(f"清空缓存失败: {str(e)}")

