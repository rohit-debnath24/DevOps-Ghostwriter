import os
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import json
import logging
import warnings
from dotenv import load_dotenv

# Load environment variables from .env.local in the root directory
env_path = Path(__file__).parent.parent.parent / ".env.local"
load_dotenv(dotenv_path=env_path)

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Add parent directories to path to import worker agents and cache_manager
sys.path.append(str(Path(__file__).parent.parent))

# Import cache manager
from cache_manager import get_cache_manager

# Import worker agents
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

# Suppress warnings and configure logging
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

# Initialize cache manager
cache_manager = get_cache_manager(
    cache_dir=str(Path(__file__).parent.parent / "agent_cache"),
    default_ttl_hours=24
)
print(f"INFO: Cache manager initialized at {cache_manager.cache_dir}")

"""
Orchestral Agent - Code Quality & Security Pipeline
====================================================
This agent orchestrates multiple worker agents:
1. Runtime Validator - Detects syntax errors, runtime issues, and logic flaws
2. Security Auditor - Scans for security vulnerabilities and anti-patterns

The orchestral agent coordinates these workers and provides a unified report.
"""


# =========================================================
# CONFIGURATION
# =========================================================

APP_NAME = "code_audit_orchestrator"
USER_ID = "orchestrator_user"
RUNTIME_SESSION_ID = "runtime_validation_session"
SECURITY_SESSION_ID = "security_audit_session"


# =========================================================
# UTILITY FUNCTIONS
# =========================================================

def read_sample_file(filename: str = "sample.py") -> str:
    """
    Reads a code file from the parent directory.
    
    Args:
        filename: Name of the file to read
        
    Returns:
        Content of the file as string
    """
    # Look in parent directory (workers_agents folder)
    path = Path(__file__).parent.parent / "workers_agents" / filename
    
    if not path.exists():
        raise FileNotFoundError(f"{filename} not found at {path}")
    
    return path.read_text(encoding="utf-8")


