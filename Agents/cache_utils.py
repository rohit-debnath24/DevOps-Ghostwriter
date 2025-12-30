"""
Cache Utility Script
====================
Provides command-line utilities for managing agent cache.

Usage:
    python cache_utils.py stats              # Show cache statistics
    python cache_utils.py clear              # Clear all cache
    python cache_utils.py clear <agent_name> # Clear cache for specific agent
    python cache_utils.py expired            # Remove expired entries
"""

import sys
from pathlib import Path
from cache_manager import get_cache_manager


def show_stats():
    """Display cache statistics."""
    cache = get_cache_manager(
        cache_dir=str(Path(__file__).parent / "agent_cache")
    )
    
    print("\n📊 Cache Statistics")
    print("=" * 50)
    
    stats = cache.get_stats()
    print(f"Cache Directory: {stats['cache_dir']}")
    print(f"Total Entries: {stats['total_entries']}")
    print(f"Active Entries: {stats['active_entries']}")
    print(f"Expired Entries: {stats['expired_entries']}")
    
    if stats['entries_by_agent']:
        print("\n📁 Entries by Agent:")
        for agent, count in stats['entries_by_agent'].items():
            print(f"  - {agent}: {count}")
    else:
        print("\n⚠️  No cache entries found")
    print()


def clear_cache(agent_name=None):
    """Clear cache entries."""
    cache = get_cache_manager(
        cache_dir=str(Path(__file__).parent / "agent_cache")
    )
    
    if agent_name:
        print(f"\n🧹 Clearing cache for agent: {agent_name}")
    else:
        print("\n🧹 Clearing all cache entries")
    
    cleared = cache.clear(agent_name)
    print(f"✅ Cleared {cleared} cache entries\n")


def clear_expired():
    """Remove expired cache entries."""
    cache = get_cache_manager(
        cache_dir=str(Path(__file__).parent / "agent_cache")
    )
    
    print("\n🧹 Removing expired cache entries")
    cleared = cache.clear_expired()
    print(f"✅ Removed {cleared} expired entries\n")


def show_help():
    """Display help message."""
    print(__doc__)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        show_stats()
    elif command == "clear":
        agent_name = sys.argv[2] if len(sys.argv) > 2 else None
        clear_cache(agent_name)
    elif command == "expired":
        clear_expired()
    elif command in ["help", "-h", "--help"]:
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
