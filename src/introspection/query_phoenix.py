import os

from src.councils.types import CouncilContext


def get_self_improvement_note(recent_eval_targets: list[str] | None = None) -> str:
    """Return raw observability/eval insight.

    In the full hackathon demo, this should call Phoenix MCP to inspect recent traces,
    sessions, evals, prompts, and annotations. This reference implementation keeps a
    deterministic fallback so judges can run the app without MCP credentials.
    """
    if os.getenv("ENABLE_PHOENIX_MCP", "false").lower() != "true":
        if recent_eval_targets:
            return "Recent evals found weak spots: " + "; ".join(recent_eval_targets)
        return (
            "No prior Phoenix MCP insight is available yet. Watch this run for vague advice, "
            "unsupported confidence, missing dissent, weak safeguards, and next actions that "
            "are not specific to the business."
        )

    # Placeholder integration point:
    # Use Gemini CLI or an MCP client configured with .gemini/settings.json to query Phoenix:
    # - recent traces for PHOENIX_PROJECT_NAME
    # - failed evals / low-confidence runs
    # - recurring weak prompt patterns
    # Then return raw findings for directive generation.
    return (
        "Phoenix MCP introspection is enabled. Query recent low-scoring traces and summarize "
        "the most common failure patterns for this council preset."
    )


def fallback_improvement_directives(context: CouncilContext, raw_insight: str) -> list[str]:
    business = context.business_name or "this business"
    return [
        f"Make the advice specific to {business}, not generic AI adoption advice.",
        "Convert abstract risks into plain operating limits the owner can understand.",
        "Make next actions concrete enough that the business can start this week.",
        "State what AI should not be allowed to do without human approval.",
        f"Use the raw observability insight as a quality warning: {raw_insight}",
    ]