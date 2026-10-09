# Swagger e OpenAPI do Odin RAG MCP

Este documento registra a interface da API em formato OpenAPI/Swagger e reforça a natureza open source do projeto.

## Acesso ao Swagger UI

Ao iniciar a API, a interface Swagger fica disponível em:

- http://localhost:8001/docs
- http://localhost:8001/redoc
- http://localhost:8001/openapi.json

## Observações sobre o projeto

- Licença: MIT
- Modelo de uso: open source, reutilizável e extensível
- Interface: REST + OpenAPI + MCP
- Compatibilidade: pode ser consumido por frontends, integrações, automatizações e agentes externos

## Exemplo de uso

### Health

GET /health

### Consulta

POST /chat

```json
{
  "question": "Qual é a finalidade do Odin?"
}
```

### Ingestão de documentos

POST /mcp

```json
{
  "method": "ingest",
  "params": {
    "documents": [
      "Odin é um agente de IA de código aberto para recuperação de contexto e respostas rastreáveis.",
      "A aplicação suporta modelos de IA de múltiplos provedores e integrações via MCP."
    ]
  }
}
```

### Consulta contextualizada

POST /mcp

```json
{
  "method": "query",
  "params": {
    "question": "Como o Odin processa contexto e resposta?"
  }
}
```

O projeto foi desenhado para ser usado conforme padrões abertos, com documentação automática e possibilidade de extensão sem bloqueio de fornecedor.
