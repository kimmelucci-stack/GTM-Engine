"""Validate local Markdown references and reject superseded normative decisions."""

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OBSOLETE = (
    "Macro-fase proposta, dettaglio da definire",
    "Output obbligatorio; specifiche da definire",
    "Confine da decidere",
    "n8n opzionale",
    "proposte tecniche da confermare",
    "backend/worker e deploy rimangono da scegliere",
    "ancora da redigere dopo questa fase",
    "Scelta finale hosting",
    "formato e motore da definire",
    "fallback di verifica assistita manuale",
    "collocazione nella Development Roadmap ancora da fissare",
    "docs/EVOLUTION_BACKLOG.md",
)


def main() -> int:
    errors = []
    links = 0
    files = [ROOT / "README.md", ROOT / "AGENTS.md", *sorted((ROOT / "docs").rglob("*.md"))]
    for file in files:
        text = file.read_text(encoding="utf-8")
        normative = text.split("## Archivio storico", 1)[0]
        for phrase in OBSOLETE:
            if phrase.casefold() in normative.casefold():
                errors.append(f"{file.relative_to(ROOT)}: obsolete expression {phrase!r}")
        # Markdown file links, excluding external URLs and in-page anchors.
        refs = re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
        # Backticked explicit document paths or local document names.
        refs += re.findall(r"`([^`\n]+\.md)`", text)
        for ref in refs:
            ref = ref.strip("<>")
            parsed = urlsplit(ref)
            if parsed.scheme or not parsed.path:
                continue
            path = unquote(parsed.path)
            if any(c in path for c in "*[]|") or "..." in path:
                continue
            # Bare SCOPE.md is a naming convention outside a module folder.
            if path == "SCOPE.md" and not (file.parent / path).exists():
                continue
            candidate = ROOT / path if path.startswith("docs/") else file.parent / path
            if path in {"AGENTS.md", "README.md"} and not candidate.exists():
                candidate = ROOT / path
            links += 1
            if not candidate.exists():
                errors.append(f"{file.relative_to(ROOT)}: missing reference {ref}")
    if (ROOT / "docs" / "EVOLUTION_BACKLOG.md").exists():
        errors.append("Obsolete duplicate backlog still exists")
    for error in errors:
        print(error)
    print(f"Checked {len(files)} Markdown files and {links} local references; errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
