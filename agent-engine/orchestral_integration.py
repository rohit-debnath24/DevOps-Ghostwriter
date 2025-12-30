"""
Orchestral Agent Integration Module
Bridges agent-engine FastAPI with the advanced Agents/orchestral_agent system
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Add Agents directory to path
agents_path = Path(__file__).parent.parent / "Agents"
sys.path.insert(0, str(agents_path))

# Load environment variables
load_dotenv('../.env.local')

# Import orchestral agent components
from orchestral_agent.orchestral_agent import (
    run_runtime_validation,
    run_security_audit
)
from cache_manager import get_cache_manager

# Import worker agents for direct access
from workers_agents.Runtime_Validator import (
    runtime_validator_agent,
    detect_syntax_errors,
    detect_infinite_loops,
)
from workers_agents.Security_Auditor import (
    security_auditor,
    scan_hardcoded_secrets,
    scan_sql_injection,
    scan_vulnerable_dependencies,
    scan_security_antipatterns,
)
try:
    from workers_agents.GhostWriter import (
        ghostwriter_agent,
        format_pr_comment_header,
        format_security_findings,
        format_logic_check,
        synthesize_pr_review
    )
    GHOSTWRITER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: GhostWriter functions not fully available: {e}")
    GHOSTWRITER_AVAILABLE = False

from google.adk.sessions import InMemorySessionService

# Initialize cache manager
cache_manager = get_cache_manager(
    cache_dir=str(agents_path / "agent_cache"),
    default_ttl_hours=24
)


async def analyze_pr_with_orchestral_agents(
    repo_id: str,
    pr_id: int,
    diff_text: str,
    title: str = None,
    description: str = None
) -> Dict[str, Any]:
    """
    Analyzes a PR using the advanced orchestral agent system.
    
    Args:
        repo_id: Repository identifier (owner/repo)
        pr_id: Pull request number
        diff_text: The PR diff content
        title: PR title
        description: PR description
        
    Returns:
        Dict containing analysis results with comment, confidence score, and detailed reports
    """
    print(f"\n🎭 ORCHESTRAL AGENT ANALYSIS - PR #{pr_id}")
    print(f"Repository: {repo_id}")
    print(f"Diff size: {len(diff_text)} characters")
    print("=" * 80)
    
    try:
        # Check cache first
        cache_key = f"pr_analysis"
        cache_input = f"{repo_id}_{pr_id}_{diff_text[:100]}"  # Include diff snippet for uniqueness
        cached_result = cache_manager.get(cache_key, cache_input)
        if cached_result:
            print("✨ Using cached analysis result")
            return cached_result
        
        # Initialize session service
        session_service = InMemorySessionService()
        
        # Step 1: Run Runtime Validation
        print("\n🔍 Step 1: Runtime Validation...")
        runtime_result = await run_runtime_validation(diff_text, session_service)
        print(f"   Status: {runtime_result['status'].upper()}")
        print(f"   Issues Found: {runtime_result['total_issues']}")
        
        # Step 2: Run Security Audit
        print("\n🔒 Step 2: Security Audit...")
        security_result = await run_security_audit(diff_text, session_service)
        print(f"   Status: {security_result.get('status', 'unknown').upper()}")
        print(f"   Issues Found: {security_result.get('total_issues', 0)}")
        
        # Step 3: Generate PR Comment using GhostWriter
        print("\n✍️  Step 3: Synthesizing PR Comment...")
        
        # Prepare data for GhostWriter
        logic_status = "Pass" if runtime_result['status'] == 'passed' else "Fail"
        logic_details = json.dumps(runtime_result, indent=2)
        
        security_issues_count = security_result.get('total_issues', 0)
        security_report_text = json.dumps(security_result, indent=2)
        
        # Format README status (check if README changes exist in diff)
        readme_updated = 'README' in diff_text or 'readme' in diff_text.lower()
        readme_changes = "README documentation updated" if readme_updated else ""
        
        # Extract PR stats from diff
        pr_stats = {
            'files_changed': diff_text.count('diff --git'),
            'lines_added': diff_text.count('\n+'),
            'lines_removed': diff_text.count('\n-')
        }
        
        # Local flag to track if we should use manual generation
        use_manual_generation = not GHOSTWRITER_AVAILABLE
        pr_comment = None
        
        # Try to use GhostWriter agent for sophisticated comment generation
        if GHOSTWRITER_AVAILABLE:
            try:
                # Create session for GhostWriter
                ghostwriter_session = await session_service.create_session(
                    app_name="pr_analysis",
                    user_id=f"{repo_id}_{pr_id}",
                    session_id=f"session_{pr_id}"
                )
                
                pr_comment = synthesize_pr_review(
                    security_report=security_report_text,
                    logic_status=logic_status,
                    logic_details=logic_details,
                    readme_updated=readme_updated,
                    readme_changes=readme_changes,
                    session_service=session_service,
                    app_name="pr_analysis",
                    user_id=f"{repo_id}_{pr_id}",
                    session_id=f"session_{pr_id}",
                    stats=pr_stats
                )
                print(f"   Used GhostWriter agent for comment generation")
            except Exception as e:
                print(f"   Warning: GhostWriter agent failed: {e}")
                print("   Falling back to manual comment generation")
                use_manual_generation = True
        
        if use_manual_generation:
            # Fallback to manual comment generation
            header = format_pr_comment_header(
                logic_status=logic_status,
                security_issues_count=security_issues_count,
                readme_updated=readme_updated
            )
            
            # Format sections
            security_section = format_security_findings(security_report_text)
            logic_section = format_logic_check(logic_status, logic_details)
            
            # Assemble final comment
            pr_comment = f"""{header}

