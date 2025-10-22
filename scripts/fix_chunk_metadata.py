#!/usr/bin/env python3
"""Migration: add normalized `source` metadata to existing collection entries.

This script will:
- instantiate the VectorDatabase
- fetch all ids and metadatas from the collection
- add a `source` field where missing using a heuristic
- call collection.update(...) to patch metadatas in-place

Run this after backing up the collection if you want a safety copy.
"""
import sys
from pathlib import Path

# ensure project root is importable
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from aasthasathi.ingestion.vector_database import VectorDatabase


def infer_source_from_metadata(md: dict, doc_id: str) -> str:
    doc_id_lower = str(doc_id or '').lower()
    if doc_id_lower.startswith('pdf_') or md.get('file_name') or md.get('file_path'):
        return 'pdf_manual'
    if doc_id_lower.startswith('web_') or md.get('url') or md.get('content_type'):
        return 'website'
    return 'unknown'


def main():
    vdb = VectorDatabase()
    coll = vdb.collection

    print('Fetching full collection...')
    try:
        results = coll.get()
    except Exception as e:
        print('Error getting collection:', e)
        return

    ids = results.get('ids', [])
    metadatas = results.get('metadatas', [])

    if not ids:
        print('No documents found in collection')
        return

    print(f'Found {len(ids)} items. Scanning for missing `source`...')

    updated_metadatas = []
    changed = 0
    for idx, md in enumerate(metadatas):
        if md is None:
            md = {}
        # ensure dict
        if not isinstance(md, dict):
            # try parse or stringify
            try:
                import json
                md = json.loads(md)
            except Exception:
                md = { 'raw': str(md) }

        if 'source' not in md or not md.get('source'):
            new_source = infer_source_from_metadata(md, ids[idx] if idx < len(ids) else '')
            md['source'] = new_source
            changed += 1
        updated_metadatas.append(md)

    print(f'Will update {changed} metadatas (out of {len(ids)})')
    if changed == 0:
        print('Nothing to do.')
        return

    # Backup small sample to disk
    backup_file = Path(vdb.settings.vector_db_path) / f'metadata_backup_{vdb.settings.chroma_collection_name}.json'
    try:
        import json
        backup = { 'ids': ids, 'metadatas': metadatas }
        with open(backup_file, 'w') as f:
            json.dump(backup, f)
        print('Wrote backup of metadatas to', backup_file)
    except Exception as e:
        print('Warning: failed to write backup:', e)

    # Try to update in-place
    try:
        coll.update(ids=ids, metadatas=updated_metadatas)
        print('Successfully updated metadatas in collection')
    except Exception as e:
        print('Error updating collection metadatas:', e)
        print('As fallback, you may need to recreate collection and re-add records with updated metadata')


if __name__ == '__main__':
    main()
