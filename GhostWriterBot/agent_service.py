"""
Agent Service Layer - Orchestrates Multi-Agent PR Review
Coordinates Security Auditor, Runtime Validator, and Ghostwriter agents (all Groq-powered).
"""

import json
import asyncio
from pathlib import Path
from typing import Dict
from datetime import datetime

# Import all three Groq-powered agents
from Security_Auditor import audit_pr_diff as run_security_audit
from Runtime_Validator import validate_runtime as run_runtime_validation
from GhostWriter import synthesize_pr_review as run_ghostwriter


class AgentOrchestrator:
    """Orchestrates the execution of all three agents for PR review."""

    def __init__(self):
        """Initialize the agent orchestrator."""
        self.app_name = "devops_ghostwriter"

    async def initialize(self):
        """Initialize orchestrator."""
        print("✅ Agent orchestrator initialized (3 Groq-powered agents)")

    async def run_security_auditor(self, pr_diff: str, pr_number: int) -> Dict:
        """
        Run Security Auditor agent on PR diff.

        Args:
            pr_diff: Unified diff content
            pr_number: PR number for logging

        Returns:
            Security audit report as dictionary
        """
        print("\n" + "=" * 70)
        print("🔒 STEP 2: Running Security Auditor Agent (Groq)")
        print("=" * 70)

        # Run security audit (uses Groq API with caching)
        result_str = run_security_audit(code_content=pr_diff)

        # Try to parse JSON response
        try:
            result = json.loads(result_str)
            print(
                f"✅ Security audit complete: {result.get('total_issues', 0)} issues found"
            )
            return result
        except json.JSONDecodeError:
            # If not JSON, return as text report
            print("⚠️ Security audit returned non-JSON response")
            return {
                "agent": "Security Auditor",
                "status": "completed",
                "total_issues": 0,
                "report": result_str,
            }

    async def run_runtime_validator(self, pr_diff: str, pr_number: int) -> Dict:
        """
        Run Runtime Validator agent on PR code.

        Args:
            pr_diff: Unified diff content (we'll extract code from it)
            pr_number: PR number for logging

        Returns:
            Runtime validation report as dictionary
        """
        print("\n" + "=" * 70)
        print("🔍 STEP 3: Running Runtime Validator Agent (Groq)")
        print("=" * 70)

        # Extract code from diff (lines starting with +)
        code_lines = []
        for line in pr_diff.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                code_lines.append(line[1:])  # Remove the + prefix

        code_content = "\n".join(code_lines)

        # Run runtime validation (uses Groq API with caching)
        result = run_runtime_validation(code_content)

        print(
            f"✅ Runtime validation complete: {result.get('total_issues', 0)} issues found"
        )
        return result

    async def run_ghostwriter(
        self,
        security_report: Dict,
        runtime_report: Dict,
        pr_metadata: Dict,
        pr_number: int,
    ) -> str:
        """
        Run Ghostwriter agent to synthesize all reports.

        Args:
            security_report: Security audit results
            runtime_report: Runtime validation results
            pr_metadata: PR metadata (files changed, additions, deletions)
            pr_number: PR number for logging

        Returns:
            Formatted markdown PR comment
        """
        print("\n" + "=" * 70)
        print("✍️ STEP 4: Running Ghostwriter Agent (Groq)")
        print("=" * 70)

        # Synthesize PR review using Groq
        pr_comment = run_ghostwriter(
            security_report=security_report,
            runtime_report=runtime_report,
            pr_metadata=pr_metadata,
        )

        print("✅ Ghostwriter synthesis complete")
        return pr_comment

    async def orchestrate_pr_review(
        self, pr_diff: str, pr_metadata: Dict, pr_number: int
    ) -> str:
        """
        Main orchestration method - runs all three agents in sequence.

        Args:
            pr_diff: Unified PR diff
            pr_metadata: PR metadata
            pr_number: PR number

        Returns:
            Final markdown comment from Ghostwriter
        """
        print("\n" + "=" * 70)
        print("🚀 STARTING MULTI-AGENT PR REVIEW ORCHESTRATION (Groq-Powered)")
        print("=" * 70)
        print(f"PR Number: {pr_number}")
        print(f"Files Changed: {pr_metadata.get('files_changed', 0)}")
        print(
            f"Lines: +{pr_metadata.get('additions', 0)}/-{pr_metadata.get('deletions', 0)}"
        )

        try:
            # Step 1: Security Audit
            security_report = await self.run_security_auditor(pr_diff, pr_number)

            # Step 2: Runtime Validation
            runtime_report = await self.run_runtime_validator(pr_diff, pr_number)

            # Step 3: Ghostwriter Synthesis
            final_comment = await self.run_ghostwriter(
                security_report=security_report,
                runtime_report=runtime_report,
                pr_metadata=pr_metadata,
                pr_number=pr_number,
            )

            print("\n" + "=" * 70)
            print("✅ MULTI-AGENT PR REVIEW COMPLETE")
            print("=" * 70)

            return final_comment

        except Exception as e:
            print(f"\n❌ Error during PR review: {e}")
            import traceback

            traceback.print_exc()

            # Return fallback error comment
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"""## 🔍 Automated PR Review Summary

⚠️ **Review Status:** Error occurred during analysis

---

### ❌ Error Report

An error occurred while running the automated PR review:

```
{str(e)}
```

Please check the server logs for more details.

---

*🤖 Automated review generated at {timestamp}*  
*Powered by DevOps-GhostWriter (Groq AI)*
"""


async def create_orchestrator() -> AgentOrchestrator:
    """
    Factory function to create and initialize an orchestrator.

    Returns:
        Initialized AgentOrchestrator instance
    """
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    return orchestrator
