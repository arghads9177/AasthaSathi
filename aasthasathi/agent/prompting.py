"""Prompting helpers for the RAG agent."""

DEFAULT_PROMPT = (
    "You are an assistant that answers questions using provided context. "
    "Use the context to ground your answer and cite sources when helpful.\n\n"
)


def build_prompt(query: str, retrieved: list) -> str:
    """Build a prompt by concatenating top-k retrieved snippets and the query."""
    parts = [DEFAULT_PROMPT]
    parts.append('Context:')
    if not retrieved:
        parts.append('No relevant documents found.')
    else:
        for i, r in enumerate(retrieved):
            md = r.get('metadata', {}) or {}
            title = md.get('title') or md.get('file_name') or md.get('content_type') or f"doc_{i}"
            snippet = (r.get('content') or '')[:800]
            parts.append(f"[{i+1}] {title} (source={md.get('source')})\n{snippet}\n---\n")

    parts.append('\nUser question:')
    parts.append(query)
    parts.append('\nAnswer concisely and cite sources like [1], [2] when using them.')

    return '\n'.join(parts)
