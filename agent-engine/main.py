import os
import asyncio
import weave
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv('../.env.local')

# Initialize Weave
WEAVE_PROJECT = "devops-ghostwriter"
try:
    weave.init(WEAVE_PROJECT)
except Exception as e:
    print(f"Warning: Failed to initialize Weave. Observability will be disabled. Error: {e}")

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Use a dummy key if missing to allow server start, but agents will fail
    print("WARNING: GEMINI_API_KEY not found.")
else:
    genai.configure(api_key=api_key)

print("INFO: Using Gemini 1.5 Flash for all agents.")

app = FastAPI()

class AnalysisRequest(BaseModel):
    repo_id: str
    pr_id: int
    diff_text: str
    title: str | None = None
    description: str | None = None

class AgentResult(BaseModel):
    agent_name: str
    verdict: str
    details: str

# -----------------------------------------------------------------------------
# Agents
# -----------------------------------------------------------------------------

@weave.op()
async def security_auditor_agent(diff_text: str) -> AgentResult:
    """
    Analyzes the diff for security vulnerabilities:
    - Hardcoded secrets
    - SQL Injection
    - Malicious dependencies
    """
    prompt = f"""
    You are a Security Auditor Specialist. Analyze the following Git Diff for security vulnerabilities.
    Focus on:
    1. Hardcoded secrets (API keys, passwords, tokens).
    2. SQL Injection vulnerabilities.
    3. Malicious dependency additions.
    
    If you find issues, list them clearly. If none, confirm the code is secure.
    
    Diff:
    {diff_text}
    """
    
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        
        return AgentResult(
            agent_name="Security Auditor",
            verdict="Analyzed",
            details=response.text
        )
    except Exception as e:
        print(f"Error in Security Agent: {e}")
        return AgentResult(agent_name="Security Auditor", verdict="Error", details=str(e))

@weave.op()
async def runtime_validator_agent(diff_text: str) -> AgentResult:
    """
    Runtime Validator Agent using Code Execution.
    Since we are in a backend environment, we use Gemini's sandbox to run a test.
    """
    prompt = f"""
    You are a Runtime Validator Agent. Your goal is to verify the logic in this Diff.
    
    1. Analyze the code changes.
    2. Create a small Python unit test that imports/mocks the changed logic and asserts expected behavior.
    3. EXECUTE this test using your code execution tool.
    4. Report if the test PASSED or FAILED and any errors.
    
    Diff:
    {diff_text}
    """
    
    try:
        # Enable code execution tool
        # note: code_execution might be limited on flash, but we try.
        model = genai.GenerativeModel(
            "gemini-2.0-flash-exp",
            tools="code_execution"
        )
        response = model.generate_content(prompt)
        
        return AgentResult(
            agent_name="Runtime Validator",
            verdict="Executed",
            details=response.text
        )
    except Exception as e:
        print(f"Error in Runtime Agent: {e}")
        return AgentResult(agent_name="Runtime Validator", verdict="Error", details=str(e))

@weave.op()
async def ghostwriter_agent(security_result: AgentResult, runtime_result: AgentResult, pr_info: dict) -> str:
    """
    Aggregates results into a GitHub comment.
    """
    prompt = f"""
    You are the 'DevOps Ghostwriter'. Synthesize the following agent reports into a professional GitHub PR comment.
    
    PR: {pr_info['repo_id']} #{pr_info['pr_id']}
    
    Security Auditor Report:
    {security_result.details}
    
    Runtime Validator Report:
    {runtime_result.details}
    
    Format:
    - Use Markdown.
    - Start with a status line (e.g., "✅ Logic Passed | ⚠️ Security Warning").
    - Provide a concise summary.
    - List detailed findings from each agent if import.
    """
    
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in Ghostwriter Agent: {e}")
        return f"Error generating comment: {e}"

@weave.op()
async def orchestration_agent(request: AnalysisRequest):
    """
    Manager Agent: Orchestrates the fan-out/gather pattern.
    """
    print(f"Starting analysis for PR #{request.pr_id} in {request.repo_id}")
    print("----------------------------------------------------------------")
    print(" RAW CODE DIFF SENT TO GEMINI:")
    print("----------------------------------------------------------------")
    print(request.diff_text)
    print("----------------------------------------------------------------")
    
    # Parallel execution of specialist agents
    security_task = security_auditor_agent(request.diff_text)
    runtime_task = runtime_validator_agent(request.diff_text)
    
    security_res, runtime_res = await asyncio.gather(security_task, runtime_task)
    
    # Synthesize results
    final_comment = await ghostwriter_agent(
        security_res, 
        runtime_res, 
        {"repo_id": request.repo_id, "pr_id": request.pr_id}
    )
    
    print(f"Analysis complete. Final Verdict:\n{final_comment}")
    return {"status": "success", "comment": final_comment}


# -----------------------------------------------------------------------------
# API Routes
# -----------------------------------------------------------------------------

@app.post("/analyze")
async def analyze_pr(request: AnalysisRequest):
    try:
        result = await orchestration_agent(request)
        return result
    except Exception as e:
        print(f"Error processing analysis: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "python-agent-engine"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
