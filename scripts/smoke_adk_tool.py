"""
Smoke test for the Google ADK-facing Decision Council tool.

This directly calls the tool function exposed to the ADK agent. It proves that:
- the ADK entrypoint can import,
- the council engine can run through the tool path,
- an optional Gemini-powered subject-matter expert can be injected,
- the same Phoenix-traced council runtime is used.
"""

import sys
from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.adk.decision_council_agent import root_agent, run_decision_council_tool

load_dotenv()


def main() -> None:
    print("ADK root_agent available:", root_agent is not None)

    result = run_decision_council_tool(
        council_id="ai_adoption",
        business_name="Stephen's Roofing",
        decision_question="Should my local roofing company become AI ready?",
        background=(
            "Stephen's Roofing has been a local roofing company for 20 years. "
            "They handle phone calls, quote requests, repair questions, scheduling issues, "
            "crew coordination, and emergency roof leak requests. The owner wants practical "
            "advice without hurting customer trust."
        ),
        expert_name="Roofing Operations Expert",
        expert_role="Local service business operations specialist",
        expert_mandate=(
            "Evaluate quote flow, emergency leak calls, crew scheduling, office workload, "
            "customer callbacks, and owner approval needs for a local roofing company."
        ),
    )

    verdict = result["verdict"]

    print("\nRun ID:")
    print(result["run_id"])

    print("\nRecommendation:")
    print(verdict["recommendation"])

    print("\nConfidence:")
    print(verdict["confidence"])

    print("\nApplied improvement directives:")
    pprint(result["applied_improvement_directives"])

    print("\nChallenge advisors:")
    for opinion in result["challenge_opinions"]:
        print(f"- {opinion['member_name']} ({opinion['stance']} · {opinion['confidence']}%)")


if __name__ == "__main__":
    main()