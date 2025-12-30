"""
Test script to verify orchestral agent integration
"""
import asyncio
import sys
from pathlib import Path

# Add agent-engine to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestral_integration import analyze_pr_with_orchestral_agents

async def test_analysis():
    """Test the orchestral agent analysis with sample data"""
    
    sample_diff = """diff --git a/app.py b/app.py
index 1234567..89abcdef 100644
--- a/app.py
+++ b/app.py
@@ -10,7 +10,7 @@ import os
 
 # Database connection
 def connect_db():
-    password = "hardcoded_password_123"
+    password = os.getenv("DB_PASSWORD")
     conn = connect(f"postgresql://user:{password}@localhost/db")
     return conn
 
@@ -25,6 +25,10 @@ def query_user(user_id):
     result = cursor.execute(query)
     return result
 
+def get_api_key():
+    # API key for external service
+    return "EXAMPLE_API_KEY_DO_NOT_HARDCODE"
+
 if __name__ == "__main__":
     app.run()
"""
    
    print("Testing Orchestral Agent Integration")
    print("=" * 80)
    
    try:
        result = await analyze_pr_with_orchestral_agents(
            repo_id="test/repo",
            pr_id=123,
            diff_text=sample_diff,
            title="Test PR: Fix database password"
        )
        
        print("\n" + "=" * 80)
        print("TEST RESULTS")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Confidence: {result['confidence_score']:.2%}")
        print(f"\nComment Preview ({len(result['comment'])} chars):")
        print("-" * 80)
        print(result['comment'][:500] + "..." if len(result['comment']) > 500 else result['comment'])
        print("-" * 80)
        
        if result.get('runtime_snapshot'):
            print(f"\nRuntime Issues: {result['runtime_snapshot']['total_issues']}")
        if result.get('security_snapshot'):
            print(f"Security Issues: {result['security_snapshot'].get('total_issues', 0)}")
        
        if result['status'] == 'error':
            print("\n⚠️  Test completed with errors (see details above)")
            return False
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_analysis())
    sys.exit(0 if success else 1)
