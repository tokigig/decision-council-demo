from src.councils.types import CouncilMember

COUNCIL_PRESETS: dict[str, list[CouncilMember]] = {
    "ai_adoption": [
        CouncilMember(
            id="technical_readiness",
            name="Technical Readiness Advisor",
            role="Systems and implementation reviewer",
            mandate="Assess feasibility, dependencies, integration risk, and operational readiness. Push for staged rollout instead of vague transformation claims.",
        ),
        CouncilMember(
            id="risk",
            name="Risk Advisor",
            role="Legal, compliance, and downside reviewer",
            mandate="Identify material downside, user harm, liability, abuse risk, and control requirements before approval.",
        ),
        CouncilMember(
            id="revenue",
            name="Revenue Advisor",
            role="Commercial upside reviewer",
            mandate="Assess revenue impact, adoption friction, conversion benefit, margin impact, and pilot economics.",
        ),
        CouncilMember(
            id="customer_trust",
            name="Customer Trust Advisor",
            role="Customer experience and brand trust reviewer",
            mandate="Protect customer confidence. Identify transparency, consent, failure recovery, and support concerns.",
        ),
    ],
    "risk_review": [
        CouncilMember(id="legal_risk", name="Legal/Risk Advisor", role="Risk reviewer", mandate="Surface legal, policy, contractual, and reputational risks."),
        CouncilMember(id="security", name="Security Advisor", role="Security reviewer", mandate="Assess data exposure, abuse paths, secrets, permissions, and monitoring."),
        CouncilMember(id="customer_trust", name="Customer Trust Advisor", role="Trust reviewer", mandate="Assess user trust, transparency, consent, and recovery paths."),
        CouncilMember(id="operations", name="Operations Advisor", role="Operator", mandate="Assess staffing, runbooks, dependencies, and launch readiness."),
    ],
    "launch_review": [
        CouncilMember(id="product", name="Product Strategist", role="Product reviewer", mandate="Assess product clarity, customer need, scope, and launch sequencing."),
        CouncilMember(id="market_skeptic", name="Market Skeptic", role="Skeptic", mandate="Challenge assumptions about demand, timing, positioning, and differentiation."),
        CouncilMember(id="revenue", name="Revenue Advisor", role="Commercial reviewer", mandate="Assess revenue model, pricing, conversion, and sales motion."),
        CouncilMember(id="operator", name="Operator", role="Execution reviewer", mandate="Assess implementation risk, support burden, and immediate next actions."),
    ],
}

def get_preset(preset_id: str) -> list[CouncilMember]:
    return COUNCIL_PRESETS.get(preset_id, COUNCIL_PRESETS["ai_adoption"])
