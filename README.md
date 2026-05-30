# Decision Council

**Self-auditing AI councils for high-stakes business decisions.**

Decision Council is a public hackathon reference implementation by tokiOS. It demonstrates a simplified Gemini-powered deliberation engine where specialized AI advisors evaluate a business decision, challenge each other, synthesize a verdict, and prepare the run for observability and self-improvement through Arize Phoenix.

## What it does

A user selects a council, enters a business decision, and receives an auditable recommendation with:

- advisor dissent
- confidence
- safeguards
- next actions
- quality evaluation
- trace/session metadata

The current demo supports:

- AI Adoption Council
- Risk Review Council
- Launch Review Council

## Why it matters

Single-chatbot business advice can be opaque, overconfident, and hard to improve. Decision Council uses a multi-agent council pattern so decisions are debated from multiple perspectives before a recommendation is produced.

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