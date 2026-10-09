# Release Notes

## Version 0.1.0 — production-ready starter for RAG + MCP

### Highlights
- Multi-provider AI abstraction for OpenAI, Anthropic, Ollama, LiteLLM, OpenRouter and Azure OpenAI
- In-memory RAG flow with document ingestion and contextual retrieval
- MCP server exposing tools for knowledge search, querying and ingestion
- JWT and API-key security layer
- Rate limiting, request size control, security headers and audit logging
- OpenAPI/Swagger documentation enabled by default through FastAPI
- LangChain + LangSmith support for optional tracing and observability

### Included features
- Health and metrics endpoints
- Secure API contract with structured responses
- Trace ID correlation for every request
- Documentation-ready REST interface with Swagger UI

### Use cases
- Internal knowledge assistants
- Local document AI prototypes
- AI orchestration experiments
- API-backed chat layers for enterprise knowledge tools
- Open-source extension point for custom providers and integrations

### Known considerations
- Knowledge base is in-memory by default and is intended for local or prototype use
- For production persistence, a vector database such as FAISS, Qdrant or pgvector should be introduced behind the same abstraction
- Real LLM provider credentials are required for live completion generation

### Recommended deployment checklist
- configure environment variables
- set JWT or API-key authentication
- choose a provider and model
- enable LangSmith if tracing is desired
- keep the API behind TLS in production
- add persistence for knowledge storage in a later phase

### Compatibility
- Python 3.10+
- FastAPI
- modern OpenAI-compatible APIs
- standard HTTP clients and MCP-compatible clients
