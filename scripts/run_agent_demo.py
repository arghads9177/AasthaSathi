#!/usr/bin/env python3
"""Demo runner for the RAG-only Agent"""
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from aasthasathi.agent import Agent
from aasthasathi.core.models import User

QUERIES = [
    "How can I open a savings account?",
    "What is the mission of Aastha Co-operative Credit Society?",
    "How to apply for a personal loan?",
]


def main():
    agent = Agent()

    for q in QUERIES:
        print('\n' + '='*40)
        print('Query:', q)
        res = agent.answer_query(q, top_k=5)
        print('\nAnswer:')
        print(res['answer'][:1000])
        print('\nCitations:')
        for c in res['citations'][:5]:
            print('-', c['id'], c['title'], c.get('source'), c.get('similarity'))

if __name__ == '__main__':
    main()
