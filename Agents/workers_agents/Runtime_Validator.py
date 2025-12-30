from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from pathlib import Path
from typing import List, Dict
import ast
import json
import asyncio
import os
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
Runtime Validator Agent (ADK-correct)

✔ No direct model.complete()
✔ All LLM reasoning via Agent
✔ Strict JSON output
✔ No code suggestions
"""


# =========================================================
# FILE READER
# =========================================================

def read_sample_file(filename: str = "sample.py") -> str:
    path = Path(__file__).parent / filename
    if not path.exists():
        raise FileNotFoundError(f"{filename} not found")
    return path.read_text(encoding="utf-8")


# =========================================================
# STATIC CHECKS (DETERMINISTIC)
# =========================================================

def detect_syntax_errors(code: str) -> List[Dict]:
    try:
        ast.parse(code)
        return []
    except SyntaxError as e:
        return [{
            "type": "Syntax Error",
            "severity": "CRITICAL",
            "description": e.msg,
            "location": f"Line {e.lineno}"
        }]


def detect_infinite_loops(code: str) -> List[Dict]:
    issues = []
    for i, line in enumerate(code.splitlines(), 1):
        if line.replace(" ", "") == "whileTrue:":
            issues.append({
                "type": "Infinite Loop",
                "severity": "HIGH",
                "description": "Unconditional infinite loop detected.",
                "location": f"Line {i}"
            })
    return issues


# =========================================================
# AGENT (LLM DOES RUNTIME REASONING)
# =========================================================

runtime_validator_agent = Agent(
    name="runtime_validator",
    model="gemini-2.5-flash",  
    description="Detects runtime logic flaws without executing code.",
    instruction="""
You are a Runtime Validator Agent.

STRICT RULES:
- Read-only analysis
- Do NOT suggest fixes
- Do NOT rewrite code
- Do NOT output explanations outside JSON
- Do NOT include example code

TASK:
Detect runtime flaws such as:
- Undefined variables
- Runtime exceptions
- Logical execution flaws

Return ONLY valid JSON in this format:

{
  "issues": [
    {
      "type": "Undefined Variable | Runtime Exception | Logic Flaw",
      "severity": "LOW | MEDIUM | HIGH | CRITICAL",
      "description": "Concise explanation",
      "location": "function or line context"
    }
  ]
}

If no issues exist, return:
{ "issues": [] }
"""
)


# =========================================================
# MAIN PIPELINE
# =========================================================

async def validate_runtime():
    """Main validation pipeline that reads sample.py, checks cache, and validates code."""
    print("\n" + "="*70)
    print("🔍 RUNTIME VALIDATOR AGENT")
    print("="*70)
    
    # Read sample.py from the same directory
    print("\n📖 Reading sample.py...")
    code = read_sample_file("sample.py")
    print(f"✅ Successfully read {len(code)} characters from sample.py")
    
    agent_name = "runtime_validator_adk"
    
    # Check cache first
    print(f"\n🔍 Checking cache for {agent_name}...")
    cached_response = cache_manager.get(agent_name, code)
    if cached_response is not None:
        print(f"✅ Cache HIT! Returning cached response.")
        print(f"   (No API call needed - using cached result)\n")
        print("="*70)
        print("VALIDATION RESULT (from cache):")
        print("="*70)
        print(json.dumps(cached_response, indent=2))
        print("="*70)
        return cached_response
    
    print(f"⚠️ Cache MISS - Calling Google ADK API...")
    print(f"   (This response will be cached for future use)\n")

    static_issues = []
    static_issues.extend(detect_syntax_errors(code))
    static_issues.extend(detect_infinite_loops(code))

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="runtime_validation_app",
        user_id="runtime_user",
        session_id="runtime_session_001"
    )

    runner = Runner(
        agent=runtime_validator_agent,
        app_name="runtime_validation_app",
        session_service=session_service
    )

    user_content = types.Content(
        role="user",
        parts=[types.Part(text=code)]
    )

    llm_issues = []

    for event in runner.run(
        user_id="runtime_user",
        session_id="runtime_session_001",
        new_message=user_content
    ):
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                try:
                    parsed = json.loads(part.text)
                    llm_issues.extend(parsed.get("issues", []))
                except Exception:
                    pass

    all_issues = static_issues + llm_issues

    result = {
        "agent": "Runtime Validator Agent",
        "status": "passed" if not all_issues else "failed",
        "total_issues": len(all_issues),
        "issues": all_issues
    }
    
    # Cache the result for future use
    print(f"\n💾 Caching response for agent: {agent_name}")
    cache_manager.set(agent_name, code, result)
    print(f"✅ Response cached successfully!\n")

    print("="*70)
    print("VALIDATION RESULT:")
    print("="*70)
    print(json.dumps(result, indent=2))
    print("="*70)
    return result


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    asyncio.run(validate_runtime())