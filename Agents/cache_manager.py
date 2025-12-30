"""
Cache Manager for Agent Responses
==================================
Provides persistent caching for agent responses to avoid redundant API calls
and handle rate limits gracefully.

Features:
- Hash-based key generation from agent name + input content
- JSON file-based persistence
- TTL (time-to-live) expiration
- Thread-safe operations
- Automatic cache directory creation
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional, Dict
import threading


class CacheManager:
    """
    Manages caching of agent responses with TTL and persistence.
    """
    
    def __init__(self, cache_dir: str = "agent_cache", default_ttl_hours: int = 24):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl_hours: Default time-to-live for cache entries in hours
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl_seconds = default_ttl_hours * 3600
        self.lock = threading.Lock()
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata file to track cache entries
        self.metadata_file = self.cache_dir / "_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load cache metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.metadata = {}
        else:
            self.metadata = {}
    
    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save cache metadata: {e}")
    
    def _generate_cache_key(self, agent_name: str, input_content: str) -> str:
        """
        Generate a unique cache key based on agent name and input content.
        
        Args:
            agent_name: Name of the agent
            input_content: Input content to hash
            
        Returns:
            SHA256 hash as cache key
        """
        # Create a combined string and hash it
        combined = f"{agent_name}:{input_content}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.json"
    
    def _is_expired(self, cache_key: str) -> bool:
        """
        Check if a cache entry has expired.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            True if expired, False otherwise
        """
        if cache_key not in self.metadata:
            return True
        
        entry = self.metadata[cache_key]
        expiry_time = entry.get('expiry_time', 0)
        
        return time.time() > expiry_time
    
    def get(self, agent_name: str, input_content: str) -> Optional[Any]:
        """
        Retrieve cached response for given agent and input.
        
        Args:
            agent_name: Name of the agent
            input_content: Input content that was processed
            
        Returns:
            Cached response if found and valid, None otherwise
        """
        with self.lock:
            cache_key = self._generate_cache_key(agent_name, input_content)
            cache_file = self._get_cache_file_path(cache_key)
            
            # Check if cache exists and is not expired
            if not cache_file.exists() or self._is_expired(cache_key):
                # Clean up expired entry
                if cache_key in self.metadata:
                    del self.metadata[cache_key]
                    self._save_metadata()
                if cache_file.exists():
                    cache_file.unlink()
                return None
            
            # Load and return cached data
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    return cached_data.get('response')
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to read cache file {cache_key}: {e}")
                return None
    
    def set(
        self, 
        agent_name: str, 
        input_content: str, 
        response: Any,
        ttl_hours: Optional[int] = None
    ) -> None:
        """
        Store response in cache.
        
        Args:
            agent_name: Name of the agent
            input_content: Input content that was processed
            response: Response to cache
            ttl_hours: Time-to-live in hours (uses default if not specified)
        """
        with self.lock:
            cache_key = self._generate_cache_key(agent_name, input_content)
            cache_file = self._get_cache_file_path(cache_key)
            
            # Calculate expiry time
            ttl_seconds = (ttl_hours * 3600) if ttl_hours else self.default_ttl_seconds
            expiry_time = time.time() + ttl_seconds
            
            # Prepare cache data
            cache_data = {
                'agent_name': agent_name,
                'response': response,
                'cached_at': time.time(),
                'expiry_time': expiry_time
            }
            
            # Write cache file
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, indent=2)
                
                # Update metadata
                self.metadata[cache_key] = {
                    'agent_name': agent_name,
                    'cached_at': cache_data['cached_at'],
                    'expiry_time': expiry_time,
                    'input_hash': cache_key[:16]  # Store partial hash for debugging
                }
                self._save_metadata()
            except IOError as e:
                print(f"Warning: Failed to write cache file {cache_key}: {e}")
    
    def clear(self, agent_name: Optional[str] = None) -> int:
        """
        Clear cache entries.
        
        Args:
            agent_name: If specified, only clear entries for this agent.
                       If None, clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        with self.lock:
            cleared_count = 0
            keys_to_remove = []
            
            for cache_key, entry in self.metadata.items():
                if agent_name is None or entry.get('agent_name') == agent_name:
                    cache_file = self._get_cache_file_path(cache_key)
                    if cache_file.exists():
                        cache_file.unlink()
                    keys_to_remove.append(cache_key)
                    cleared_count += 1
            
            # Remove from metadata
            for key in keys_to_remove:
                del self.metadata[key]
            
            self._save_metadata()
            return cleared_count
    
    def clear_expired(self) -> int:
        """
        Remove all expired cache entries.
        
        Returns:
            Number of expired entries removed
        """
        with self.lock:
            cleared_count = 0
            keys_to_remove = []
            
            for cache_key in list(self.metadata.keys()):
                if self._is_expired(cache_key):
                    cache_file = self._get_cache_file_path(cache_key)
                    if cache_file.exists():
                        cache_file.unlink()
                    keys_to_remove.append(cache_key)
                    cleared_count += 1
            
            # Remove from metadata
            for key in keys_to_remove:
                del self.metadata[key]
            
            self._save_metadata()
            return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            total_entries = len(self.metadata)
            expired_count = sum(1 for key in self.metadata if self._is_expired(key))
            
            # Count by agent
            agent_counts = {}
            for entry in self.metadata.values():
                agent_name = entry.get('agent_name', 'unknown')
                agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
            
            return {
                'total_entries': total_entries,
                'active_entries': total_entries - expired_count,
                'expired_entries': expired_count,
                'entries_by_agent': agent_counts,
                'cache_dir': str(self.cache_dir)
            }


# Singleton instance
_cache_manager_instance: Optional[CacheManager] = None


def get_cache_manager(
    cache_dir: str = "agent_cache", 
    default_ttl_hours: int = 24
) -> CacheManager:
    """
    Get or create the singleton cache manager instance.
    
    Args:
        cache_dir: Directory to store cache files
        default_ttl_hours: Default time-to-live for cache entries in hours
        
    Returns:
        CacheManager instance
    """
    global _cache_manager_instance
    
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager(cache_dir, default_ttl_hours)
    
    return _cache_manager_instance


# Example usage and testing
if __name__ == "__main__":
    # Initialize cache manager
    cache = get_cache_manager(cache_dir="test_cache", default_ttl_hours=1)
    
    # Test data
    test_agent = "test_agent"
    test_input = "sample code content"
    test_response = {"status": "success", "issues": []}
    
    # Set cache
    print("Setting cache...")
    cache.set(test_agent, test_input, test_response)
    
    # Get cache
    print("Getting cache...")
    cached = cache.get(test_agent, test_input)
    print(f"Cached response: {cached}")
    
    # Get stats
    print("\nCache statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Clear cache
    print(f"\nClearing cache: {cache.clear()} entries removed")
