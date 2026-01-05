from groq import Groq
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Groq API key
GROQ_API_KEY = os.getenv("GHOSTWRITER_API_KEY") or os.getenv("GROQ_API_KEY")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

"""
Ghostwriter Agent (Groq-powered) - The Synthesizer for PR Reviews
Gathers findings from Security and Runtime agents and writes professional GitHub comments
with proper markdown formatting, summaries, and recommendations.
"""


def synthesize_pr_review(
    security_report: dict, runtime_report: dict, pr_metadata: dict
) -> str:
    """
    Synthesize PR review using Groq AI to generate professional comment.

    Args:
        security_report: Security audit results (dict)
        runtime_report: Runtime validation results (dict)
        pr_metadata: PR metadata (files changed, additions, deletions)

    Returns:
        Formatted markdown PR comment
    """
    print("\n" + "=" * 70)
    print("✍️ GHOSTWRITER AGENT (Groq)")
    print("=" * 70)

    # Extract key information
    security_issues = security_report.get("total_issues", 0)
    security_status = security_report.get("status", "unknown")

    runtime_issues = runtime_report.get("total_issues", 0)
    runtime_status = runtime_report.get("status", "unknown")

    files_changed = pr_metadata.get("files_changed", 0)
    additions = pr_metadata.get("additions", 0)
    deletions = pr_metadata.get("deletions", 0)

    # Prepare context for Groq
    prompt = f"""You are a professional technical writer creating a GitHub PR review comment.

**Security Analysis Results:**
- Status: {security_status}
- Issues Found: {security_issues}
- Details: {json.dumps(security_report.get('scans', []), indent=2)}

**Runtime Validation Results:**
- Status: {runtime_status}
- Issues Found: {runtime_issues}
- Details: {json.dumps(runtime_report.get('issues', []), indent=2)}

**PR Statistics:**
- Files Changed: {files_changed}
- Lines Added: +{additions}
- Lines Removed: -{deletions}

Create a professional, well-formatted GitHub PR comment with:

1. **Header**: Summary line with emojis (✅ for pass, ⚠️ for warnings, ❌ for critical)
2. **Security Section**: List security findings with severity
3. **Runtime Section**: List runtime/logic issues
4. **Statistics Table**: Show PR metrics
5. **Recommendations**: Actionable next steps

Use proper markdown formatting. Be concise but informative.
Make it easy to scan with emojis and clear sections.

Return ONLY the markdown comment, no other text."""

    try:
        print("🤖 Generating PR comment with Groq AI...")

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional technical writer. Create clear, well-formatted GitHub PR comments.",
                },
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2000,
        )

        comment = chat_completion.choices[0].message.content

        # Add footer
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comment += f"""

---

*🤖 Automated review generated at {timestamp}*  
*Powered by DevOps-GhostWriter (Groq AI)*  
*Security Auditor • Runtime Validator • Ghostwriter*
"""

        print("✅ PR comment generated successfully")
        return comment

    except Exception as e:
        print(f"❌ Error generating comment: {e}")

        # Fallback to basic template
        return generate_fallback_comment(
            security_issues,
            security_status,
            runtime_issues,
            runtime_status,
            files_changed,
            additions,
            deletions,
        )


def generate_fallback_comment(
    security_issues: int,
    security_status: str,
    runtime_issues: int,
    runtime_status: str,
    files_changed: int,
    additions: int,
    deletions: int,
) -> str:
    """Generate a basic comment if Groq API fails."""

    # Determine overall status
    if security_issues == 0 and runtime_issues == 0:
        overall_emoji = "✅"
        overall_status = "All Checks Passed"
    elif security_issues > 0 or runtime_issues > 0:
        overall_emoji = "⚠️"
        overall_status = "Issues Found"
    else:
        overall_emoji = "❓"
        overall_status = "Review Incomplete"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""## 🔍 Automated PR Review Summary

{overall_emoji} **Status:** {overall_status}

---

### 🔒 Security Analysis
**Status:** {"✅ Passed" if security_issues == 0 else f"⚠️ {security_issues} issue(s) found"}

{f"{security_issues} security issue(s) detected. Please review." if security_issues > 0 else "No security vulnerabilities detected."}

---

### 🧮 Runtime & Logic Check
**Status:** {"✅ Passed" if runtime_issues == 0 else f"⚠️ {runtime_issues} issue(s) found"}

{f"{runtime_issues} runtime issue(s) detected. Please review." if runtime_issues > 0 else "No runtime issues detected."}

---

### 📊 Change Statistics

| Metric | Value |
|--------|-------|
| Files Changed | {files_changed} |
| Lines Added | +{additions} |
| Lines Removed | -{deletions} |
| Net Change | {additions - deletions:+d} |
| Security Issues | {security_issues} |
| Runtime Issues | {runtime_issues} |

---

### 💡 Recommendations

{"- 🔒 **Security:** Address security vulnerabilities before merging" if security_issues > 0 else ""}
{"- 🧮 **Runtime:** Fix runtime issues before merging" if runtime_issues > 0 else ""}
{"- ✅ **Ready to Merge:** All checks passed!" if security_issues == 0 and runtime_issues == 0 else ""}

---

*🤖 Automated review generated at {timestamp}*  
*Powered by DevOps-GhostWriter (Groq AI)*
"""


if __name__ == "__main__":
    # Test the Ghostwriter
    print("\n" + "=" * 70)
    print("✍️ TESTING GHOSTWRITER AGENT")
    print("=" * 70)

    # Sample data
    security_report = {
        "agent": "Security Auditor",
        "status": "failed",
        "total_issues": 2,
        "scans": [
            {
                "scan_type": "hardcoded_secrets",
                "status": "failed",
                "total_issues": 1,
                "issues": [
                    {
                        "type": "Hardcoded Secret",
                        "secret_type": "API Key",
                        "severity": "CRITICAL",
                        "line": 42,
                    }
                ],
            }
        ],
    }

    runtime_report = {
        "agent": "Runtime Validator",
        "status": "passed",
        "total_issues": 0,
        "issues": [],
    }

    pr_metadata = {"files_changed": 3, "additions": 145, "deletions": 23}

    comment = synthesize_pr_review(security_report, runtime_report, pr_metadata)

    print("\n" + "=" * 70)
    print("GENERATED PR COMMENT:")
    print("=" * 70)
    print(comment)
    print("=" * 70)
