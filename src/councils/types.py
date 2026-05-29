from typing import Literal
from pydantic import BaseModel, Field

CouncilPresetId = Literal["ai_adoption", "risk_review", "launch_review", "custom"]
Stance = Literal["support", "oppose", "conditional"]

class CouncilMember(BaseModel):
    id: str
    name: str
    role: str
    mandate: str

class CouncilContext(BaseModel):
    business_name: str | None = None
    decision_question: str
    background: str | None = None
    constraints: list[str] = Field(default_factory=list)
    known_facts: list[str] = Field(default_factory=list)

class MemberOpinion(BaseModel):
    member_id: str
    member_name: str
    stance: Stance
    confidence: int = Field(ge=0, le=100)
    reasoning: str
    risks: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    evidence_needed: list[str] = Field(default_factory=list)

class CouncilVerdict(BaseModel):
    recommendation: str
    confidence: int = Field(ge=0, le=100)
    summary: str
    dissent: list[str] = Field(default_factory=list)
    safeguards: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    trace_id: str | None = None

class VerdictEval(BaseModel):
    score: int = Field(ge=0, le=100)
    passed: bool
    findings: list[str] = Field(default_factory=list)
    improvement_targets: list[str] = Field(default_factory=list)

class CouncilRunResult(BaseModel):
    run_id: str
    preset_id: CouncilPresetId
    context: CouncilContext
    independent_opinions: list[MemberOpinion]
    challenge_opinions: list[MemberOpinion]
    verdict: CouncilVerdict
    eval: VerdictEval
    self_improvement_note: str
