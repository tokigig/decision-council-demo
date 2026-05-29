from src.councils.types import CouncilContext

MADGESFOOD_AI_CHECKOUT = CouncilContext(
    business_name="MadgesFood",
    decision_question="Should MadgesFood enable AI-agent checkout?",
    background="MadgesFood is a food retail concept exploring whether AI shopping agents should be allowed to discover products, assemble carts, and complete checkout on behalf of customers.",
    constraints=[
        "Must not erode customer trust",
        "Must avoid accidental purchases and refund spikes",
        "Must be demoable within hackathon scope",
    ],
    known_facts=[
        "The business wants a guarded pilot rather than a full rollout",
        "Agentic commerce is strategically important but operationally immature",
        "Checkout flows must preserve consent, auditability, and human recovery paths",
    ],
)
