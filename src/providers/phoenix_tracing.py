import os
from contextlib import contextmanager
from typing import Any, Iterator

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

_TRACER_READY = False

def setup_tracing() -> None:
    global _TRACER_READY
    if _TRACER_READY:
        return
    if os.getenv("ENABLE_PHOENIX_TRACING", "false").lower() != "true":
        _TRACER_READY = True
        return
    try:
        from phoenix.otel import register
        from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

        project_name = os.getenv("PHOENIX_PROJECT_NAME", "decision-council-demo")
        tracer_provider = register(project_name=project_name, auto_instrument=True)
        GoogleGenAIInstrumentor().instrument(tracer_provider=tracer_provider)
        _TRACER_READY = True
    except Exception as exc:
        print(f"Phoenix tracing setup skipped: {exc}")
        _TRACER_READY = True

def get_tracer():
    setup_tracing()
    return trace.get_tracer("decision-council-demo")

@contextmanager
def council_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[Any]:
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        for key, value in (attributes or {}).items():
            if value is not None:
                span.set_attribute(key, value)
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
