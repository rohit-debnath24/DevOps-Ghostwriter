"""
Cache Manager for Agent Responses
Handles caching of agent outputs to reduce API calls and handle rate limits.
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime, timedelta


class CacheManager:
    """
    Simple file-based cache manager for agent responses.
    Uses content hashing for cache keys and TTL for expiration.
    """

    def __init__(self, cache_dir: str = "agent_cache", default_ttl_hours: int = 24):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory to store cache files
            default_ttl_hours: Default time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = timedelta(hours=default_ttl_hours)

    def _generate_cache_key(self, agent_name: str, content: str) -> str:
        """
        Generate a cache key from agent name and content.

        Args:
            agent_name: Name of the agent
            content: Input content to hash

        Returns:
            Cache key string
        """
        # Create hash of content for deterministic key
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"{agent_name}_{content_hash}"

    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, agent_name: str, content: str) -> Optional[Any]:
        """
        Retrieve cached response if available and not expired.

        Args:
            agent_name: Name of the agent
            content: Input content

        Returns:
            Cached response or None if not found/expired
        """
        cache_key = self._generate_cache_key(agent_name, content)
        cache_file = self._get_cache_file_path(cache_key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Check expiration
            cached_time = datetime.fromisoformat(cache_data["timestamp"])
            if datetime.now() - cached_time > self.default_ttl:
                # Cache expired, delete it
                cache_file.unlink()
                return None

            return cache_data["response"]

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, delete it
            cache_file.unlink()
            return None

    def set(self, agent_name: str, content: str, response: Any) -> None:
        """
        Store a response in cache.

        Args:
            agent_name: Name of the agent
            content: Input content
            response: Response to cache
        """
        cache_key = self._generate_cache_key(agent_name, content)
        cache_file = self._get_cache_file_path(cache_key)

        cache_data = {
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat(),
            "response": response,
        }

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Warning: Failed to write cache: {e}")

    def clear(self, agent_name: Optional[str] = None) -> int:
        """
        Clear cache files.

        Args:
            agent_name: If provided, only clear cache for this agent.
                       If None, clear all cache.

        Returns:
            Number of files deleted
        """
        deleted = 0

        if agent_name:
            # Clear specific agent cache
            pattern = f"{agent_name}_*.json"
            for cache_file in self.cache_dir.glob(pattern):
                cache_file.unlink()
                deleted += 1
        else:
            # Clear all cache
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                deleted += 1

        return deleted

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_files = len(cache_files)
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            "total_entries": total_files,
            "total_size_bytes": total_size,
            "cache_dir": str(self.cache_dir),
        }


# Global cache manager instance
_cache_manager_instance: Optional[CacheManager] = None


def get_cache_manager(
    cache_dir: str = "agent_cache", default_ttl_hours: int = 24
) -> CacheManager:
    """
    Get or create the global cache manager instance.

    Args:
        cache_dir: Directory to store cache files
        default_ttl_hours: Default time-to-live in hours

    Returns:
        CacheManager instance
    """
    global _cache_manager_instance

    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager(cache_dir, default_ttl_hours)

    return _cache_manager_instance


if __name__ == "__main__":
    # Test the cache manager
    cache = get_cache_manager()

    print("Testing Cache Manager...")

    # Test set and get
    cache.set("test_agent", "test content", {"result": "test response"})
    result = cache.get("test_agent", "test content")
    print(f"Cache test: {result}")

    # Test stats
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")

    # Test clear
    deleted = cache.clear("test_agent")
    print(f"Deleted {deleted} cache entries")
