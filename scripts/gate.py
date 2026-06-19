#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'state' / 'wp-state.json'


def main() -> int:
    try:
        data = json.loads(STATE.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'gate: cannot read state/wp-state.json: {exc}', file=sys.stderr)
        return 1

    if data.get('version') != 1:
        print('gate: unsupported state version', file=sys.stderr)
        return 1

    articles = data.get('articles')
    if not isinstance(articles, list):
        print('gate: articles must be a list', file=sys.stderr)
        return 1

    published = [a for a in articles if a.get('published')]
    for a in articles:
        for key in ('slug', 'title', 'wp_post_id', 'stage', 'gate', 'published'):
            if key not in a:
                print(f"gate: missing {key} in {a!r}", file=sys.stderr)
                return 1
        if a.get('published') and a.get('gate') != 'ready':
            print(f"gate: published article must have gate=ready: {a['slug']}", file=sys.stderr)
            return 1

    blocked = sum(1 for a in articles if a.get('gate') in {'not ready', 'blocker'})
    print(f'gate: ok | articles={len(articles)} | published={len(published)} | blocked={blocked}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
