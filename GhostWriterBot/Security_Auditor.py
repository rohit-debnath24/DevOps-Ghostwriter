from groq import Groq
import os
from pathlib import Path
from datetime import datetime
import json
import sys
from dotenv import load_dotenv

# Import cache_manager from current directory
try:
    from cache_manager import get_cache_manager
except ImportError:
    # Fallback if running from different directory
    sys.path.append(str(Path(__file__).parent))
    from cache_manager import get_cache_manager

# Load environment variables
load_dotenv()

# Get Groq API key
GROQ_API_KEY = os.getenv("SECURITY_AUDITOR_API_KEY") or os.getenv("GROQ_API_KEY")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize cache manager
cache_manager = get_cache_manager(
    cache_dir=str(Path(__file__).parent / "agent_cache"), default_ttl_hours=24
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
def scan_hardcoded_secrets(
    code_diff: Annotated[str, "The PR diff content to scan"],
) -> str:
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
        "Private Key": r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
        "OAuth Token": r'(?i)(oauth[_-]?token|access[_-]?token)\s*[:=]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
        "GitHub Token": r"(?i)(gh[ps]_[a-zA-Z0-9]{36,})",
        "Generic Secret": r'(?i)(secret|token|bearer)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{32,})["\']',
    }

    lines = code_diff.split("\n")
    for line_num, line in enumerate(lines, 1):
        # Check all lines (not just those starting with +)
        for secret_type, pattern in patterns.items():
            if re.search(pattern, line):
                findings.append(
                    {
                        "type": "Hardcoded Secret",
                        "secret_type": secret_type,
                        "severity": "CRITICAL",
                        "line": line_num,
                        "code_snippet": line.strip()[:80],
                        "recommendation": "Remove hardcoded secrets and use environment variables or secret management systems",
                    }
                )

    result = {
        "scan_type": "hardcoded_secrets",
        "status": "failed" if findings else "passed",
        "total_issues": len(findings),
        "issues": findings,
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
        "Format in SQL": r"(?i)(execute|exec|query)\s*\([^)]*\.format\(",
        "Unsafe SQL construction": r"(?i)(select|insert|update|delete).*[+%].*(?:where|from|into)",
    }

    lines = code_diff.split("\n")
    for line_num, line in enumerate(lines, 1):
        for vuln_type, pattern in patterns.items():
            if re.search(pattern, line):
                findings.append(
                    {
                        "type": "SQL Injection Vulnerability",
                        "vulnerability_type": vuln_type,
                        "severity": "HIGH",
                        "line": line_num,
                        "code_snippet": line.strip()[:80],
                        "recommendation": "Use parameterized queries or ORM to prevent SQL injection",
                    }
                )

    result = {
        "scan_type": "sql_injection",
        "status": "failed" if findings else "passed",
        "total_issues": len(findings),
        "issues": findings,
    }
    return json.dumps(result)


# Tool: Scan for vulnerable dependencies
def scan_vulnerable_dependencies(
    code_diff: Annotated[str, "The PR diff content to scan"],
) -> str:
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

    lines = code_diff.split("\n")
    for line_num, line in enumerate(lines, 1):
        # Check requirements.txt or similar files
        for package, vuln_versions in vulnerable_packages.items():
            for version in vuln_versions:
                if (
                    f"{package}=={version}" in line.lower()
                    or f"{package}@{version}" in line.lower()
                ):
                    findings.append(
                        {
                            "type": "Vulnerable Dependency",
                            "package": package,
                            "vulnerable_version": version,
                            "severity": "HIGH",
                            "line": line_num,
                            "recommendation": f"Update {package} to the latest secure version",
                        }
                    )

    result = {
        "scan_type": "vulnerable_dependencies",
        "status": "failed" if findings else "passed",
        "total_issues": len(findings),
        "issues": findings,
    }
    return json.dumps(result)


# Tool: Scan for general security anti-patterns
def scan_security_antipatterns(
    code_diff: Annotated[str, "The PR diff content to scan"],
) -> str:
    """
    Scans for common security anti-patterns and unsafe practices.
    Returns findings as a JSON string.
    """
    findings = []

    # Common security anti-patterns
    patterns = {
        "eval() usage": (
            r"\beval\s*\(",
            "Avoid eval() - it can execute arbitrary code",
            "HIGH",
        ),
        "exec() usage": (
            r"\bexec\s*\(",
            "Avoid exec() - it can execute arbitrary code",
            "HIGH",
        ),
        "pickle.loads()": (
            r"pickle\.loads\s*\(",
            "Pickle is unsafe for untrusted data - use JSON",
            "MEDIUM",
        ),
        "shell=True": (
            r"shell\s*=\s*True",
            "Avoid shell=True - use shell=False with list arguments",
            "HIGH",
        ),
        "md5 hashing": (
            r"\bhashlib\.md5\s*\(",
            "MD5 is cryptographically broken - use SHA256 or better",
            "MEDIUM",
        ),
        "assert for validation": (
            r"^\s*assert\s+",
            "Don't use assert for data validation - it can be disabled",
            "LOW",
        ),
        "hardcoded localhost": (
            r"(?i)(localhost|127\.0\.0\.1):[0-9]+",
            "Avoid hardcoded hosts - use configuration",
            "LOW",
        ),
    }

    lines = code_diff.split("\n")
    for line_num, line in enumerate(lines, 1):
        for pattern_name, (pattern, recommendation, severity) in patterns.items():
            if re.search(pattern, line):
                findings.append(
                    {
                        "type": "Security Anti-Pattern",
                        "pattern_name": pattern_name,
                        "severity": severity,
                        "line": line_num,
                        "code_snippet": line.strip()[:80],
                        "recommendation": recommendation,
                    }
                )

    result = {
        "scan_type": "security_antipatterns",
        "status": "failed" if findings else "passed",
        "total_issues": len(findings),
        "issues": findings,
    }
    return json.dumps(result)