{security_section}

{logic_section}

### 📊 Pull Request Statistics
- **Files Changed:** {pr_stats['files_changed']}
- **Lines Added:** {pr_stats['lines_added']}
- **Lines Removed:** {pr_stats['lines_removed']}

### 🎯 Recommendation
"""
        
        # Calculate confidence score
        confidence_score = 1.0
        if runtime_result['status'] == 'failed':
            confidence_score -= 0.3
        if security_issues_count > 0:
            confidence_score -= min(0.5, security_issues_count * 0.1)
        confidence_score = max(0.0, confidence_score)
        
        # Add recommendation based on analysis
        if confidence_score >= 0.8:
            pr_comment += "✅ **APPROVED** - This PR meets code quality and security standards. Safe to merge.\n"
        elif confidence_score >= 0.6:
            pr_comment += "⚠️ **APPROVED WITH CAUTION** - Minor issues detected. Review recommendations before merging.\n"
        else:
            pr_comment += "❌ **CHANGES REQUESTED** - Critical issues found. Please address before merging.\n"
        
        pr_comment += f"\n**Confidence Score:** {confidence_score:.2%}\n"
        pr_comment += "\n---\n*🤖 Generated by DevOps Ghostwriter - Powered by AI Agents*"
        
        print(f"   Generated comment ({len(pr_comment)} characters)")
        
        # Determine final status
        if confidence_score >= 0.8:
            status = "success"
        elif confidence_score >= 0.6:
            status = "warning"
        else:
            status = "error"
        
        # Prepare result
        result = {
            "status": status,
            "comment": pr_comment,
            "confidence_score": confidence_score,
            "runtime_snapshot": runtime_result,
            "security_snapshot": security_result,
            "metadata": {
                "repo_id": repo_id,
                "pr_id": pr_id,
                "title": title,
                "pr_stats": pr_stats,
                "agent_version": "orchestral_v1.0"
            }
        }
        
        # Cache the result
        cache_manager.set(cache_key, cache_input, result)
        
        print("\n✅ Analysis Complete!")
        print(f"   Final Status: {status.upper()}")
        print(f"   Confidence: {confidence_score:.2%}")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error in orchestral analysis: {e}")
        import traceback
        traceback.print_exc()
        
        # Return error response
        return {
            "status": "error",
            "comment": f"⚠️ Analysis failed: {str(e)}\n\nPlease check the agent service logs for details.",
            "confidence_score": 0.0,
            "runtime_snapshot": None,
            "security_snapshot": None,
            "error": str(e)
        }


def get_cache_stats() -> Dict[str, Any]:
    """Get statistics about the agent cache."""
    return cache_manager.get_stats()


def clear_cache() -> bool:
    """Clear all cached analysis results."""
    try:
        cleared_count = cache_manager.clear()  # Clear all entries
        print(f"Cleared {cleared_count} cache entries")
        return True
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return False
