#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / 'drafts' / 'ratgeber'
MARKERS = [
    'НУЖНО ПРОВЕРИТЬ',
    '[НУЖНО ПРОВЕРИТЬ',
    '[private CTA target omitted]',
    '[CTA omitted in public repo]',
    'TODO',
    'TBD',
    'PLACEHOLDER',
]


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith('---\n'):
        return {}, text
    end = text.find('\n---\n', 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        data[key.strip()] = value.strip().strip('"\'')
    return data, body


def truthy(value: str | None) -> bool:
    return bool(value) and value.lower() in {'true', 'yes', '1', 'ready', 'publish'}


def ready_candidate(meta: dict[str, str]) -> bool:
    return any(
        [
            truthy(meta.get('ready_for_publish')),
            meta.get('gate_status', '').lower() == 'ready',
            meta.get('publish_gate', '').lower() == 'ready',
            meta.get('wp_status', '').lower() == 'publish',
        ]
    )


def main() -> int:
    if not DRAFTS.exists():
        print('content_gate: no drafts directory found', file=sys.stderr)
        return 1

    checked = 0
    fails = 0

    for path in sorted(DRAFTS.glob('*.md')):
        meta, body = parse_front_matter(path.read_text(encoding='utf-8'))
        if not meta or not ready_candidate(meta):
            continue

        checked += 1
        problems = []
        if meta.get('gate_status', '').lower() != 'ready':
            problems.append('front-matter gate_status is not ready')
        if meta.get('publish_gate', '').lower() != 'ready':
            problems.append('front-matter publish_gate is not ready')
        if truthy(meta.get('ready_for_publish')) and meta.get('gate_status', '').lower() != 'ready':
            problems.append('ready_for_publish true but gate_status disagrees')
        if truthy(meta.get('ready_for_publish')) and meta.get('publish_gate', '').lower() != 'ready':
            problems.append('ready_for_publish true but publish_gate disagrees')

        for marker in MARKERS:
            if marker in body:
                problems.append(f'body marker present: {marker}')

        if problems:
            fails += 1
            print(f'FAIL {path.relative_to(ROOT)}')
            for problem in problems:
                print(f'  - {problem}')

    print(f'content_gate: checked={checked} fails={fails}')
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main())
