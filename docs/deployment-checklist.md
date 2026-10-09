# Deployment Checklist

## Pre-deployment
- [ ] Confirm Python version is 3.10 or newer
- [ ] Install all dependencies from `requirements.txt`
- [ ] Define `.env` values for your provider and security settings
- [ ] Choose the model provider: OpenAI, Anthropic, Ollama, LiteLLM, OpenRouter or Azure OpenAI
- [ ] Set `JWT_SECRET` or `ODIN_API_KEY` depending on auth strategy
- [ ] Confirm CORS origins match your frontend domain

## Security hardening
- [ ] Use a strong secret for JWT or API key
- [ ] Enable TLS in front of the API
- [ ] Keep rate limits enabled for public endpoints
- [ ] Review audit logs and trace IDs during integration tests
- [ ] Restrict access to docs and internal endpoints in production

## Runtime validation
- [ ] Run the test suite: `python -m pytest tests/test_security.py -q`
- [ ] Verify the app boots with Uvicorn
- [ ] Test `/health`
- [ ] Test `/providers`
- [ ] Test `/chat`
- [ ] Test `/mcp` ingestion and query flows
- [ ] Call `/metrics` and confirm values are returned

## Production recommendations
- [ ] Replace in-memory storage with a vector database for durable search
- [ ] Add container image or orchestration config for deployment automation
- [ ] Place API behind a reverse proxy with HTTPS
- [ ] Add monitoring, backups and alerting for operational resilience
- [ ] Record provider usage and token consumption for cost control

## Open-source posture
- [ ] Keep repo license visible and consistent
- [ ] Document setup steps clearly for contributors
- [ ] Keep endpoints discoverable through Swagger/OpenAPI
- [ ] Use conventional commit messages and public changelogs
