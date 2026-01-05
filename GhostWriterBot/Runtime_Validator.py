from groq import Groq
from pathlib import Path
from typing import List, Dict
import ast
import json
import os
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
GROQ_API_KEY = os.getenv("RUNTIME_VALIDATOR_API_KEY") or os.getenv("GROQ_API_KEY")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize cache manager
cache_manager = get_cache_manager(
    cache_dir=str(Path(__file__).parent / "agent_cache"), default_ttl_hours=24
)

"""
Runtime Validator Agent (Groq-powered)

✔ Uses Groq API for runtime analysis
✔ Detects syntax errors, undefined variables, logic flaws
✔ Strict JSON output
✔ No code execution
"""


# =========================================================
# STATIC CHECKS (DETERMINISTIC)
# =========================================================


def detect_syntax_errors(code: str) -> List[Dict]:
    """Detect Python syntax errors using AST parsing."""
    try:
        ast.parse(code)
        return []
    except SyntaxError as e:
        return [
            {
                "type": "Syntax Error",
                "severity": "CRITICAL",
                "description": e.msg,
                "location": f"Line {e.lineno}",
            }
        ]


def detect_infinite_loops(code: str) -> List[Dict]:
    """Detect obvious infinite loops."""
    issues = []
    for i, line in enumerate(code.splitlines(), 1):
        if line.replace(" ", "") == "whileTrue:":
            issues.append(
                {
                    "type": "Infinite Loop",
                    "severity": "HIGH",
                    "description": "Unconditional infinite loop detected.",
                    "location": f"Line {i}",
                }
            )
    return issues


def detect_undefined_variables(code: str) -> List[Dict]:
    """Detect potentially undefined variables using basic analysis."""
    issues = []
    try:
        tree = ast.parse(code)
        defined_vars = set()

        for node in ast.walk(tree):
            # Track assignments
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined_vars.add(target.id)
            # Check usage
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id not in defined_vars and node.id not in dir(__builtins__):
                    issues.append(
                        {
                            "type": "Potentially Undefined Variable",
                            "severity": "MEDIUM",
                            "description": f"Variable '{node.id}' may be used before assignment",
                            "location": f"Line {node.lineno}",
                        }
                    )
    except:
        pass

    return issues


# =========================================================
# GROQ-POWERED RUNTIME ANALYSIS
# =========================================================


def analyze_runtime_with_groq(code: str) -> List[Dict]:
    """
    Use Groq AI to detect runtime issues and logic flaws.

    Args:
        code: Python code to analyze

    Returns:
        List of runtime issues found
    """
    prompt = f"""You are a runtime code validator. Analyze this Python code for runtime issues.

Code to analyze:
```python
{code}
```

Detect:
- Undefined variables
- Type errors
- Runtime exceptions (division by zero, index errors, etc.)
- Logic flaws
- Resource leaks

Return ONLY valid JSON in this format:
{{
  "issues": [
    {{
      "type": "Issue type",
      "severity": "LOW | MEDIUM | HIGH | CRITICAL",
      "description": "Brief description",
      "location": "Line number or function name"
    }}
  ]
}}

If no issues, return: {{"issues": []}}
"""

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a code validator. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=1500,
        )

        response_text = chat_completion.choices[0].message.content

        # Try to parse JSON response
        try:
            result = json.loads(response_text)
            return result.get("issues", [])
        except json.JSONDecodeError:
            # If not valid JSON, try to extract issues from text
            return [
                {
                    "type": "Runtime Analysis",
                    "severity": "MEDIUM",
                    "description": response_text[:200],
                    "location": "General",
                }
            ]

    except Exception as e:
        print(f"⚠️ Groq API error: {e}")
        return []


# =========================================================
# MAIN VALIDATION FUNCTION
# =========================================================


def validate_runtime(code: str) -> Dict:
    """
    Main validation function that combines static and AI-powered checks.

    Args:
        code: Python code to validate

    Returns:
        Validation report as dictionary
    """
    agent_name = "runtime_validator_groq"

    # Check cache first
    print(f"\n🔍 Checking cache for {agent_name}...")
    cached_response = cache_manager.get(agent_name, code)
    if cached_response is not None:
        print(f"✅ Cache HIT! Returning cached response.")
        print(f"   (No API call needed - using cached result)\n")
        return cached_response

    print(f"⚠️ Cache MISS - Running validation...")
    print(f"   (This response will be cached for future use)\n")

    # Run static checks
    print("🔍 Running static checks...")
    static_issues = []
    static_issues.extend(detect_syntax_errors(code))
    static_issues.extend(detect_infinite_loops(code))
    static_issues.extend(detect_undefined_variables(code))

    print(f"   Found {len(static_issues)} static issues")

    # Run AI-powered analysis
    print("🤖 Running AI-powered runtime analysis...")
    ai_issues = analyze_runtime_with_groq(code)
    print(f"   Found {len(ai_issues)} AI-detected issues")

    # Combine all issues
    all_issues = static_issues + ai_issues

    result = {
        "agent": "Runtime Validator Agent (Groq)",
        "status": "passed" if not all_issues else "failed",
        "total_issues": len(all_issues),
        "issues": all_issues,
    }

    # Cache the result
    print(f"\n💾 Caching response for agent: {agent_name}")
    cache_manager.set(agent_name, code, result)
    print(f"✅ Response cached successfully!\n")

    return result


# =========================================================
# ENTRY POINT FOR TESTING
# =========================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔍 RUNTIME VALIDATOR AGENT (Groq)")
    print("=" * 70)

    # Test code
    test_code = """
def calculate(x, y):
    result = x / y  # Potential division by zero
    return result

def process_data(items):
    for item in items:
        print(undefined_var)  # Undefined variable
    
    while True:  # Infinite loop
        pass

calculate(10, 0)
"""

    result = validate_runtime(test_code)

    print("\n" + "=" * 70)
    print("VALIDATION RESULT:")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print("=" * 70)
