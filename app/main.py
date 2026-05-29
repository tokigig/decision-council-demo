from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.councils.types import CouncilContext
from src.deliberation.run_council import run_council
from src.demo.sample_contexts import MADGESFOOD_AI_CHECKOUT
from src.providers.phoenix_tracing import setup_tracing
from fastapi.responses import HTMLResponse, RedirectResponse

load_dotenv()
setup_tracing()

app = FastAPI(title="Decision Council", version="0.1.0")


def _layout(body: str) -> str:
    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Decision Council</title>
  <style>
    :root {{ color-scheme: dark; --bg:#08111f; --panel:#111d2f; --muted:#9fb1c8; --text:#eef5ff; --accent:#5eead4; --line:#23344d; --warn:#fbbf24; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; background: radial-gradient(circle at top, #12243b, var(--bg)); color:var(--text); }}
    main {{ max-width:1120px; margin:0 auto; padding:48px 20px; }}
    .eyebrow {{ color:var(--accent); letter-spacing:.16em; text-transform:uppercase; font-size:12px; font-weight:700; }}
    h1 {{ font-size: clamp(42px, 7vw, 82px); line-height:.94; margin:12px 0 18px; }}
    h2 {{ font-size:28px; margin:0 0 12px; }}
    h3 {{ margin:0 0 8px; }}
    p {{ color:var(--muted); line-height:1.65; }}
    .hero {{ display:grid; grid-template-columns:1.1fr .9fr; gap:28px; align-items:start; }}
    .panel {{ background:rgba(17,29,47,.84); border:1px solid var(--line); border-radius:24px; padding:24px; box-shadow: 0 24px 80px rgba(0,0,0,.24); }}
    label {{ display:block; font-weight:700; margin:16px 0 8px; }}
    input, textarea, select {{ width:100%; padding:13px 14px; background:#08111f; color:var(--text); border:1px solid var(--line); border-radius:14px; font:inherit; }}
    textarea {{ min-height:120px; }}
    button {{ margin-top:18px; width:100%; padding:14px 18px; border:0; border-radius:14px; background:linear-gradient(135deg,#5eead4,#60a5fa); color:#031018; font-weight:900; cursor:pointer; }}
    .grid {{ display:grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap:18px; margin-top:18px; }}
    .card {{ background:rgba(8,17,31,.72); border:1px solid var(--line); border-radius:18px; padding:18px; }}
    .badge {{ display:inline-flex; border:1px solid var(--line); border-radius:999px; padding:5px 10px; color:var(--accent); font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:.08em; }}
    .list {{ margin:10px 0 0; padding-left:20px; color:var(--muted); line-height:1.55; }}
    .verdict {{ border-color: rgba(94,234,212,.55); background:linear-gradient(180deg, rgba(94,234,212,.12), rgba(17,29,47,.84)); }}
    .trace {{ color:#bfdbfe; }}
    .small {{ font-size:13px; }}
    @media (max-width: 860px) {{ .hero,.grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body><main>{body}</main></body></html>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    body = """
<section class="hero">
  <div>
    <div class="eyebrow">Decision Council · by tokiOS</div>
    <h1>Self-auditing AI councils for high-stakes decisions.</h1>
    <p>Run a Gemini-powered deliberation team, trace each step to Phoenix, evaluate the verdict, and feed observability insight back into the next decision.</p>
    <div class="grid">
      <div class="card"><span class="badge">Deliberate</span><p>Independent advisors plus a challenge round.</p></div>
      <div class="card"><span class="badge">Observe</span><p>OpenInference/Phoenix tracing hooks around each agent step.</p></div>
      <div class="card"><span class="badge">Evaluate</span><p>Verdict quality checks for dissent, safeguards, actions, and confidence.</p></div>
      <div class="card"><span class="badge">Improve</span><p>Phoenix MCP introspection path for self-improvement.</p></div>
    </div>
  </div>
  <form class="panel" method="post" action="/run">
    <h2>Run a council</h2>
    <label>Council</label>
    <select name="preset_id">
      <option value="ai_adoption">AI Adoption Council</option>
      <option value="risk_review">Risk Review Council</option>
      <option value="launch_review">Launch Review Council</option>
    </select>
    <label>Business name</label>
    <input name="business_name" value="MadgesFood" />
    <label>Decision question</label>
    <textarea name="decision_question">Should MadgesFood enable AI-agent checkout?</textarea>
    <label>Background</label>
    <textarea name="background">MadgesFood is exploring whether AI shopping agents should be allowed to discover products, assemble carts, and complete checkout on behalf of customers.</textarea>
    <button type="submit">Run Decision Council</button>
    <p class="small">Uses Gemini through Google Cloud ADC/Vertex when configured. Falls back to deterministic demo mode only when Gemini is unavailable. Add Gemini and Phoenix keys for live tracing.</p>
  </form>
</section>
"""
    return _layout(body)


def _opinion_card(opinion) -> str:
    risks = "".join(f"<li>{risk}</li>" for risk in opinion.risks)
    actions = "".join(f"<li>{action}</li>" for action in opinion.recommended_actions)
    return f"""
<div class="card">
  <span class="badge">{opinion.stance} · {opinion.confidence}%</span>
  <h3>{opinion.member_name}</h3>
  <p>{opinion.reasoning}</p>
  <strong>Risks</strong><ul class="list">{risks}</ul>
  <strong>Actions</strong><ul class="list">{actions}</ul>
</div>
"""


def _list(items: list[str]) -> str:
    return "".join(f"<li>{item}</li>" for item in items)

@app.get("/run")
def run_get():
    return RedirectResponse(url="/", status_code=303)

@app.post("/run", response_class=HTMLResponse)
def run_form(
    preset_id: str = Form("ai_adoption"),
    business_name: str = Form(""),
    decision_question: str = Form(""),
    background: str = Form(""),
) -> str:
    context = CouncilContext(
        business_name=business_name or None,
        decision_question=decision_question or MADGESFOOD_AI_CHECKOUT.decision_question,
        background=background or MADGESFOOD_AI_CHECKOUT.background,
        constraints=MADGESFOOD_AI_CHECKOUT.constraints,
        known_facts=MADGESFOOD_AI_CHECKOUT.known_facts,
    )
    result = run_council(preset_id, context)
    verdict = result.verdict
    cards = "".join(_opinion_card(o) for o in result.challenge_opinions)
    body = f"""
<a class="trace" href="/">← New council</a>
<section class="panel verdict" style="margin-top:18px;">
  <span class="badge">Verdict · {verdict.confidence}% confidence</span>
  <h1 style="font-size:46px;">{verdict.recommendation}</h1>
  <p>{verdict.summary}</p>
  <p class="trace">Trace/session id: {result.run_id}</p>
</section>
<section class="grid">
  <div class="card"><h2>Dissent</h2><ul class="list">{_list(verdict.dissent)}</ul></div>
  <div class="card"><h2>Safeguards</h2><ul class="list">{_list(verdict.safeguards)}</ul></div>
  <div class="card"><h2>Next actions</h2><ul class="list">{_list(verdict.next_actions)}</ul></div>
  <div class="card"><h2>Quality eval</h2><span class="badge">Score {result.eval.score} · {'Passed' if result.eval.passed else 'Needs work'}</span><ul class="list">{_list(result.eval.findings + result.eval.improvement_targets)}</ul></div>
</section>
<section class="panel" style="margin-top:18px;">
  <h2>Self-improvement note</h2>
  <p>{result.self_improvement_note}</p>
</section>
<h2 style="margin-top:28px;">Challenge round advisor positions</h2>
<section class="grid">{cards}</section>
"""
    return _layout(body)


@app.post("/api/council/run")
def run_api(payload: CouncilContext, preset_id: str = "ai_adoption"):
    return JSONResponse(run_council(preset_id, payload).model_dump())
