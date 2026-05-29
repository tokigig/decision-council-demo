from uuid import uuid4

from src.councils.presets import get_preset
from src.councils.types import CouncilContext, CouncilRunResult
from src.providers.gemini import run_member_opinion, synthesize_verdict
from src.providers.phoenix_tracing import council_span
from src.evals.evaluate_verdict import evaluate_verdict
from src.introspection.query_phoenix import get_self_improvement_note


def _summarize_opinions(opinions) -> str:
    return "\n".join(
        f"{o.member_name}: stance={o.stance}, confidence={o.confidence}, risks={'; '.join(o.risks[:2])}"
        for o in opinions
    )


def run_council(preset_id: str, context: CouncilContext) -> CouncilRunResult:
    run_id = str(uuid4())
    members = get_preset(preset_id)
    improvement_note = get_self_improvement_note()

    with council_span("council.run", {"run_id": run_id, "councilPresetId": preset_id, "business": context.business_name}):
        independent = []
        for member in members:
            with council_span("council.member.independent", {"run_id": run_id, "memberId": member.id, "round": "independent"}):
                opinion = run_member_opinion(member, context, "independent")
                independent.append(opinion)

        peer_summary = _summarize_opinions(independent)
        challenge = []
        for member in members:
            with council_span("council.member.challenge", {"run_id": run_id, "memberId": member.id, "round": "challenge"}):
                opinion = run_member_opinion(member, context, "challenge", peer_summary=peer_summary)
                challenge.append(opinion)

        with council_span("council.synthesis", {"run_id": run_id, "round": "synthesis"}):
            verdict = synthesize_verdict(context, challenge, improvement_note)
            verdict.trace_id = run_id

        with council_span("council.eval", {"run_id": run_id, "round": "eval"}):
            verdict_eval = evaluate_verdict(verdict)

        final_note = get_self_improvement_note(verdict_eval.improvement_targets)

    return CouncilRunResult(
        run_id=run_id,
        preset_id=preset_id,  # type: ignore[arg-type]
        context=context,
        independent_opinions=independent,
        challenge_opinions=challenge,
        verdict=verdict,
        eval=verdict_eval,
        self_improvement_note=final_note,
    )
