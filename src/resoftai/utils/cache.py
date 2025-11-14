"""Redis caching utilities for performance optimization."""
import json
import logging
from typing import Any, Optional, Callable
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

# Redis client instance (will be initialized on app startup)
redis_client: Optional[Any] = None


async def init_redis(url: str = "redis://localhost:6379/0"):
    """
    Initialize Redis connection.

    Args:
        url: Redis connection URL
    """
    global redis_client
    try:
        import redis.asyncio as aioredis
        redis_client = await aioredis.from_url(
            url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20
        )
        await redis_client.ping()
        logger.info(f"Redis connected successfully: {url}")
    except ImportError:
        logger.warning("redis package not installed. Caching will be disabled.")
        redis_client = None
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        redis_client = None


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


class CacheManager:
    """Manager for Redis caching operations."""

    def __init__(self, prefix: str = "resoftai"):
        """
        Initialize cache manager.

        Args:
            prefix: Key prefix for all cache entries
        """
        self.prefix = prefix

    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not redis_client:
            return None

        try:
            full_key = self._make_key(key)
            value = await redis_client.get(full_key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        if not redis_client:
            return False

        try:
            full_key = self._make_key(key)
            serialized = json.dumps(value)
            await redis_client.setex(full_key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not redis_client:
            return False

        try:
            full_key = self._make_key(key)
            await redis_client.delete(full_key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not redis_client:
            return False

        try:
            full_key = self._make_key(key)
            return await redis_client.exists(full_key) > 0
        except Exception as e:
            logger.error(f"Cache exists check error for key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.

        Args:
            pattern: Key pattern (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        if not redis_client:
            return 0

        try:
            full_pattern = self._make_key(pattern)
            keys = []
            async for key in redis_client.scan_iter(match=full_pattern):
                keys.append(key)

            if keys:
                return await redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment counter in cache.

        Args:
            key: Cache key
            amount: Amount to increment by

        Returns:
            New counter value
        """
        if not redis_client:
            return 0

        try:
            full_key = self._make_key(key)
            return await redis_client.incrby(full_key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0


# Global cache manager instance
cache_manager = CacheManager()


def cached(
    key_func: Callable = None,
    ttl: int = 3600,
    key_prefix: str = ""
):
    """
    Decorator for caching function results.

    Args:
        key_func: Function to generate cache key from args/kwargs
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key

    Example:
        @cached(key_func=lambda user_id: f"user:{user_id}", ttl=300)
        async def get_user(user_id: int):
            # Expensive operation
            return user_data
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = f"{key_prefix}:{key_func(*args, **kwargs)}"
            else:
                # Default: use function name and args
                args_str = "_".join(str(arg) for arg in args)
                kwargs_str = "_".join(f"{k}={v}" for k, v in kwargs.items())
                cache_key = f"{key_prefix}:{func.__name__}:{args_str}:{kwargs_str}"

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cached result for key: {cache_key}")

            return result

        return wrapper
    return decorator


class RateLimiter:
    """Rate limiter using Redis."""

    def __init__(self, cache_manager: CacheManager):
        """
        Initialize rate limiter.

        Args:
            cache_manager: Cache manager instance
        """
        self.cache_manager = cache_manager

    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Check if request is allowed under rate limit.

        Args:
            key: Rate limit key (e.g., user ID or IP)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if request is allowed, False otherwise
        """
        if not redis_client:
            return True  # Allow if Redis not available

        try:
            rate_key = f"ratelimit:{key}:{window_seconds}"
            current = await self.cache_manager.increment(rate_key)

            # Set expiry on first request
            if current == 1:
                full_key = self.cache_manager._make_key(rate_key)
                await redis_client.expire(full_key, window_seconds)

            return current <= max_requests
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True  # Allow on error


# Global rate limiter instance
rate_limiter = RateLimiter(cache_manager)
