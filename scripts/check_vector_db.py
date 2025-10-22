#!/usr/bin/env python3
"""Quick vector DB health check script

Prints collections, stats and runs a set of sample queries to validate that
PDF and scraped website content is indexed and retrievable.
"""
import sys
from pathlib import Path
# Ensure project root is on sys.path so imports work when running this script
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from aasthasathi.ingestion.vector_database import VectorDatabase

COMMON_QUERIES = [
    "savings account",
    "how to become a member",
    "fixed deposit",
    "loan",
    "member details",
    "Mission of Aastha Co-operative Credit Society",
]


def print_stats(vdb: VectorDatabase):
    print("\n--- Collections ---")
    try:
        cols = [c for c in vdb.client.list_collections()]
        print(cols)
    except Exception as e:
        print("Error listing collections:", e)

    print("\n--- Collection stats ---")
    try:
        stats = vdb.get_collection_stats()
        for k, v in stats.items():
            print(f"{k}: {v}")
    except Exception as e:
        print("Error getting stats:", e)


def run_queries(vdb: VectorDatabase):
    print("\n--- Sample queries ---")
    for q in COMMON_QUERIES:
        print(f"\nQuery: {q}")
        try:
            results = vdb.search_documents(q, n_results=5)
            if not results:
                print("  No results")
                continue
            for i, r in enumerate(results):
                md = r.get("metadata", {})
                title = md.get("title") or md.get("file_name") or md.get("document_type") or md.get("content_type")
                print(f"  {i+1}. id={r['id']}, similarity={r['similarity']:.3f}, title={title}")
                snippet = (r['content'] or "")[:200].replace("\n", " ")
                print(f"     snippet: {snippet}")
        except Exception as e:
            print("  Error querying:", e)


if __name__ == '__main__':
    vdb = VectorDatabase()
    print_stats(vdb)
    run_queries(vdb)