def write_consolidated_report(
    runtime_report: Dict,
    security_report: Dict,
    filename: str = "orchestral_audit_report.json"
) -> None:
    """
    Writes a consolidated audit report combining runtime and security findings.
    
    Args:
        runtime_report: Runtime validation results dictionary
        security_report: Security audit results dictionary
        filename: Output filename (default JSON format)
    """
    output_path = Path(__file__).parent / filename
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    consolidated_report = {
        "report_type": "Orchestral Code Audit",
        "timestamp": timestamp,
        "runtime_validation": runtime_report,
        "security_audit": security_report,
        "overall_summary": {
            "total_runtime_issues": runtime_report.get('total_issues', 0),
            "total_security_issues": security_report.get('total_issues', 0),
            "runtime_status": runtime_report.get('status', 'unknown'),
            "security_status": security_report.get('status', 'unknown'),
            "overall_status": "passed" if runtime_report.get('status') == 'passed' and security_report.get('status') == 'passed' else "failed"
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(consolidated_report, f, indent=2)
    
    print(f"\n✅ Consolidated JSON report written to: {output_path}")


# =========================================================
# AGENT INTERACTION FUNCTIONS
# =========================================================

async def run_runtime_validation(
    code_content: str,
    session_service: InMemorySessionService
) -> Dict[str, Any]:
    """
    Runs the Runtime Validator agent on the provided code.
    Now includes caching to handle rate limits.
    
    Args:
        code_content: The code to validate
        session_service: ADK session service
        
    Returns:
        Dictionary containing validation results
    """
    print("\n" + "="*80)
    print("🔍 STARTING RUNTIME VALIDATION")
    print("="*80)
    
    agent_name = "orchestral_runtime_validator"
    
    # Check cache first
    cached_response = cache_manager.get(agent_name, code_content)
    if cached_response is not None:
        print(f"✅ Cache HIT for {agent_name}")
        print(f"✅ Runtime validation complete: {cached_response.get('total_issues', 0)} total issue(s)")
        return cached_response
    
    print(f"⚠️ Cache MISS for {agent_name} - calling Google ADK API")
    
    # Create session for runtime validation
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=RUNTIME_SESSION_ID
    )
    
    # Run static checks first
    static_issues = []
    static_issues.extend(detect_syntax_errors(code_content))
    static_issues.extend(detect_infinite_loops(code_content))
    
    print(f"✅ Static analysis complete: {len(static_issues)} issue(s) found")
    
    # Create runner for runtime validator
    runner = Runner(
        agent=runtime_validator_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    # Prepare user message
    user_content = types.Content(
        role="user",
        parts=[types.Part(text=code_content)]
    )
    
    llm_issues = []
    print("🤖 Running LLM-based runtime analysis...")
    
    # Run agent and collect results
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=RUNTIME_SESSION_ID,
        new_message=user_content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    try:
                        parsed = json.loads(part.text)
                        llm_issues.extend(parsed.get("issues", []))
                    except json.JSONDecodeError:
                        # If not JSON, treat as descriptive text
                        pass
    
    # Combine all issues
    all_issues = static_issues + llm_issues
    
    result = {
        "agent": "Runtime Validator Agent",
        "status": "passed" if not all_issues else "failed",
        "total_issues": len(all_issues),
        "issues": all_issues
    }
    
    # Cache the result
    cache_manager.set(agent_name, code_content, result)
    
    print(f"✅ Runtime validation complete: {len(all_issues)} total issue(s)")
    
    return result


async def run_security_audit(
    code_content: str,
    session_service: InMemorySessionService
) -> Dict[str, Any]:
    """
    Runs the Security Auditor agent on the provided code.
    Now includes caching to handle rate limits.
    
    Args:
        code_content: The code to audit
        session_service: ADK session service
        
    Returns:
        Dictionary containing the security audit results
    """
    print("\n" + "="*80)
    print("🔒 STARTING SECURITY AUDIT")
    print("="*80)
    
    agent_name = "orchestral_security_auditor"
    
    # Check cache first
    cached_response = cache_manager.get(agent_name, code_content)
    if cached_response is not None:
        print(f"✅ Cache HIT for {agent_name}")
        print("✅ Security audit complete")
        return cached_response
    
    print(f"⚠️ Cache MISS for {agent_name} - calling Google ADK API")
    
    # Create session for security audit
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SECURITY_SESSION_ID
    )
    
    # Create runner for security auditor
    runner = Runner(
        agent=security_auditor,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    # Prepare the security audit query
    query = f"""
Please conduct a comprehensive security audit of this code:

{code_content}

Run all security checks:
1. Scan for hardcoded secrets
2. Check for SQL injection vulnerabilities
3. Identify vulnerable dependencies
4. Detect security anti-patterns

Return the final JSON report from generate_security_summary.
"""
    
    user_content = types.Content(
        role="user",
        parts=[types.Part(text=query)]
    )
    
    responses = []
    print("🤖 Running security analysis...")
    
    # Run agent and collect responses
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SECURITY_SESSION_ID,
        new_message=user_content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        responses.append(part.text)
    
    # Try to parse JSON from responses
    security_result = {
        "agent": "Security Auditor Agent",
        "status": "unknown",
        "total_issues": 0,
        "scans": [],
        "raw_response": "\n\n".join(responses) if responses else "No response"
    }
    
    for response in responses:
        try:
            parsed = json.loads(response)
            if "agent" in parsed and "status" in parsed:
                security_result = parsed
                break
        except json.JSONDecodeError:
            continue
    
    # Cache the result
    cache_manager.set(agent_name, code_content, security_result)
    
    print("✅ Security audit complete")
    
    return security_result


# =========================================================
# MAIN ORCHESTRATION FUNCTION
# =========================================================

async def orchestrate_code_audit(filename: str = "sample.py"):
    """
    Main orchestration function that coordinates all worker agents.
    
    Args:
        filename: Name of the code file to audit
    """
    print("\n" + "="*80)
    print("🎭 ORCHESTRAL CODE AUDIT PIPELINE")
    print("="*80)
    print(f"Target File: {filename}")
    print("Workers: Runtime Validator, Security Auditor")
    print("="*80)
    
    try:
        # Initialize session service
        session_service = InMemorySessionService()
        
        # Read the code file
        print(f"\n📖 Reading {filename}...")
        code_content = read_sample_file(filename)
        print(f"✅ Successfully read {len(code_content)} characters")
        
        # Run Runtime Validation
        runtime_result = await run_runtime_validation(code_content, session_service)
        
        # Run Security Audit
        security_result = await run_security_audit(code_content, session_service)
        
        # Display results
        print("\n" + "="*80)
        print("📊 AUDIT RESULTS SUMMARY")
        print("="*80)
        
        print(f"\n🔍 Runtime Validation: {runtime_result['status'].upper()}")
        print(f"   Total Issues: {runtime_result['total_issues']}")
        
        if runtime_result['issues']:
            print("   Issues:")
            for issue in runtime_result['issues'][:3]:  # Show first 3
                print(f"   - {issue.get('type')}: {issue.get('description')[:50]}...")
            if runtime_result['total_issues'] > 3:
                print(f"   ... and {runtime_result['total_issues'] - 3} more")
        
        print(f"\n🔒 Security Audit: {security_result.get('status', 'unknown').upper()}")
        print(f"   Total Issues: {security_result.get('total_issues', 0)}")
        
        if security_result.get('scans'):
            for scan in security_result['scans']:
                scan_type = scan.get('scan_type', 'unknown')
                scan_status = scan.get('status', 'unknown')
                scan_issues = scan.get('total_issues', 0)
                if scan_issues > 0:
                    print(f"   - {scan_type}: {scan_issues} issue(s)")
        
        # Write consolidated report
        write_consolidated_report(runtime_result, security_result)
        
        # Print final status
        print("\n" + "="*80)
        if runtime_result['status'] == 'failed' or security_result.get('status') == 'failed':
            print("⚠️  AUDIT COMPLETED WITH ISSUES - REVIEW REQUIRED")
        else:
            print("✅ AUDIT COMPLETED - ALL CHECKS PASSED")
        print("="*80)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print(f"Please ensure '{filename}' exists in the workers_agents directory.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    try:
        # You can specify a different file here
        target_file = "sample.py"
        
        # Run the orchestral audit
        asyncio.run(orchestrate_code_audit(target_file))
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Audit interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
