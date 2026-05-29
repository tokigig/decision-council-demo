from src.councils.types import CouncilVerdict, VerdictEval


def evaluate_verdict(verdict: CouncilVerdict) -> VerdictEval:
    findings: list[str] = []
    targets: list[str] = []
    score = 0

    if verdict.recommendation and len(verdict.recommendation) >= 20:
        score += 20
        findings.append("Verdict gives a direct recommendation.")
    else:
        targets.append("Make the recommendation direct and specific.")

    if verdict.dissent:
        score += 15
        findings.append("Verdict preserves dissent instead of hiding disagreement.")
    else:
        targets.append("Include material dissent or explain why none exists.")

    if len(verdict.safeguards) >= 3:
        score += 25
        findings.append("Verdict includes multiple safeguards.")
    else:
        targets.append("Add at least three concrete safeguards.")

    if len(verdict.next_actions) >= 3:
        score += 25
        findings.append("Verdict includes concrete next actions.")
    else:
        targets.append("Add at least three immediate next actions.")

    if 45 <= verdict.confidence <= 85:
        score += 15
        findings.append("Confidence appears calibrated, not blindly overconfident.")
    else:
        targets.append("Calibrate confidence; avoid unsupported certainty.")

    return VerdictEval(score=score, passed=score >= 75, findings=findings, improvement_targets=targets)
