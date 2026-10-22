"""Bounded, structured answer contracts for checking every submitted quotation."""

from __future__ import annotations

import json
from typing import Any


def validate_claims(claims: Any) -> list[dict[str, Any]]:
    """Reject ambiguous schemas before performing any storage lookups."""
    if not isinstance(claims, list) or not 1 <= len(claims) <= 100:
        raise ValueError("An answer needs between 1 and 100 claims")
    seen = set()
    for claim in claims:
        if not isinstance(claim, dict) or set(claim) != {"id", "text", "citations"}:
            raise ValueError("Each claim must contain only id, text and citations")
        for name, limit in (("id", 128), ("text", 8192)):
            item = claim[name]
            if not isinstance(item, str) or not item.strip() or len(item) > limit:
                raise ValueError(
                    f"Claim {name} must be nonblank text of at most {limit} characters"
                )
        if claim["id"] in seen:
            raise ValueError("Claim IDs must be unique")
        seen.add(claim["id"])
        citations = claim["citations"]
        if not isinstance(citations, list) or len(citations) > 20:
            raise ValueError("A claim accepts at most 20 citations")
        for citation in citations:
            if not isinstance(citation, dict) or set(citation) != {"citation", "quote"}:
                raise ValueError("Each citation must contain only citation and quote")
            for name, limit in (("citation", 256), ("quote", 8192)):
                value = citation[name]
                if not isinstance(value, str) or not value.strip() or len(value) > limit:
                    raise ValueError(
                        f"Citation {name} must be nonblank text of at most {limit} characters"
                    )
    if len(json.dumps(claims, ensure_ascii=False).encode("utf-8")) > 1048576:
        raise ValueError("Answer claims must be at most 1 MiB")
    return claims


def load_claims(data: bytes) -> list[dict[str, Any]]:
    """Parse an answer file with duplicate-key rejection and a bounded size."""
    if len(data) > 1048576:
        raise ValueError("Answer files must be at most 1 MiB")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate answer key: {key}")
            result[key] = value
        return result

    return validate_claims(json.loads(data, object_pairs_hook=pairs))
