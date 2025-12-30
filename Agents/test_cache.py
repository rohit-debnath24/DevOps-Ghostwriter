"""
Cache System Test Script
========================
Tests the caching functionality with both worker agents.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from cache_manager import get_cache_manager
import json


def test_cache_basics():
    """Test basic cache operations."""
    print("\n" + "="*70)
    print("🧪 Testing Cache Manager - Basic Operations")
    print("="*70)
    
    # Initialize cache
    cache = get_cache_manager(
        cache_dir=str(Path(__file__).parent / "agent_cache"),
        default_ttl_hours=24
    )
    
    # Test data
    agent_name = "test_agent"
    input_code = "def hello():\n    print('Hello World')"
    response_data = {
        "status": "passed",
        "issues": [],
        "total_issues": 0
    }
    
    print("\n1️⃣  Setting cache entry...")
    cache.set(agent_name, input_code, response_data)
    print("   ✅ Cache entry created")
    
    print("\n2️⃣  Retrieving cache entry...")
    cached = cache.get(agent_name, input_code)
    print(f"   ✅ Cache retrieved: {cached}")
    
    print("\n3️⃣  Verifying cache content...")
    if cached == response_data:
        print("   ✅ Cache content matches original!")
    else:
        print("   ❌ Cache content mismatch!")
    
    print("\n4️⃣  Testing cache miss (different input)...")
    different_input = "def goodbye():\n    print('Goodbye')"
    missed = cache.get(agent_name, different_input)
    if missed is None:
        print("   ✅ Cache miss detected correctly")
    else:
        print("   ❌ Unexpected cache hit!")
    
    print("\n5️⃣  Cache statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    print("\n6️⃣  Clearing test cache...")
    cleared = cache.clear()
    print(f"   ✅ Cleared {cleared} entries")
    
    print("\n" + "="*70)
    print("✅ Basic cache tests completed!")
    print("="*70 + "\n")


async def test_runtime_validator_cache():
    """Test Runtime Validator with cache."""
    print("\n" + "="*70)
    print("🧪 Testing Runtime Validator Agent - Cache Integration")
    print("="*70)
    
    try:
        from workers_agents.Runtime_Validator import validate_runtime
        
        print("\n1️⃣  First run (cache MISS expected)...")
        result1 = await validate_runtime()
        
        print("\n2️⃣  Second run (cache HIT expected)...")
        result2 = await validate_runtime()
        
        print("\n3️⃣  Verifying both results match...")
        if result1 == result2:
            print("   ✅ Results match! Cache is working correctly.")
        else:
            print("   ⚠️  Results differ (this might be expected if agent behavior varies)")
        
        print("\n" + "="*70)
        print("✅ Runtime Validator cache test completed!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error testing Runtime Validator: {e}")
        print("   Note: This might fail if dependencies or sample.py are missing\n")


async def test_security_auditor_cache():
    """Test Security Auditor with cache."""
    print("\n" + "="*70)
    print("🧪 Testing Security Auditor Agent - Cache Integration")
    print("="*70)
    
    try:
        from workers_agents.Security_Auditor import audit_code_security
        from google.adk.sessions import InMemorySessionService
        
        # Sample code to audit
        test_code = """
def process_user_input(user_id, password):
    api_key = "sk_test_12345678901234567890"
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query
"""
        
        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name="cache_test_app",
            user_id="test_user",
            session_id="test_session"
        )
        
        print("\n1️⃣  First run (cache MISS expected)...")
        result1 = await audit_code_security(
            code_content=test_code,
            session_service=session_service,
            user_id="test_user",
            session_id="test_session"
        )
        print(f"   Result preview: {result1[:200]}...")
        
        print("\n2️⃣  Second run (cache HIT expected)...")
        result2 = await audit_code_security(
            code_content=test_code,
            session_service=session_service,
            user_id="test_user",
            session_id="test_session"
        )
        
        print("\n3️⃣  Verifying both results match...")
        if result1 == result2:
            print("   ✅ Results match! Cache is working correctly.")
        else:
            print("   ⚠️  Results differ")
        
        print("\n" + "="*70)
        print("✅ Security Auditor cache test completed!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error testing Security Auditor: {e}")
        print("   Note: This might fail if dependencies or API keys are missing\n")


async def main():
    """Run all tests."""
    print("\n" + "🚀 "*35)
    print("CACHE SYSTEM COMPREHENSIVE TEST SUITE")
    print("🚀 "*35 + "\n")
    
    # Test 1: Basic cache operations
    test_cache_basics()
    
    # Test 2: Runtime Validator cache
    print("\n⏳ Starting Runtime Validator cache test...")
    await test_runtime_validator_cache()
    
    # Test 3: Security Auditor cache
    print("\n⏳ Starting Security Auditor cache test...")
    await test_security_auditor_cache()
    
    # Final statistics
    print("\n" + "="*70)
    print("📊 FINAL CACHE STATISTICS")
    print("="*70)
    cache = get_cache_manager()
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
