import os
import asyncio
import weave
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

# Import orchestral agent integration
try:
    from orchestral_integration import analyze_pr_with_orchestral_agents, get_cache_stats, clear_cache
    ORCHESTRAL_AVAILABLE = True
    print("INFO: Orchestral agent system loaded successfully")
except ImportError as e:
    ORCHESTRAL_AVAILABLE = False
    print(f"WARNING: Orchestral agent system not available: {e}")
    print("INFO: Falling back to simple agent implementation")

# Import Groq agents (high-quota alternative)
try:
    from groq_agents import analyze_pr_groq
    GROQ_AVAILABLE = True
    print("INFO: Groq agent system loaded successfully")
except ImportError as e:
    GROQ_AVAILABLE = False
    print(f"WARNING: Groq agent system not available: {e}")

# Load environment variables
load_dotenv('../.env.local')

# Initialize W&B Weave
# This captures all inputs/outputs of functions decorated with @weave.op
WEAVE_PROJECT = "devops-ghostwriter"
try:
    # Check if WANDB_API_KEY is set, otherwise disable weave
    if os.getenv("WANDB_API_KEY"):
        weave.init(WEAVE_PROJECT)
        print(f"INFO: Weave initialized for project '{WEAVE_PROJECT}'")
    else:
        print("INFO: WANDB_API_KEY not set. Weave observability is disabled.")
        os.environ["WANDB_MODE"] = "disabled"
except Exception as e:
    print(f"Warning: Failed to initialize Weave. Observability will be disabled. Error: {e}")
    os.environ["WANDB_MODE"] = "disabled"

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found. Agents will fail.")
else:
    genai.configure(api_key=api_key)

app = FastAPI()

# -----------------------------------------------------------------------------
# W&B / Agent Data Models (Schema)
# -----------------------------------------------------------------------------

class AnalysisRequest(BaseModel):
    repo_id: str
    pr_id: int
    diff_text: str
    title: Optional[str] = None

class Vulnerability(BaseModel):
    type: str = Field(description="Category (e.g., 'Secret Leak', 'SQL Injection')")
    severity: str = Field(description="Critical, High, Medium, or Low")
    description: str = Field(description="Brief explanation of the finding")
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    reasoning_path: str = Field(description="Chain-of-thought explaining why this is a vulnerability")
    confidence_score: float = Field(description="0.0 to 1.0 score indicating certainty")

class SecurityReport(BaseModel):
    is_secure: bool
    vulnerabilities: List[Vulnerability]
    summary_reasoning: str

class ValidationStep(BaseModel):
    step_name: str
    description: str
    expected_output: str
    actual_output: str
    status: str = Field(description="PASS or FAIL")

class ValidationReport(BaseModel):
    steps: List[ValidationStep]
    error_recovery_attempted: bool = False
    recovery_trace: Optional[str] = None
    final_verdict: str = Field(description="PASS or FAIL")

class FinalVerdict(BaseModel):
    status: str
    comment: str
    confidence_score: float

# -----------------------------------------------------------------------------
# Agents
# -----------------------------------------------------------------------------

@weave.op()
async def security_auditor_agent(diff_text: str) -> SecurityReport:
    """
    Security Auditor: Analyzes diffs for specific vulnerabilities using CoT.
    Returns structured data for W&B logging.
    """
    prompt = f"""
    You are a Security Auditor. Analyze this Git Diff for:
    1. Hardcoded Secrets (API keys, passwords)
    2. Injection Risks (SQL, Command, XSS)
    3. Malicious Dependencies

    Respond STRICTLY in JSON format matching this schema:
    {{
        "is_secure": boolean,
        "summary_reasoning": "High level analysis...",
        "vulnerabilities": [
            {{
                "type": "string",
                "severity": "High/Medium/Low",
                "description": "string",
                "file_path": "string or null",
                "line_number": 0,
                "reasoning_path": "Step-by-step logic finding this issue...",
                "confidence_score": 0.0 to 1.0
            }}
        ]
    }}

    Diff:
    {diff_text}
    """
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash", generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)
        # Parse JSON to validate against Pydantic model
        data = json.loads(response.text)
        report = SecurityReport(**data)
        return report
    except Exception as e:
        print(f"Security Agent Error: {e}")
        # Return a fallback "safe" report with error note to prevent crash
        return SecurityReport(
            is_secure=False, 
            vulnerabilities=[], 
            summary_reasoning=f"Agent failed to run: {str(e)}"
        )

