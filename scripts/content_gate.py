#!/usr/bin/env python3
"""
Content gate for vorino-content-public (hardened).
Stdlib-only. Вывод совместим: 'content_gate: checked=N fails=N blocked=N'.

Для статьи, помеченной ready:
  R1 gate_status и publish_gate оба == ready
  R2 ready_for_publish: true ⇒ оба поля ready
  R3 needs_verification ДОЛЖЕН быть false
  R4 в теле нет маркеров: НУЖНО ПРОВЕРИТЬ / TODO / TBD / FIXME / PLACEHOLDER / Lorem ipsum / XXX
  R5 нет пустых markdown-ссылок ( ]( ) или ](#) )
Скан drafts/**/*.md. Намеренные пометки об отсутствии CTA в публичном репо — допустимы.
Exit 0 — чисто; 1 — нарушение у ready-статьи.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"

FORBIDDEN = ["НУЖНО ПРОВЕРИТЬ", "TODO", "TBD", "FIXME", "PLACEHOLDER", "Lorem ipsum", "XXX"]
ALLOWED = ("[CTA omitted in public repo]", "[private CTA target omitted]")
LINK = re.compile(r"\[[^\]]+\]\(([^)]*)\)")


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw, body = text[4:end], text[end + 5:]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip("\"'")
    return data, body


def truthy(value: str | None) -> bool:
    return bool(value) and value.lower() in {"true", "yes", "1", "ready", "publish"}


def ready_candidate(meta: dict[str, str]) -> bool:
    return any([
        truthy(meta.get("ready_for_publish")),
        meta.get("gate_status", "").lower() == "ready",
        meta.get("publish_gate", "").lower() == "ready",
        meta.get("wp_status", "").lower() == "publish",
    ])


def main() -> int:
    if not DRAFTS.exists():
        print("content_gate: no drafts directory found", file=sys.stderr)
        return 1

    checked = fails = blocked = 0
    for path in sorted(DRAFTS.rglob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if not meta or not ready_candidate(meta):
            blocked += 1
            continue

        checked += 1
        problems: list[str] = []
        if meta.get("gate_status", "").lower() != "ready":
            problems.append("gate_status is not ready")
        if meta.get("publish_gate", "").lower() != "ready":
            problems.append("publish_gate is not ready")
        if truthy(meta.get("needs_verification")):
            problems.append("needs_verification=true while ready")

        scan = body
        for ok in ALLOWED:
            scan = scan.replace(ok, "")
        for marker in FORBIDDEN:
            if marker.lower() in scan.lower():
                problems.append(f"body marker present: {marker}")

        for tgt in LINK.findall(body):
            if tgt.strip() in ("", "#"):
                problems.append("empty markdown link")
                break

        if problems:
            fails += 1
            print(f"FAIL {path.relative_to(ROOT)}")
            for p in problems:
                print(f"  - {p}")

    print(f"content_gate: checked={checked} fails={fails} blocked={blocked}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