def run_security_audit_with_groq(code_diff: str) -> dict:
    """
    Run security audit using Groq API to analyze the scan results.

    Args:
        code_diff: The PR diff content to scan

    Returns:
        Consolidated security report as dictionary
    """
    # Run all scans
    secrets_result = scan_hardcoded_secrets(code_diff)
    sql_result = scan_sql_injection(code_diff)
    deps_result = scan_vulnerable_dependencies(code_diff)
    antipatterns_result = scan_security_antipatterns(code_diff)

    # Parse results
    all_scans = []
    total_issues = 0

    for result_str in [secrets_result, sql_result, deps_result, antipatterns_result]:
        try:
            result = json.loads(result_str)
            all_scans.append(result)
            total_issues += result.get("total_issues", 0)
        except json.JSONDecodeError:
            pass

    # Use Groq to generate summary
    prompt = f"""You are a security auditor. Analyze these security scan results and provide a brief summary.

Scan Results:
{json.dumps(all_scans, indent=2)}

Provide a JSON response with:
- overall_status: "passed" or "failed"
- total_issues: number
- critical_count: number of CRITICAL issues
- high_count: number of HIGH issues
- summary: brief text summary

Return ONLY valid JSON, no other text."""

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a security expert. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",  # Groq's best model
            temperature=0.1,
            max_tokens=1000,
        )

        llm_response = chat_completion.choices[0].message.content

        # Try to parse LLM response as JSON
        try:
            llm_summary = json.loads(llm_response)
        except:
            llm_summary = {"summary": llm_response}

    except Exception as e:
        print(f"⚠️ Groq API error: {e}")
        llm_summary = {"summary": "LLM analysis unavailable"}

    # Build final report
    summary = {
        "agent": "Security Auditor Agent (Groq)",
        "status": "failed" if total_issues > 0 else "passed",
        "total_issues": total_issues,
        "scans": all_scans,
        "llm_analysis": llm_summary,
        "summary": {
            "hardcoded_secrets": sum(
                1
                for s in all_scans
                if s.get("scan_type") == "hardcoded_secrets"
                and s.get("status") == "failed"
            ),
            "sql_injection": sum(
                1
                for s in all_scans
                if s.get("scan_type") == "sql_injection" and s.get("status") == "failed"
            ),
            "vulnerable_dependencies": sum(
                1
                for s in all_scans
                if s.get("scan_type") == "vulnerable_dependencies"
                and s.get("status") == "failed"
            ),
            "security_antipatterns": sum(
                1
                for s in all_scans
                if s.get("scan_type") == "security_antipatterns"
                and s.get("status") == "failed"
            ),
        },
    }

    return summary


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

    with open(file_path, "r", encoding="utf-8") as f:
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

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_report)

    print(f"✅ Report written to: {file_path}")


def audit_pr_diff(
    code_content: str,
) -> str:
    """
    Main function to audit code for security issues using Groq API.
    Now includes caching to handle rate limits.

    Args:
        code_content: The code content to audit

    Returns:
        Security audit report as a JSON string
    """
    agent_name = "security_auditor_groq"

    # Check cache first
    print(f"\n🔍 Checking cache for {agent_name}...")
    cached_response = cache_manager.get(agent_name, code_content)
    if cached_response is not None:
        print(f"✅ Cache HIT! Returning cached response.")
        print(f"   (No API call needed - using cached result)\n")
        return (
            cached_response
            if isinstance(cached_response, str)
            else json.dumps(cached_response, indent=2)
        )

    print(f"⚠️ Cache MISS - Calling Groq API...")
    print(f"   (This response will be cached for future use)\n")

    # Run security audit with Groq
    print("\n🤖 Running security scans...\n")
    result = run_security_audit_with_groq(code_content)

    # Convert to JSON string
    final_response = json.dumps(result, indent=2)

    # Cache the successful response for future use
    print(f"\n💾 Caching response for agent: {agent_name}")
    cache_manager.set(agent_name, code_content, result)
    print(f"✅ Response cached successfully!\n")

    return final_response


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔒 SECURITY AUDITOR AGENT (Groq)")
    print("=" * 70)

    try:
        # Read the sample.py file
        print("\n📖 Reading sample.py...")
        code_content = read_sample_file("sample.py")
        print(f"✅ Successfully read {len(code_content)} characters from sample.py")
        print()

        # Run the security audit
        print("🔒 Running security audit...")
        result = audit_pr_diff(code_content)

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