@weave.op()
async def runtime_validator_agent(diff_text: str) -> ValidationReport:
    """
    Runtime Validator: Attempts to 'execute' or simulate execution logic.
    For this demo, it generates a test plan and simulates the comparison.
    """
    prompt = f"""
    You are a Runtime Validator. 
    1. Analyze the logic changes in the Diff.
    2. Design 3 specific test cases.
    3. PREDICT the 'Expected Output'.
    4. SIMULATE the 'Actual Output' (assume code works unless obvious syntax error).
    
    Respond STRICTLY in JSON format:
    {{
        "final_verdict": "PASS" or "FAIL",
        "error_recovery_attempted": false,
        "steps": [
            {{
                "step_name": "Test Case 1",
                "description": "Testing auth flow...",
                "expected_output": "200 OK",
                "actual_output": "200 OK",
                "status": "PASS"
            }}
        ]
    }}

    Diff:
    {diff_text}
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash", generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)
        data = json.loads(response.text)
        return ValidationReport(**data)
    except Exception as e:
        print(f"Runtime Agent Error: {e}")
        return ValidationReport(steps=[], final_verdict="FAIL", error_recovery_attempted=True, recovery_trace=str(e))

@weave.op()
async def ghostwriter_agent(security_report: SecurityReport, validation_report: ValidationReport, pr_info: dict) -> FinalVerdict:
    """
    Ghostwriter: Synthesizes reports into a final GitHub comment and score.
    Uses confidence weighting.
    """
    
    # Calculate aggregate confidence
    # If security is insecure, confidence in "Passing" drops.
    sec_score = 100.0 if security_report.is_secure else 50.0
    
    # Simple formatting for prompt
    prompt = f"""
    You are the DevOps Ghostwriter. Synthesize these reports into a final PR comment.
    
    PR: {pr_info['repo_id']} #{pr_info['pr_id']}
    
    Security Report:
    Secure: {security_report.is_secure}
    Reasoning: {security_report.summary_reasoning}
    Vulnerabilities: {len(security_report.vulnerabilities)} found.
    
    Runtime Report:
    Verdict: {validation_report.final_verdict}
    Tests Passed: {len([s for s in validation_report.steps if s.status == 'PASS'])}/{len(validation_report.steps)}
    
    Task:
    1. Generate a professional Markdown comment for GitHub.
    2. Calculate a final "Confidence Score" (0.0 - 1.0).
    
    Respond in JSON:
    {{
        "status": "success",
        "comment": "markdown string...",
        "confidence_score": 0.95
    }}
    """
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash", generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)
        data = json.loads(response.text)
        return FinalVerdict(**data)
    except Exception as e:
        return FinalVerdict(status="error", comment=f"Failed to synthesize: {e}", confidence_score=0.0)

@weave.op()
async def orchestration_agent(request: AnalysisRequest):
    """
    Orchestrator: Manages the parallel workflow and traces the task decomposition.
    """
    print(f"🚀 Starting Analysis for PR #{request.pr_id}")
    
    # 1. Trace Task Decomposition (Implicitly logged by Weave via inputs)
    # in a real complex agent, we might have an LLM call here to decide WHICH agents to run.
    # For now, we hardcode the fan-out.
    
    # 2. Parallel Execution
    security_task = security_auditor_agent(request.diff_text)
    runtime_task = runtime_validator_agent(request.diff_text)
    
    sec_report, run_report = await asyncio.gather(security_task, runtime_task)
    
    # 3. Synthesis
    final_verdict = await ghostwriter_agent(
        sec_report,
        run_report,
        {"repo_id": request.repo_id, "pr_id": request.pr_id}
    )
    
    print(f"✅ Analysis Complete. Score: {final_verdict.confidence_score}")
    
    return {
        "status": final_verdict.status,
        "comment": final_verdict.comment,
        "confidence_score": final_verdict.confidence_score,
        "security_snapshot": sec_report.model_dump(),
        "runtime_snapshot": run_report.model_dump()
    }

# -----------------------------------------------------------------------------
# API Routes
# -----------------------------------------------------------------------------

@app.post("/analyze")
async def analyze_pr(request: AnalysisRequest):
    """
    Analyzes a Pull Request using available agent systems in priority order:
    1. Groq (fastest, highest quota)
    2. Orchestral agents (Google ADK with caching)
    3. Simple Gemini agents (fallback)
    """
    try:
        # Try Groq first (best quota)
        if GROQ_AVAILABLE and os.getenv("GROQ_API_KEY"):
            print(f"Using Groq Agent System for PR #{request.pr_id}")
            result = await analyze_pr_groq(
                repo_id=request.repo_id,
                pr_id=request.pr_id,
                diff_text=request.diff_text,
                title=request.title
            )
            return result
            
        # Try orchestral agents (Google ADK with caching)
        elif ORCHESTRAL_AVAILABLE:
            print(f"Using Orchestral Agent System for PR #{request.pr_id}")
            result = await analyze_pr_with_orchestral_agents(
                repo_id=request.repo_id,
                pr_id=request.pr_id,
                diff_text=request.diff_text,
                title=request.title
            )
            return result
            
        # Fall back to simple agent implementation
        else:
            print(f"Using Simple Agent System for PR #{request.pr_id}")
            result = await orchestration_agent(request)
            return result
            
    except Exception as e:
        print(f"Error processing analysis: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "python-agent-engine-v2",
        "groq_agents": GROQ_AVAILABLE,
        "orchestral_agents": ORCHESTRAL_AVAILABLE
    }

@app.get("/cache/stats")
def cache_stats():
    """Get cache statistics (only available with orchestral agents)."""
    if not ORCHESTRAL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Orchestral agent system not available")
    try:
        return get_cache_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cache/clear")
def cache_clear():
    """Clear all cached analysis results."""
    if not ORCHESTRAL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Orchestral agent system not available")
    try:
        success = clear_cache()
        return {"success": success, "message": "Cache cleared" if success else "Failed to clear cache"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
