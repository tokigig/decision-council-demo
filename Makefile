.PHONY: dev check docker-build docker-run

dev:
	uvicorn app.main:app --reload --port 8080

check:
	python -m compileall app src
	python - <<'PY'
from src.deliberation.run_council import run_council
from src.demo.sample_contexts import MADGESFOOD_AI_CHECKOUT
result = run_council('ai_adoption', MADGESFOOD_AI_CHECKOUT)
assert result.verdict.recommendation
assert result.eval.score >= 0
print('Decision Council smoke test passed:', result.run_id)
PY

docker-build:
	docker build -t decision-council-demo .

docker-run:
	docker run --rm -p 8080:8080 --env-file .env decision-council-demo
