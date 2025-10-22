#!/usr/bin/env python3
"""Atomic reindex helper

Usage:
  python3 scripts/atomic_reindex.py [--run] [--collection-name NAME]

Behavior:
- By default does a dry run: prints the new collection name it would create.
- With --run it will set an environment variable CHROMA_COLLECTION to the new name
  and call the ingestion pipeline function. On success it writes the new collection
  name to `data/vector_db/current_collection.txt` as the active collection manifest.

Note: This script expects to be run from the project root and will not change
code; it only orchestrates env and calls the existing ingestion API.
"""
import argparse
import os
from datetime import datetime
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from aasthasathi.ingestion.pipeline import run_ingestion_pipeline
from aasthasathi.core.config import get_settings


def generate_collection_name(base_name: str = None):
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    base = base_name or get_settings().chroma_collection_name
    return f"{base}_v{ts}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true', help='Execute ingestion into the new collection')
    parser.add_argument('--collection-name', type=str, help='Supply a custom collection name')
    parser.add_argument('--pdf-dir', type=str, default='data/raw', help='PDF directory to pass to ingestion')
    parser.add_argument('--website-pages', type=int, default=50, help='Max website pages to scrape')
    args = parser.parse_args()

    new_name = args.collection_name or generate_collection_name()
    print('Planned new collection:', new_name)

    if not args.run:
        print('Dry run. Use --run to execute ingestion into the new collection')
        return

    # Set CHROMA_COLLECTION env var just for this process
    os.environ['CHROMA_COLLECTION'] = new_name

    try:
        # Run ingestion pipeline (this will pick up CHROMA_COLLECTION via settings/env)
        import asyncio
        print('Starting ingestion into', new_name)
        success = asyncio.run(run_ingestion_pipeline(pdf_directory=args.pdf_dir, website_max_pages=args.website_pages, clear_existing=False))

        if success:
            # Write manifest
            manifest = Path('data/vector_db') / 'current_collection.txt'
            manifest.parent.mkdir(parents=True, exist_ok=True)
            with open(manifest, 'w') as f:
                f.write(new_name)
            print('Ingestion succeeded. New collection set in', manifest)
        else:
            print('Ingestion failed; manifest not updated')

    except Exception as e:
        print('Error during atomic reindex:', e)


if __name__ == '__main__':
    main()
