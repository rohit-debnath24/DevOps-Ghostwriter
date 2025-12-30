"""
Groq-based agent implementation
Fast and high-quota alternative to Google Gemini
"""
import os
import asyncio
from typing import Dict, Any, List
from groq import AsyncGroq
from dotenv import load_dotenv
import json

load_dotenv('../.env.local')

# Initialize Groq client
groq_client = AsyncGroq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Default model - fast and capable
DEFAULT_MODEL = "llama-3.3-70b-versatile"  # or "mixtral-8x7b-32768"

async def security_auditor_groq(diff_text: str) -> Dict[str, Any]:
    """
    Security auditor using Groq LLM
    """
    prompt = f"""You are a security auditor. Analyze this code diff for security vulnerabilities.

Respond in JSON format:
{{
    "is_secure": boolean,
    "vulnerabilities": [
        {{
            "type": "string (e.g., 'SQL Injection', 'Hardcoded Secret')",
            "severity": "Critical|High|Medium|Low",
            "description": "string",
            "file_path": "string or null",
            "line_number": number or null,
            "reasoning_path": "string explaining why this is a vulnerability",
            "confidence_score": float (0.0 to 1.0)
        }}
    ],
    "summary_reasoning": "string"
}}

Diff:
{diff_text}
"""

    try:
        response = await groq_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a security expert. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Groq Security Auditor Error: {e}")
        return {
            "is_secure": False,
            "vulnerabilities": [],
            "summary_reasoning": f"Analysis failed: {str(e)}"
        }


async def runtime_validator_groq(diff_text: str) -> Dict[str, Any]:
    """
    Runtime validator using Groq LLM
    """
    prompt = f"""You are a runtime validator. Analyze this code diff for potential runtime issues.

Respond in JSON format:
{{
    "steps": [
        {{
            "step_name": "string",
            "description": "string",
            "expected_output": "string",
            "actual_output": "string",
            "status": "PASS|FAIL"
        }}
    ],
    "final_verdict": "PASS|FAIL",
    "error_recovery_attempted": boolean,
    "recovery_trace": "string or null"
}}

Check for:
- Syntax errors
- Undefined variables
- Type mismatches
- Infinite loops
- Logic errors

Diff:
{diff_text}
"""

    try:
        response = await groq_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a code quality expert. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Groq Runtime Validator Error: {e}")
        return {
            "steps": [],
            "final_verdict": "FAIL",
            "error_recovery_attempted": True,
            "recovery_trace": str(e)
        }


async def ghostwriter_groq(
    security_report: Dict[str, Any],
    runtime_report: Dict[str, Any],
    pr_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Ghostwriter using Groq LLM - synthesizes reports into GitHub comment
    """
    prompt = f"""You are a technical writer creating a GitHub PR review comment.

Security Report:
{json.dumps(security_report, indent=2)}

Runtime Report:
{json.dumps(runtime_report, indent=2)}

PR Info:
{json.dumps(pr_info, indent=2)}

Create a professional Markdown comment with:
1. Executive summary with emoji indicators
2. Security findings (if any)
3. Runtime/logic issues (if any)
4. Overall recommendation

Respond in JSON:
{{
    "status": "success|warning|error",
    "comment": "markdown string...",
    "confidence_score": float (0.0 to 1.0)
}}
"""

    try:
        response = await groq_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional technical writer. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Groq Ghostwriter Error: {e}")
        return {
            "status": "error",
            "comment": f"Failed to generate review: {str(e)}",
            "confidence_score": 0.0
        }


async def analyze_pr_groq(
    repo_id: str,
    pr_id: int,
    diff_text: str,
    title: str = None
) -> Dict[str, Any]:
    """
    Complete PR analysis using Groq agents
    """
    print(f"\n🚀 GROQ AGENT ANALYSIS - PR #{pr_id}")
    print(f"Repository: {repo_id}")
    print(f"Model: {DEFAULT_MODEL}")
    print("=" * 80)
    
    try:
        # Run agents in parallel
        print("\n⚡ Running Security & Runtime analysis in parallel...")
        security_task = security_auditor_groq(diff_text)
        runtime_task = runtime_validator_groq(diff_text)
        
        security_report, runtime_report = await asyncio.gather(security_task, runtime_task)
        
        print(f"✅ Security: {len(security_report.get('vulnerabilities', []))} issues")
        print(f"✅ Runtime: {runtime_report.get('final_verdict', 'unknown')}")
        
        # Synthesize with Ghostwriter
        print("\n✍️  Generating PR comment...")
        pr_info = {
            "repo_id": repo_id,
            "pr_id": pr_id,
            "title": title
        }
        
        final_verdict = await ghostwriter_groq(security_report, runtime_report, pr_info)
        
        print(f"✅ Analysis Complete - Confidence: {final_verdict['confidence_score']:.2%}")
        
        return {
            "status": final_verdict["status"],
            "comment": final_verdict["comment"],
            "confidence_score": final_verdict["confidence_score"],
            "security_snapshot": security_report,
            "runtime_snapshot": runtime_report,
            "metadata": {
                "model": DEFAULT_MODEL,
                "provider": "groq"
            }
        }
        
    except Exception as e:
        print(f"❌ Groq Analysis Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "comment": f"Analysis failed: {str(e)}",
            "confidence_score": 0.0,
            "security_snapshot": {},
            "runtime_snapshot": {},
            "error": str(e)
        }
