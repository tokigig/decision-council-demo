# Decision Council

**Self-auditing AI councils for high-stakes business decisions.**

Decision Council is a public hackathon reference implementation by tokiOS. It demonstrates a Gemini-powered deliberation engine where specialized AI advisors evaluate a business decision, challenge each other, synthesize a verdict, and prepare the run for observability and self-improvement through Arize Phoenix.

## Live demo

Public demo URL:

http://34.27.103.208

The public demo runs on Google Kubernetes Engine using a Kubernetes `LoadBalancer` service.

Cloud Run was also validated successfully, but this Google Cloud project inherits an organization policy that blocks public `allUsers` Cloud Run invoker bindings. GKE LoadBalancer is used as the public web entrypoint for the hackathon demo.

## Current deployed proof

- Public web app: `http://34.27.103.208`
- Runtime: FastAPI code-owned agent runtime
- Model: Gemini through Google Cloud Vertex AI / ADC
- Public platform: Google Kubernetes Engine Autopilot
- Observability: Arize Phoenix / OpenInference tracing
- Phoenix project: `decision-council-demo`
- Example trace/session id: `59a4dd75-9b97-42f7-bc89-5d921054698c`
- Trace structure includes `council.run`, independent advisor rounds, challenge advisor rounds, synthesis, and eval spans.

## What it does

A user selects a council, enters a business decision, and receives an auditable recommendation with:

- advisor dissent
- confidence
- safeguards
- next actions
- quality evaluation
- trace/session metadata
- applied improvement directives

The current demo supports:

- AI Adoption Council
- Risk Review Council
- Launch Review Council

## Why it matters

Single-chatbot business advice can be opaque, overconfident, and hard to improve.

Decision Council uses a multi-agent council pattern so decisions are debated from multiple perspectives before a recommendation is produced. Each run is traced so the system can inspect what happened, evaluate quality, and feed improvement directives into future council runs.

The long-term product direction is observable deliberation: every agent step should be inspectable, evaluable, and improvable.

## Architecture

```txt
Browser UI
  -> FastAPI council runtime
  -> Council presets
  -> Gemini / Vertex AI provider
  -> Independent advisor round
  -> Challenge round
  -> Verdict synthesis
  -> Quality evaluation
  -> Phoenix tracing / MCP introspection path