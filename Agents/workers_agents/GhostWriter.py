from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import os
from pathlib import Path
from datetime import datetime
from typing import Annotated

"""
Ghostwriter Agent (The Synthesizer) for PR Reviews
Gathers findings from multiple sources and writes professional GitHub comments
with proper markdown formatting, summaries, and recommendations.
"""


# Tool: Format PR comment header
def format_pr_comment_header(
    logic_status: Annotated[str, "Pass/Fail status of logic check"],
    security_issues_count: Annotated[int, "Number of security issues found"],
    readme_updated: Annotated[bool, "Whether README was updated"]
) -> str:
    """
    Creates a professional PR comment header with emoji indicators.
    """
    # Format logic status
    logic_emoji = "✅" if logic_status.lower() == "pass" else "❌"
    logic_text = f"{logic_emoji} Logic {logic_status}"
    
    # Format security status
    if security_issues_count == 0:
        security_text = "✅ No Security Risks"
    elif security_issues_count == 1:
        security_text = "⚠️ 1 Security Risk Found"
    else:
        security_text = f"⚠️ {security_issues_count} Security Risks Found"
    
    # Format README status
    readme_text = "📝 README Updated" if readme_updated else "📄 No README Changes"
    
    header = f"""## 🔍 Pull Request Review Summary

{logic_text} | {security_text} | {readme_text}

---
"""
    return header


# Tool: Format security findings section
def format_security_findings(
    security_report: Annotated[str, "Raw security audit report"]
) -> str:
    """
    Formats security findings into a clean, readable markdown section.
    """
    if "✅" in security_report and "PASSED" in security_report.upper():
        return """### 🔒 Security Analysis
**Status:** ✅ All security checks passed

No security vulnerabilities detected in this PR.
"""
    
    section = """### 🔒 Security Analysis
**Status:** ⚠️ Issues Require Attention

"""
    
    # Extract key findings from the report
    if "HARDCODED SECRETS" in security_report:
        section += "#### 🔐 Hardcoded Secrets\n"
        section += "Potential credentials or API keys detected in code. Please use environment variables or secret management.\n\n"
    
    if "SQL INJECTION" in security_report:
        section += "#### 💉 SQL Injection Risks\n"
        section += "Unsafe SQL query construction detected. Use parameterized queries or ORM methods.\n\n"
    
    if "VULNERABLE DEPENDENCIES" in security_report:
        section += "#### 📦 Vulnerable Dependencies\n"
        section += "Outdated packages with known vulnerabilities found. Update to latest secure versions.\n\n"
    
    if "SECURITY ANTI-PATTERNS" in security_report:
        section += "#### 🛡️ Security Anti-Patterns\n"
        section += "Unsafe coding practices detected. Review and apply security best practices.\n\n"
    
    return section


# Tool: Format logic check section
def format_logic_check(
    logic_status: Annotated[str, "Pass/Fail status"],
    logic_details: Annotated[str, "Details about logic check"]
) -> str:
    """
    Formats the logic check results into markdown.
    """
    emoji = "✅" if logic_status.lower() == "pass" else "❌"
    
    section = f"""### 🧮 Logic & Functionality
**Status:** {emoji} {logic_status}

{logic_details}
"""
    return section


# Tool: Format README changes section
def format_readme_section(
    readme_updated: Annotated[bool, "Whether README was updated"],
    readme_changes: Annotated[str, "Description of README changes if any"]
) -> str:
    """
    Formats the README update section.
    """
    if readme_updated:
        return f"""### 📝 Documentation Updates
**Status:** ✅ README Updated

{readme_changes}
"""
    else:
        return """### 📝 Documentation Updates
**Status:** ℹ️ No documentation changes in this PR

Consider updating the README if new features or significant changes were introduced.
"""


