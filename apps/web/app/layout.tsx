import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Odin RAG MCP',
  description: 'Agente de IA modular com RAG e MCP',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
