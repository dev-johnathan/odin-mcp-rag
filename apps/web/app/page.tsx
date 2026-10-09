'use client';

import { FormEvent, useState } from 'react';

export default function HomePage() {
  const [question, setQuestion] = useState('Qual é a visão geral do agente Odin?');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8001'}/chat`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, provider: 'openai' }),
        },
      );

      const data = await response.json();
      setAnswer(data.answer ?? 'Sem resposta no momento.');
    } catch (error) {
      setAnswer('Falha ao conectar com a API do Odin. Verifique se o backend está em execução.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="panel hero-panel">
        <div className="hero-badge">Odin RAG MCP</div>
        <h1>Agente de sabedoria operacional</h1>
        <p>
          Um agente modular para pesquisa, recuperação de contexto e geração de
          respostas com múltiplos provedores de IA.
        </p>
      </section>

      <section className="panel form-panel">
        <form onSubmit={handleSubmit} className="chat-form">
          <label htmlFor="question">Pergunta para o agente</label>
          <textarea
            id="question"
            rows={5}
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ex.: Descreva a arquitetura do Odin e como ele recupera contexto..."
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Consultando...' : 'Consultar Odin'}
          </button>
        </form>
      </section>

      <section className="panel answer-panel">
        <h2>Resposta</h2>
        <p>{answer || 'A resposta do agente aparecerá aqui.'}</p>
      </section>
    </main>
  );
}
