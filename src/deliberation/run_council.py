from uuid import uuid4

from src.councils.presets import get_preset
from src.councils.types import CouncilContext, CouncilMember, CouncilRunResult
from src.evals.evaluate_verdict import evaluate_verdict
from src.introspection.query_phoenix import get_self_improvement_note
from src.providers.gemini import (
    generate_improvement_directives,
    run_member_opinion,
    synthesize_verdict,
)
from src.providers.phoenix_tracing import council_span


def _summarize_opinions(opinions) -> str:
    return "\n".join(
        f"{o.member_name}: stance={o.stance}, confidence={o.confidence}, risks={'; '.join(o.risks[:2])}"
        for o in opinions
    )


def run_council(
    preset_id: str,
    context: CouncilContext,
    extra_members: list[CouncilMember] | None = None,
) -> CouncilRunResult:
    run_id = str(uuid4())
    members = get_preset(preset_id)

    if extra_members:
        members = members + extra_members

    raw_improvement_note = get_self_improvement_note()
    improvement_directives = generate_improvement_directives(context, raw_improvement_note)

    with council_span(
        "council.run",
        {
            "run_id": run_id,
            "councilPresetId": preset_id,
            "business": context.business_name,
            "improvementDirectiveCount": len(improvement_directives),
            "memberCount": len(members),
        },
    ):
        independent = []

        for member in members:
            with council_span(
                "council.member.independent",
                {
                    "run_id": run_id,
                    "councilPresetId": preset_id,
                    "memberId": member.id,
                    "memberName": member.name,
                    "memberRole": member.role,
                    "round": "independent",
                },
            ) as span:
                opinion = run_member_opinion(
                    member,
                    context,
                    "independent",
                    improvement_directives=improvement_directives,
                )
                span.set_attribute("stance", opinion.stance)
                span.set_attribute("confidence", opinion.confidence)
                span.set_attribute("riskCount", len(opinion.risks))
                span.set_attribute("actionCount", len(opinion.recommended_actions))
                independent.append(opinion)

        peer_summary = _summarize_opinions(independent)
        challenge = []

        for member in members:
            with council_span(
                "council.member.challenge",
                {
                    "run_id": run_id,
                    "councilPresetId": preset_id,
                    "memberId": member.id,
                    "memberName": member.name,
                    "memberRole": member.role,
                    "round": "challenge",
                },
            ) as span:
                opinion = run_member_opinion(
                    member,
                    context,
                    "challenge",
                    peer_summary=peer_summary,
                    improvement_directives=improvement_directives,
                )
                span.set_attribute("stance", opinion.stance)
                span.set_attribute("confidence", opinion.confidence)
                span.set_attribute("riskCount", len(opinion.risks))
                span.set_attribute("actionCount", len(opinion.recommended_actions))
                challenge.append(opinion)

        with council_span(
            "council.synthesis",
            {
                "run_id": run_id,
                "councilPresetId": preset_id,
                "round": "synthesis",
            },
        ) as span:
            verdict = synthesize_verdict(
                context,
                challenge,
                raw_improvement_note,
                improvement_directives=improvement_directives,
            )
            verdict.trace_id = run_id
            span.set_attribute("recommendation", verdict.recommendation)
            span.set_attribute("confidence", verdict.confidence)
            span.set_attribute("dissentCount", len(verdict.dissent))
            span.set_attribute("safeguardCount", len(verdict.safeguards))
            span.set_attribute("nextActionCount", len(verdict.next_actions))

        with council_span(
            "council.eval",
            {
                "run_id": run_id,
                "councilPresetId": preset_id,
                "round": "eval",
            },
        ) as span:
            verdict_eval = evaluate_verdict(verdict)
            span.set_attribute("evalScore", verdict_eval.score)
            span.set_attribute("evalPassed", verdict_eval.passed)
            span.set_attribute("improvementTargetCount", len(verdict_eval.improvement_targets))

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
            applied_improvement_directives=improvement_directives,
        )