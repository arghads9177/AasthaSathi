"""Agent package for RAG and later API-tooling.

This package currently implements a RAG-only Agent with LangChain/LangGraph
integration when available, and a robust fallback when those libraries or API
keys are not present. The Agent API is intentionally small:

    from aasthasathi.agent import Agent
    agent = Agent(vector_db)
    result = agent.answer_query("How to open a savings account?")

Result is a dict: {'success': bool, 'answer': str, 'citations': list}
"""

from .agent import Agent
from .prompting import build_prompt, DEFAULT_PROMPT

__all__ = ["Agent", "build_prompt", "DEFAULT_PROMPT"]