# Tool: Generate recommendations
def generate_recommendations(
    has_security_issues: Annotated[bool, "Whether security issues exist"],
    has_logic_issues: Annotated[bool, "Whether logic issues exist"],
    needs_readme: Annotated[bool, "Whether README should be updated"]
) -> str:
    """
    Generates actionable recommendations based on findings.
    """
    recommendations = []
    
    if has_security_issues:
        recommendations.append("🔒 **Security:** Address all security vulnerabilities before merging")
    
    if has_logic_issues:
        recommendations.append("🧮 **Logic:** Fix identified logic errors and add test coverage")
    
    if needs_readme:
        recommendations.append("📝 **Documentation:** Update README to reflect new changes")
    
    if not recommendations:
        recommendations.append("✅ **Ready to Merge:** All checks passed successfully!")
    
    section = """### 💡 Recommendations

"""
    section += "\n".join(f"- {rec}" for rec in recommendations)
    section += "\n"
    
    return section


# Tool: Create final PR comment
def create_pr_comment(
    header: Annotated[str, "Formatted header section"],
    security_section: Annotated[str, "Formatted security section"],
    logic_section: Annotated[str, "Formatted logic section"],
    readme_section: Annotated[str, "Formatted README section"],
    recommendations: Annotated[str, "Formatted recommendations"]
) -> str:
    """
    Combines all sections into a complete, professional GitHub PR comment.
    """
    footer = f"""
---

*🤖 Automated review generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Powered by ADK Multi-Agent PR Review System*
"""
    
    full_comment = (
        header +
        security_section +
        logic_section +
        readme_section +
        recommendations +
        footer
    )
    
    return full_comment


# Tool: Generate summary statistics
def generate_summary_statistics(
    total_files_changed: Annotated[int, "Number of files changed"],
    lines_added: Annotated[int, "Lines of code added"],
    lines_removed: Annotated[int, "Lines of code removed"],
    security_issues: Annotated[int, "Number of security issues"],
    logic_issues: Annotated[int, "Number of logic issues"]
) -> str:
    """
    Creates a summary statistics section for the PR.
    """
    section = f"""### 📊 Change Statistics

| Metric | Value |
|--------|-------|
| Files Changed | {total_files_changed} |
| Lines Added | +{lines_added} |
| Lines Removed | -{lines_removed} |
| Net Change | {lines_added - lines_removed:+d} |
| Security Issues | {security_issues} |
| Logic Issues | {logic_issues} |

"""
    return section


# Create the Ghostwriter Agent
ghostwriter_agent = Agent(
    model="gemini-2.5-flash",
    name="ghostwriter",
    description=(
        "The Synthesizer - Gathers findings from security audits and logic checks, "
        "then writes professional, well-formatted GitHub PR comments with clear "
        "summaries, statistics, and actionable recommendations."
    ),
    instruction="""
    You are the Ghostwriter, a professional technical writer specializing in PR reviews.
    
    Your responsibilities:
    1. Synthesize findings from security audits and logic checks
    2. Create professional, well-formatted GitHub comments with proper markdown
    3. Generate clear summaries with emoji indicators (✅ ⚠️ ❌ 📝)
    4. Provide actionable recommendations
    5. Format complex technical information in an accessible way
    
    Process:
    - Use format_pr_comment_header to create the summary line
    - Use format_security_findings to present security issues
    - Use format_logic_check to present logic analysis
    - Use format_readme_section to document README changes
    - Use generate_summary_statistics for PR stats (if available)
    - Use generate_recommendations for actionable next steps
    - Use create_pr_comment to combine everything into a polished final comment
    
    Writing Guidelines:
    - Be clear, concise, and professional
    - Use emojis sparingly but effectively for visual scanning
    - Format with proper markdown (headers, lists, tables, code blocks)
    - Balance technical accuracy with readability
    - Always provide constructive, actionable feedback
    - End on a positive or encouraging note when appropriate
    """,
    tools=[
        format_pr_comment_header,
        format_security_findings,
        format_logic_check,
        format_readme_section,
        generate_recommendations,
        generate_summary_statistics,
        create_pr_comment,
    ],
)


