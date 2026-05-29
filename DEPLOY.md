# Cloud Run deploy notes

```bash
gcloud run deploy decision-council-demo \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_MODEL=gemini-2.5-flash,ENABLE_PHOENIX_TRACING=true,PHOENIX_PROJECT_NAME=decision-council-demo
```

Add secrets for `GEMINI_API_KEY`, `PHOENIX_API_KEY`, and `PHOENIX_COLLECTOR_ENDPOINT` using Secret Manager or Cloud Run environment variables before the final demo.
