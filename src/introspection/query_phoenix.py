import os


def get_self_improvement_note(recent_eval_targets: list[str] | None = None) -> str:
    """Return a self-improvement note for the next council run.

    In the full hackathon demo, this should call Phoenix MCP to inspect recent traces,
    sessions, evals, prompts, and annotations. This reference implementation keeps a
    deterministic fallback so judges can run the app without secrets.
    """
    if os.getenv("ENABLE_PHOENIX_MCP", "false").lower() != "true":
        if recent_eval_targets:
            return "Prior evals found weak spots: " + "; ".join(recent_eval_targets) + ". For this run, make the verdict more measurable and action-oriented."
        return "No prior Phoenix MCP insight available in fallback mode. For this run, require measurable safeguards, explicit dissent, and concrete next actions."

    # Placeholder integration point:
    # Use Gemini CLI or an MCP client configured with .gemini/settings.json to query Phoenix:
    # - recent traces for PHOENIX_PROJECT_NAME
    # - failed evals / low-confidence runs
    # - recurring weak prompt patterns
    # Then summarize one improvement instruction for the next run.
    return "Phoenix MCP introspection is enabled. Query recent low-scoring traces and instruct the synthesizer to improve the most common failure pattern."
