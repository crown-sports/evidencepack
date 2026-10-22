"""Run a complete answer gate without a model or persistent private data."""

import json
import tempfile
from pathlib import Path

from evidencepack import EvidenceService, Scope, SQLiteRepository

with tempfile.TemporaryDirectory() as directory:
    service = EvidenceService(
        SQLiteRepository(Path(directory) / "vault.sqlite"), Scope("demo", "answer")
    )
    artifact = service.capture("probe", "ERROR connection refused\n")
    pack = service.pack("connection refused", [artifact.id], budget=2048)
    claims = [
        {
            "id": "failure",
            "text": "The probe failed",
            "citations": [{"citation": pack.excerpts[0].citation, "quote": "connection refused"}],
        }
    ]
    print(json.dumps(service.verify_answer(pack.receipt, claims), indent=2))
    claims.append({"id": "unsupported", "text": "The service recovered", "citations": []})
    print(json.dumps(service.verify_answer(pack.receipt, claims), indent=2))
