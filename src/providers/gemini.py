import json
import os
import re
from typing import Any

from src.councils.types import CouncilMember, CouncilContext, MemberOpinion, CouncilVerdict


def _json_from_text(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)

def _clean_markdown(value):
    if isinstance(value, str):
        value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
        value = re.sub(r"^\s*[-*]\s+", "", value)
        return value.strip()
    if isinstance(value, list):
        return [_clean_markdown(item) for item in value]
    if isinstance(value, dict):
        return {key: _clean_markdown(item) for key, item in value.items()}
    return value

def _client():
    try:
        from google import genai

        use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"

        if use_vertex:
            project = os.getenv("GOOGLE_CLOUD_PROJECT")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

            if not project:
                print("GOOGLE_GENAI_USE_VERTEXAI=true but GOOGLE_CLOUD_PROJECT is missing; using fallback mode.")
                return None

            return genai.Client(
                vertexai=True,
                project=project,
                location=location,
            )

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None

        return genai.Client(api_key=api_key)
    except Exception as exc:
        print(f"Gemini client unavailable, using fallback mode: {exc}")
        return None


def _generate_json(prompt: str) -> dict[str, Any] | None:
    client = _client()
    if client is None:
        return None
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    response = client.models.generate_content(model=model, contents=prompt)
    return _clean_markdown(_json_from_text(response.text or "{}"))


def _fallback_opinion(member: CouncilMember, context: CouncilContext, round_name: str) -> MemberOpinion:
    conditional = member.id in {"risk", "customer_trust", "legal_risk", "security"}
    stance = "conditional" if conditional else "support"
    confidence = 72 if stance == "conditional" else 78
    return MemberOpinion(
        member_id=member.id,
        member_name=member.name,
        stance=stance,
        confidence=confidence,
        reasoning=(
            f"{member.name} recommends a guarded pilot for '{context.decision_question}'. "
            f"The decision has upside, but should be constrained by measurable safeguards, explicit customer consent, and rollback criteria."
        ),
        risks=[
            "Overconfident automation could create customer trust issues.",
            "Operational support may be unprepared for agent-caused checkout mistakes.",
        ],
        recommended_actions=[
            "Run a limited pilot with clear opt-in consent.",
            "Track failed checkout, refund, support, and customer satisfaction metrics.",
            "Define human recovery and rollback paths before expansion.",
        ],
        evidence_needed=[
            "Baseline conversion and support ticket metrics.",
            "Checkout failure rate during a small controlled pilot.",
        ],
    )


def run_member_opinion(member: CouncilMember, context: CouncilContext, round_name: str, peer_summary: str | None = None) -> MemberOpinion:
    prompt = f"""
You are {member.name}, role: {member.role}.
Mandate: {member.mandate}

Decision context:
Business: {context.business_name or "Unknown"}
Question: {context.decision_question}
Background: {context.background or ""}
Constraints: {context.constraints}
Known facts: {context.known_facts}

Round: {round_name}
Peer summary, if any: {peer_summary or "No peer summary for this round."}
Return plain text JSON string values only. Do not use Markdown. Do not use asterisks, double asterisks, headings, bullet characters, numbered lists, colons used as headings, or decorative formatting inside JSON string values.

Return strict JSON only with this shape:
{{
  "member_id": "{member.id}",
  "member_name": "{member.name}",
  "stance": "support|oppose|conditional",
  "confidence": 0-100,
  "reasoning": "brief but concrete reasoning",
  "risks": ["..."],
  "recommended_actions": ["..."],
  "evidence_needed": ["..."]
}}
"""
    data = _generate_json(prompt)
    if data is None:
        return _fallback_opinion(member, context, round_name)
    return MemberOpinion(**data)


def synthesize_verdict(context: CouncilContext, opinions: list[MemberOpinion], improvement_note: str) -> CouncilVerdict:
    opinion_blob = "\n".join(
        f"- {o.member_name}: {o.stance}, confidence {o.confidence}. {o.reasoning}" for o in opinions
    )
    prompt = f"""
You are the Decision Council synthesizer.

Decision: {context.decision_question}
Business: {context.business_name or "Unknown"}
Self-improvement instruction from prior observability/evals: {improvement_note}

Council opinions:
{opinion_blob}
Do not use Markdown formatting. Do not use **bold**, headings, or bullet symbols inside JSON strings. Return plain text only.

Return strict JSON only with this shape:
{{
  "recommendation": "direct recommendation",
  "confidence": 0-100,
  "summary": "short synthesis",
  "dissent": ["material dissent or concern"],
  "safeguards": ["measurable safeguard with owner/threshold where possible"],
  "next_actions": ["concrete next action"]
}}
"""
    data = _generate_json(prompt)
    if data is None:
        return CouncilVerdict(
            recommendation="Proceed with a guarded pilot, not a full rollout.",
            confidence=76,
            summary=(
                "The council sees strategic value in AI-agent checkout, but only if MadgesFood treats it as a measured pilot with consent, auditability, support readiness, and rollback controls."
            ),
            dissent=[
                "Risk and customer trust advisors oppose a broad rollout until refund, consent, and support controls are proven.",
                "Technical readiness depends on clear failure handling and observability before customer-wide deployment.",
            ],
            safeguards=[
                "Limit the pilot to opted-in users and cap transaction value during the first test window.",
                "Require explicit human confirmation before purchase completion.",
                "Monitor refund rate, checkout failure rate, support tickets, and customer satisfaction weekly.",
                "Define rollback criteria before launch, including failure thresholds and owner accountability.",
            ],
            next_actions=[
                "Design a two-week opt-in pilot with success and stop-loss metrics.",
                "Create support runbooks for agent checkout errors and customer disputes.",
                "Instrument the pilot so every automated decision is traceable and reviewable.",
            ],
        )
    return CouncilVerdict(**data)
