"""Render actual quickstart API output as a documentation figure (not product UI)."""

from __future__ import annotations

import json
from dataclasses import asdict
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory

from evidencepack import EvidenceService, Scope, SQLiteRepository


def main() -> None:
    output = Path(__file__).parent / "assets"
    noise = "INFO checkout /ping status=200\n" * 900
    sources = {
        "application-log": noise
        + "ERROR checkout upstream connection refused status=502\n"
        + noise,
        "configuration": "CONFIG upstream_port=8080 health_path=/health\n",
        "backend-runtime": "LISTENER bound_port=8081 health_path=/health\n",
    }
    query = "Diagnose checkout HTTP 502. Compare upstream_port to backend bound_port."
    with TemporaryDirectory(prefix="evidencepack-figure-") as directory:
        service = EvidenceService(
            SQLiteRepository(Path(directory) / "vault.sqlite"), Scope("demo", "incident-1")
        )
        artifacts = [service.capture(source, text) for source, text in sources.items()]
        pack = service.pack(query, [item.id for item in artifacts], budget=2000)
        configuration = next(item for item in pack.excerpts if item.source == "configuration")
        verdicts = [
            {"quote": quote, **asdict(service.verify(pack.receipt, configuration.citation, quote))}
            for quote in ("upstream_port=8080", "upstream_port=9999")
        ]
        result = {
            "input_bytes": sum(len(text.encode()) for text in sources.values()),
            "budget_bytes": 2000,
            "serialized_bytes": len(pack.to_json().encode()),
            "pack": json.loads(pack.to_json()),
            "verdicts": verdicts,
        }
        service.release(pack.receipt)
    output.mkdir(exist_ok=True)
    (output / "readme-demo.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    cards = "".join(
        f'<div class="quote {"pass" if item["valid"] else "fail"}">'
        f"<b>{'ACCEPT' if item['valid'] else 'REJECT'}</b>"
        f"<code>{escape(item['quote'])}</code><span>{escape(item['reason'])}</span></div>"
        for item in verdicts
    )
    html = (Path(__file__).parent / "example-template.html").read_text(encoding="utf-8")
    html = (
        html.replace("INPUT_BYTES", f"{result['input_bytes']:,}")
        .replace("PACK_BYTES", f"{result['serialized_bytes']:,}")
        .replace("CARDS", cards)
    )
    source_lines = "<br>".join(
        f"{escape(name)} · {len(value.splitlines()):,} "
        f"{'line' if len(value.splitlines()) == 1 else 'lines'}"
        for name, value in sources.items()
    )
    html = html.replace("SOURCE_LINES", source_lines).replace(
        "CONFIGURATION_TEXT", escape(configuration.text.strip())
    )
    (output / "readme-demo.html").write_text(html, encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "pack"}))


if __name__ == "__main__":
    main()
