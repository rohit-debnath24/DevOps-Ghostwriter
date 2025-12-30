from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import os
from pathlib import Path
from datetime import datetime
import json
import sys
from dotenv import load_dotenv

# Add parent directory to import cache_manager
sys.path.append(str(Path(__file__).parent.parent))
from cache_manager import get_cache_manager

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env.local"
load_dotenv(dotenv_path=env_path)

os.environ["GOOGLE_API_KEY"] = os.getenv("RUNTIME_VALIDATOR_API_KEY")

# Initialize cache manager
cache_manager = get_cache_manager(
    cache_dir=str(Path(__file__).parent.parent / "agent_cache"),
    default_ttl_hours=24
)

"""
Security Auditor Agent for PR Code Review
Scans code diffs for security vulnerabilities including:
- Hardcoded secrets (API keys, passwords, tokens)
- SQL injection vulnerabilities
- Vulnerable dependencies
- Common security anti-patterns
"""

import re
from typing import Annotated

# Tool: Scan for hardcoded secrets
def scan_hardcoded_secrets(code_diff: Annotated[str, "The PR diff content to scan"]) -> str:
    """
    Scans code diff for hardcoded secrets like API keys, passwords, and tokens.
    Returns findings as a JSON string.
    """
    findings = []
    
    # Patterns for common secrets
    patterns = {
        "API Key": r'(?i)(api[_-]?key|apikey|api[_-]?secret)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "AWS Access Key": r'(?i)(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret)\s*[:=]\s*["\']([A-Z0-9]{20,})["\']',
        "Password": r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']',
        "Private Key": r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',
        "OAuth Token": r'(?i)(oauth[_-]?token|access[_-]?token)\s*[:=]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
        "GitHub Token": r'(?i)(gh[ps]_[a-zA-Z0-9]{36,})',
        "Generic Secret": r'(?i)(secret|token|bearer)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{32,})["\']',
    }
    
    lines = code_diff.split('\n')
    for line_num, line in enumerate(lines, 1):
        # Check all lines (not just those starting with +)
        for secret_type, pattern in patterns.items():
            if re.search(pattern, line):
                findings.append({
                    "type": "Hardcoded Secret",
                    "secret_type": secret_type,
                    "severity": "CRITICAL",
                    "line": line_num,
                    "code_snippet": line.strip()[:80],
                    "recommendation": "Remove hardcoded secrets and use environment variables or secret management systems"
                })
    
    result = {
        "scan_type": "hardcoded_secrets",
        "status": "failed" if findings else "passed",
        "total_issues": len(findings),
        "issues": findings
    }
    return json.dumps(result)


# Tool: Scan for SQL injection vulnerabilities
def scan_sql_injection(code_diff: Annotated[str, "The PR diff content to scan"]) -> str:
    """
    Scans code diff for potential SQL injection vulnerabilities.
    Returns findings as a JSON string.
    """
    findings = []
    
    # Patterns for SQL injection vulnerabilities
    patterns = {
        "String concatenation in SQL": r'(?i)(execute|exec|query)\s*\([^)]*[+%]\s*["\']',
        "F-string in SQL": r'(?i)(execute|exec|query)\s*\([^)]*f["\'].*{',
        "Format in SQL": r'(?i)(execute|exec|query)\s*\([^)]*\.format\(',
        "Unsafe SQL construction": r'(?i)(select|insert|update|delete).*[+%].*(?:where|from|into)',
    }
    
    lines = code_diff.split('\n')
    for line_num, line in enumerate(lines, 1):
        for vuln_type, pattern in patterns.items():
            if re.search(pattern, line):
                findings.append({
                    "type": "SQL Injection Vulnerability",
                    "vulnerability_type": vuln_type,
                    "severity": "HIGH",
                    "line": line_num,
                    "code_snippet": line.strip()[:80],
                    "recommendation": "Use parameterized queries or ORM to prevent SQL injection"
                })
    
    result = {
        "scan_type": "sql_injection",
        "status": "failed" if findings else "passed",
        "total_issues": len(findings),
        "issues": findings
    }
    return json.dumps(result)


# Tool: Scan for vulnerable dependencies
def scan_vulnerable_dependencies(code_diff: Annotated[str, "The PR diff content to scan"]) -> str:
    """
    Scans dependency files for known vulnerable versions.
    Returns findings as a JSON string.
    """
    findings = []
    
    # Known vulnerable patterns (simplified - in production, use a vulnerability database)
    vulnerable_packages = {
        "requests": ["2.25.0", "2.26.0"],  # Example: versions with known issues
        "pyyaml": ["5.3", "5.3.1"],  # Versions with arbitrary code execution
        "pillow": ["8.1.0", "8.1.1"],  # Versions with security issues
        "django": ["3.0", "3.0.1"],  # Example vulnerable versions
        "flask": ["1.0", "1.0.1"],  # Example vulnerable versions
    }
    
    lines = code_diff.split('\n')
    for line_num, line in enumerate(lines, 1):
        # Check requirements.txt or similar files
        for package, vuln_versions in vulnerable_packages.items():
            for version in vuln_versions:
                if f"{package}=={version}" in line.lower() or f"{package}@{version}" in line.lower():
                    findings.append({
                        "type": "Vulnerable Dependency",
                        "package": package,
                        "vulnerable_version": version,
                        "severity": "HIGH",
                        "line": line_num,
                        "recommendation": f"Update {package} to the latest secure version"
                    })
    
    result = {
        "scan_type": "vulnerable_dependencies",
        "status": "failed" if findings else "passed",
        "total_issues": len(findings),
        "issues": findings
    }
    return json.dumps(result)


# Tool: Scan for general security anti-patterns
def scan_security_antipatterns(code_diff: Annotated[str, "The PR diff content to scan"]) -> str:
    """
    Scans for common security anti-patterns and unsafe practices.
    Returns findings as a JSON string.
    """
    findings = []
    
    # Common security anti-patterns
    patterns = {
        "eval() usage": (r'\beval\s*\(', "Avoid eval() - it can execute arbitrary code", "HIGH"),
        "exec() usage": (r'\bexec\s*\(', "Avoid exec() - it can execute arbitrary code", "HIGH"),
        "pickle.loads()": (r'pickle\.loads\s*\(', "Pickle is unsafe for untrusted data - use JSON", "MEDIUM"),
        "shell=True": (r'shell\s*=\s*True', "Avoid shell=True - use shell=False with list arguments", "HIGH"),
        "md5 hashing": (r'\bhashlib\.md5\s*\(', "MD5 is cryptographically broken - use SHA256 or better", "MEDIUM"),
        "assert for validation": (r'^\s*assert\s+', "Don't use assert for data validation - it can be disabled", "LOW"),
        "hardcoded localhost": (r'(?i)(localhost|127\.0\.0\.1):[0-9]+', "Avoid hardcoded hosts - use configuration", "LOW"),
    }
    
    lines = code_diff.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern_name, (pattern, recommendation, severity) in patterns.items():
            if re.search(pattern, line):
                findings.append({
                    "type": "Security Anti-Pattern",
                    "pattern_name": pattern_name,
                    "severity": severity,
                    "line": line_num,
                    "code_snippet": line.strip()[:80],
                    "recommendation": recommendation
                })
    
    result = {
        "scan_type": "security_antipatterns",
        "status": "failed" if findings else "passed",
        "total_issues": len(findings),
        "issues": findings
    }
    return json.dumps(result)


# Tool: Generate security summary
def generate_security_summary(
    secrets_result: Annotated[str, "Results from secrets scan"],
    sql_result: Annotated[str, "Results from SQL injection scan"],
    deps_result: Annotated[str, "Results from dependency scan"],
    antipatterns_result: Annotated[str, "Results from anti-patterns scan"]
) -> str:
    """
    Generates a comprehensive security summary from all scan results.
    Returns a JSON string with consolidated results.
    """
    all_scans = []
    total_issues = 0
    overall_status = "passed"
    
    for result_str in [secrets_result, sql_result, deps_result, antipatterns_result]:
        try:
            result = json.loads(result_str)
            all_scans.append(result)
            total_issues += result.get("total_issues", 0)
            if result.get("status") == "failed":
                overall_status = "failed"
        except json.JSONDecodeError:
            pass
    
    summary = {
        "agent": "Security Auditor Agent",
        "status": overall_status,
        "total_issues": total_issues,
        "scans": all_scans,
        "summary": {
            "hardcoded_secrets": sum(1 for s in all_scans if s.get("scan_type") == "hardcoded_secrets" and s.get("status") == "failed"),
            "sql_injection": sum(1 for s in all_scans if s.get("scan_type") == "sql_injection" and s.get("status") == "failed"),
            "vulnerable_dependencies": sum(1 for s in all_scans if s.get("scan_type") == "vulnerable_dependencies" and s.get("status") == "failed"),
            "security_antipatterns": sum(1 for s in all_scans if s.get("scan_type") == "security_antipatterns" and s.get("status") == "failed")
        }
    }
    
    return json.dumps(summary)


# Create the Security Auditor Agent
security_auditor = Agent(
    model="gemini-2.5-flash",  # Use Ollama Llama 3.1 via LiteLLM
    name="security_auditor",
    description=(
        "Security specialist that scans pull request diffs for security vulnerabilities "
        "including hardcoded secrets, SQL injection risks, vulnerable dependencies, "
        "and common security anti-patterns."
    ),
    instruction="""
    You are a security expert auditing code changes in a pull request.
    
    STRICT RULES:
    - All tools return JSON format
    - Return ONLY the final JSON from generate_security_summary
    - Do NOT add explanatory text outside the JSON
    - Do NOT format or pretty-print the response
    
    Your responsibilities:
    1. Scan the PR diff for hardcoded secrets (API keys, passwords, tokens)
    2. Identify SQL injection vulnerabilities
    3. Check for vulnerable dependencies
    4. Detect security anti-patterns and unsafe coding practices
    
    Process:
    - Use scan_hardcoded_secrets to check for exposed credentials (returns JSON)
    - Use scan_sql_injection to find SQL injection risks (returns JSON)
    - Use scan_vulnerable_dependencies to identify insecure package versions (returns JSON)
    - Use scan_security_antipatterns to catch common security mistakes (returns JSON)
    - Use generate_security_summary with ALL four results to create final JSON report
    
    Always run ALL security checks in sequence and return the final consolidated JSON.
    Be thorough but avoid false positives - focus on actual security risks.
    """,
    tools=[
        scan_hardcoded_secrets,
        scan_sql_injection,
        scan_vulnerable_dependencies,
        scan_security_antipatterns,
        generate_security_summary,
    ],
)


def read_sample_file(filename: str = "sample.py") -> str:
    """
    Reads the sample Python file from the current directory.
    
    Args:
        filename: Name of the file to read (default: sample.py)
        
    Returns:
        Content of the file as a string
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    file_path = Path(__file__).parent / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"File '{filename}' not found in {file_path.parent}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_report(report_content: str, filename: str = "report.txt") -> None:
    """
    Writes the security audit report to a text file.
    
    Args:
        report_content: The report content to write
        filename: Name of the report file (default: report.txt)
    """
    file_path = Path(__file__).parent / filename
    
    # Add timestamp and header
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_report = f"""
{'='*70}
SECURITY AUDIT REPORT
Generated: {timestamp}
{'='*70}

{report_content}

{'='*70}
End of Report
{'='*70}
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(full_report)
    
    print(f"✅ Report written to: {file_path}")


def audit_pr_diff(code_content: str, session_service: InMemorySessionService, 
                  app_name: str, user_id: str, session_id: str) -> str:
    """
    Main function to audit code for security issues using ADK Runner.
    Now includes caching to handle rate limits.
    
    Args:
        code_content: The code content to audit
        session_service: ADK session service
        app_name: Application name for the session
        user_id: User ID for the session
        session_id: Session ID for the audit
        
    Returns:
        Security audit report as a string
    """
    agent_name = "security_auditor_adk"
    
    # Check cache first
    print(f"\n🔍 Checking cache for {agent_name}...")
    cached_response = cache_manager.get(agent_name, code_content)
    if cached_response is not None:
        print(f"✅ Cache HIT! Returning cached response.")
        print(f"   (No API call needed - using cached result)\n")
        return cached_response if isinstance(cached_response, str) else json.dumps(cached_response, indent=2)
    
    print(f"⚠️ Cache MISS - Calling Google ADK API...")
    print(f"   (This response will be cached for future use)\n")
    
    # Create the runner with the security auditor agent
    runner = Runner(
        agent=security_auditor,
        app_name=app_name,
        session_service=session_service
    )
    
    # Create the user query content
    query = f"""
    Please conduct a comprehensive security audit of this code:
    
    {code_content}
    
    Run all security checks and provide a detailed summary report.
    """
    
    user_content = types.Content(
        role='user',
        parts=[types.Part(text=query)]
    )
    
    # Run the agent and collect all responses
    responses = []
    print("\n🤖 Agent is processing...\n")
    
    for event in runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=user_content
    ):
        # Debug: print event type and attributes
        print(f"Event type: {type(event).__name__}")
        print(f"Event attributes: {dir(event)}")
        
        # Try to get text from various possible attributes
        text_content = None
        
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts') and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_content = part.text
                        print(f"📝 Collected response part ({len(part.text)} chars)")
                        responses.append(part.text)
        
        # Also try direct text attribute
        if hasattr(event, 'text') and event.text:
            text_content = event.text
            print(f"📝 Collected direct text ({len(event.text)} chars)")
            responses.append(event.text)
        
        # Print first 200 chars of any text found
        if text_content:
            print(f"Preview: {text_content[:200]}...")
        
        # Check for final response
        if hasattr(event, 'is_final_response'):
            if callable(event.is_final_response):
                if event.is_final_response():
                    print("✅ Received final response marker")
            elif event.is_final_response:
                print("✅ Received final response marker")
    
    # Combine all responses
    final_response = "\n\n".join(responses) if responses else ""
    
    if not final_response:
        print("⚠️ Warning: No text content found in agent responses")
        final_response = "No response received from agent. Please check the API configuration and try again."
    else:
        # Cache the successful response for future use
        print(f"\n💾 Caching response for agent: {agent_name}")
        cache_manager.set(agent_name, code_content, final_response)
        print(f"✅ Response cached successfully!\n")
    
    return final_response


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("\n" + "=" * 70)
        print("🔒 SECURITY AUDITOR AGENT")
        print("=" * 70)
        
        # ADK Configuration
        APP_NAME = "security_audit_app"
        USER_ID = "auditor_user"
        SESSION_ID = "audit_session_001"
        
        try:
            # Initialize session service
            session_service = InMemorySessionService()
            
            # Create a session (async)
            session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID
            )
            print(f"✅ Session created: {SESSION_ID}")
            
            # Read the sample.py file
            print("📖 Reading sample.py...")
            code_content = read_sample_file("sample.py")
            print(f"✅ Successfully read {len(code_content)} characters from sample.py")
            print()
            
            # Run the security audit
            print("🔒 Running security audit...")
            result = audit_pr_diff(
                code_content, 
                session_service, 
                APP_NAME, 
                USER_ID, 
                SESSION_ID
            )
            
            # Display result in console
            print()
            print("=" * 70)
            print(result)
            print("=" * 70)
            
            # Write report to file
            print()
            write_report(result)
            
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            print("Please create a 'sample.py' file in the same directory as this script.")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            import traceback
            traceback.print_exc()
    
    # Run the async main function
    asyncio.run(main())