import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    # Prefer LangChain + LangGraph if available
    import langchain
    HAS_LANGCHAIN = True
except Exception:
    HAS_LANGCHAIN = False

import os
try:
    import openai
    HAS_OPENAI_SDK = True
except Exception:
    HAS_OPENAI_SDK = False

from aasthasathi.ingestion.vector_database import VectorDatabase
from .prompting import build_prompt


@dataclass
class AgentResult:
    success: bool
    answer: str
    citations: List[Dict]


class Agent:
    """RAG-only Agent. Uses VectorDatabase for retrieval and an LLM for
    generation. If LangChain is available, it will use it; otherwise a simple
    fallback generator is used (for smoke tests).
    """

    def __init__(self, vector_db: Optional[VectorDatabase] = None, llm=None):
        self.vector_db = vector_db or VectorDatabase()
        self.llm = llm

        # If LangChain is present and no llm provided, attempt to create one
        if HAS_LANGCHAIN and self.llm is None:
            try:
                from langchain.llms import OpenAI
                self.llm = OpenAI(temperature=0)
            except Exception as e:
                logger.debug('LangChain OpenAI LLM not available: %s', e)
                self.llm = None

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve top-k chunks from vector DB and return formatted results."""
        try:
            results = self.vector_db.search_documents(query, n_results=top_k)
            return results
        except Exception as e:
            logger.error('Retrieval error: %s', e)
            return []

    def generate(self, prompt: str) -> str:
        """Generate a response using the LLM or a fallback summarizer."""
        # If OpenAI SDK is available and API key present, prefer direct call
        openai_key = os.environ.get('OPENAI_API_KEY')
        model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
        if HAS_OPENAI_SDK and openai_key:
            try:
                # Use ChatCompletion API
                openai.api_key = openai_key
                resp = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                # Extract content
                content = resp.choices[0].message.get('content') if resp.choices else None
                if content:
                    return content
            except Exception as e:
                logger.error('OpenAI SDK call failed: %s', e)

        # Otherwise, if LangChain LLM is available, use it
        if self.llm is not None:
            try:
                if HAS_LANGCHAIN:
                    return self.llm(prompt)
                else:
                    return self.llm.generate(prompt)
            except Exception as e:
                logger.error('LLM generation failed: %s', e)

        # Simple deterministic fallback: echo prompt trimmed
        logger.debug('Using fallback generator')
        out = '\n'.join([p.strip() for p in prompt.split('\n') if p.strip()])
        return out[:2000]

    def answer_query(self, query: str, top_k: int = 5) -> Dict:
        """Main entry: perform retrieval, build prompt, call LLM, and format result."""
        retrieved = self.retrieve(query, top_k=top_k)

        # Build the prompt using retrieved texts
        prompt = build_prompt(query, retrieved)

        generated = self.generate(prompt)

        # Format citations from retrieved chunks (include id, metadata, snippet)
        citations = []
        for r in retrieved:
            md = r.get('metadata', {}) or {}
            snippet = (r.get('content') or '')[:400]
            citations.append({
                'id': r.get('id'),
                'title': md.get('title') or md.get('file_name') or md.get('content_type'),
                'source': md.get('source'),
                'url': md.get('url'),
                'file_path': md.get('file_path'),
                'snippet': snippet,
                'similarity': r.get('similarity')
            })

        return AgentResult(success=True, answer=generated, citations=citations).__dict__
