"""In-memory knowledge base used for retrieval augmented generation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class KnowledgeDocument:
    """A single indexed document used to enrich the model context."""

    content: str
    source: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


class KnowledgeBase:
    """Simple retrieval implementation that keeps documents in memory.

    This class intentionally keeps the logic simple and transparent so it can be
    replaced by a vector database later without changing the public behavior.
    """

    def __init__(self) -> None:
        self.documents: list[KnowledgeDocument] = []

    def index(self, documents: list[str] | list[KnowledgeDocument]) -> int:
        """Insert new documents into memory and return the total size."""
        for item in documents:
            if isinstance(item, str):
                self.documents.append(KnowledgeDocument(content=item))
            else:
                self.documents.append(item)
        return len(self.documents)

    def search(self, query: str, limit: int = 5) -> list[dict[str, str]]:
        """Return a ranked list of matching documents by keyword overlap."""
        if not query or not query.strip():
            return []

        lowered_query = query.lower()
        terms = {term for term in lowered_query.split() if len(term) > 2}

        scored: list[tuple[float, str]] = []
        for document in self.documents:
            text = document.content.lower()
            score = sum(1 for term in terms if term in text)
            if score == 0 and terms:
                score = 0.1
            scored.append((float(score), document.content))

        ranked = sorted(scored, key=lambda item: item[0], reverse=True)[:limit]
        return [{"content": content, "score": str(score)} for score, content in ranked]