def synthesize_pr_review(
    security_report: str,
    logic_status: str,
    logic_details: str,
    readme_updated: bool,
    readme_changes: str,
    session_service: InMemorySessionService,
    app_name: str,
    user_id: str,
    session_id: str,
    stats: dict = None
) -> str:
    """
    Main function to synthesize PR review and generate comment.
    
    Args:
        security_report: Raw security audit report
        logic_status: Pass/Fail status of logic check
        logic_details: Details about logic analysis
        readme_updated: Whether README was updated
        readme_changes: Description of README changes
        session_service: ADK session service
        app_name: Application name
        user_id: User ID
        session_id: Session ID
        stats: Optional dictionary with PR statistics
        
    Returns:
        Formatted GitHub PR comment
    """
    runner = Runner(
        agent=ghostwriter_agent,
        app_name=app_name,
        session_service=session_service
    )
    
    # Prepare the synthesis request
    stats_text = ""
    if stats:
        stats_text = f"""
        
PR Statistics:
- Files changed: {stats.get('files_changed', 0)}
- Lines added: {stats.get('lines_added', 0)}
- Lines removed: {stats.get('lines_removed', 0)}
"""
    
    query = f"""
    Please synthesize the following PR review findings into a professional GitHub comment:
    
    SECURITY AUDIT REPORT:
    {security_report}
    
    LOGIC CHECK:
    Status: {logic_status}
    Details: {logic_details}
    
    README STATUS:
    Updated: {readme_updated}
    Changes: {readme_changes}
    {stats_text}
    
    Create a complete, well-formatted PR comment with:
    1. Summary header with status indicators
    2. Security findings section
    3. Logic check section
    4. README updates section
    5. Statistics (if provided)
    6. Actionable recommendations
    
    Use proper markdown formatting and make it professional and easy to scan.
    """
    
    user_content = types.Content(
        role='user',
        parts=[types.Part(text=query)]
    )
    
    responses = []
    print("\n✍️ Ghostwriter is synthesizing review...\n")
    
    for event in runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=user_content
    ):
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts') and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        responses.append(part.text)
        
        if hasattr(event, 'text') and event.text:
            responses.append(event.text)
    
    return "\n\n".join(responses) if responses else "No response generated."


def write_pr_comment(comment: str, filename: str = "pr_comment.md") -> None:
    """
    Writes the PR comment to a markdown file.
    """
    file_path = Path(__file__).parent / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(comment)
    
    print(f"✅ PR comment written to: {file_path}")


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("✍️ Starting Ghostwriter Agent Test...")
        print("=" * 70)
        
        # ADK Configuration
        APP_NAME = "ghostwriter_app"
        USER_ID = "ghostwriter_user"
        SESSION_ID = "ghostwriter_session_001"
        
        try:
            # Initialize session service
            session_service = InMemorySessionService()
            
            session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID
            )
            print(f"✅ Session created: {SESSION_ID}\n")
            
            # Sample data (simulating results from other agents)
            security_report = """
🔍 SECURITY AUDIT SUMMARY
=========================
Found 1 security concern(s):

⚠️ Line 12: Potential API Key detected
   Code: api_key = "sk_live_1234567890abcdef"...

⚡ ACTION REQUIRED: Please address these security issues before merging.
"""
            
            logic_status = "Pass"
            logic_details = """
The code logic has been reviewed and all functionality works as expected:
- Functions have proper input validation
- Error handling is comprehensive
- Edge cases are covered
- Return types are consistent
"""
            
            readme_updated = True
            readme_changes = """
Added new section documenting the API authentication flow and updated 
installation instructions to include the new dependency requirements.
"""
            
            pr_stats = {
                'files_changed': 3,
                'lines_added': 145,
                'lines_removed': 23
            }
            
            # Generate the PR comment
            print("📝 Synthesizing PR review comment...")
            pr_comment = synthesize_pr_review(
                security_report=security_report,
                logic_status=logic_status,
                logic_details=logic_details,
                readme_updated=readme_updated,
                readme_changes=readme_changes,
                session_service=session_service,
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID,
                stats=pr_stats
            )
            
            # Display result
            print()
            print("=" * 70)
            print(pr_comment)
            print("=" * 70)
            
            # Write to file
            print()
            write_pr_comment(pr_comment)
            
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(main())