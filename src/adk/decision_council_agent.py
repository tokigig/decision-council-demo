"""
Google ADK entrypoint for Decision Council.

This file exposes the existing Decision Council engine as a callable ADK agent tool.
It does not replace the FastAPI/GKE public demo. It provides an Agent Builder / ADK
entrypoint into the same Gemini-powered, Phoenix-traced council runtime.

Optional experts are additional Gemini-powered council roles, not external LLMs.
"""

from typing import Any

from dotenv import load_dotenv

from src.councils.types import CouncilContext, CouncilMember
from src.deliberation.run_council import run_council
from src.providers.phoenix_tracing import setup_tracing

load_dotenv()
setup_tracing()


def _slug(value: str) -> str:
    return (
        value.lower()
        .replace("&", "and")
        .replace("/", " ")
        .replace("-", " ")
        .replace("_", " ")
        .strip()
        .replace(" ", "_")
    )


def run_decision_council_tool(
    council_id: str,
    business_name: str,
    decision_question: str,
    background: str,
    expert_name: str = "",
    expert_role: str = "",
    expert_mandate: str = "",
) -> dict[str, Any]:
    """Run a traced Decision Council deliberation.

    Args:
        council_id: Council preset id. Use ai_adoption, risk_review, or launch_review.
        business_name: Name of the business or organization being evaluated.
        decision_question: The decision the council should evaluate.
        background: Relevant context, constraints, facts, and business situation.
        expert_name: Optional subject-matter expert name to add to the council.
        expert_role: Optional subject-matter expert role.
        expert_mandate: Optional mandate describing what the expert should evaluate.

    Returns:
        A structured Decision Council result including verdict, opinions, eval, trace id,
        and applied improvement directives.
    """

    context = CouncilContext(
        business_name=business_name or None,
        decision_question=decision_question,
        background=background or None,
    )

    extra_members: list[CouncilMember] = []

    if expert_name and expert_mandate:
        extra_members.append(
            CouncilMember(
                id=f"custom_{_slug(expert_name)}",
                name=expert_name,
                role=expert_role or "Subject-matter expert",
                mandate=expert_mandate,
            )
        )

    result = run_council(
        council_id or "ai_adoption",
        context,
        extra_members=extra_members or None,
    )

    return result.model_dump()


try:
    from google.adk.agents import Agent

    root_agent = Agent(
        name="decision_council_agent",
        model="gemini-2.5-flash",
        instruction=(
            "You are the Decision Council ADK entrypoint. "
            "Use run_decision_council_tool to evaluate high-stakes business decisions. "
            "When the user asks for domain expertise, add one Gemini-powered subject-matter "
            "expert by filling expert_name, expert_role, and expert_mandate. "
            "Do not use external LLMs. The council engine handles deliberation, tracing, "
            "evaluation, and improvement directives."
        ),
        tools=[run_decision_council_tool],
    )
except Exception:
    # Allows the tool function to be imported and smoke-tested even if google-adk
    # is not installed in a minimal local environment.
    root_agent = None