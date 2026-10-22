"""Application facade that binds trusted scope to storage and selection policy."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import uuid4

from .answers import validate_claims
from .counters import ByteCounter
from .domain import (
    Artifact,
    BudgetTooSmall,
    Counter,
    MediaType,
    Pack,
    Ranker,
    Repository,
    Scope,
    Verdict,
)
from .selection import BudgetPacker, LexicalRanker


class EvidenceService:
    """Compose replaceable ports once, keeping scope out of model-supplied arguments."""

    def __init__(
        self,
        repository: Repository,
        scope: Scope,
        *,
        counter: Counter | None = None,
        ranker: Ranker | None = None,
    ) -> None:
        self.repository = repository
        self.scope = scope
        self.counter = counter or ByteCounter()
        self.packer = BudgetPacker(self.counter, ranker or LexicalRanker())

    def capture(self, source: str, text: str, *, media_type: MediaType = "text") -> Artifact:
        """Persist original textual output before building any model projection."""
        return self.repository.put(self.scope, source, text, media_type)

    def pack(self, query: str, artifact_ids: Sequence[str], *, budget: int = 4096) -> Pack:
        """Select complete evidence, enforce the allowance, then commit its receipt."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be nonblank")
        if not artifact_ids:
            raise ValueError("At least one artifact ID is required")
        units = self.repository.units(self.scope, tuple(artifact_ids))
        pack = self.packer.build(query, units, budget)
        self.repository.record(self.scope, pack)
        return pack

    def read(self, artifact_id: str, locator: str, *, budget: int = 4096) -> Pack:
        """Expose an exact line range or JSON record through a fresh bounded receipt."""
        if type(budget) is not int or budget < 1:
            raise ValueError("budget must be a positive integer")
        unit = self.repository.resolve(self.scope, artifact_id, locator)
        pack = Pack("p_" + uuid4().hex, (unit,), 0, self.counter.name)
        required = self.counter.count(pack.to_json())
        if required > budget:
            raise BudgetTooSmall(budget, required)
        self.repository.record(self.scope, pack)
        return pack

    def raw(self, artifact_id: str) -> Artifact:
        """Recover original output for the trusted host; this is deliberately unbudgeted."""
        return self.repository.get(self.scope, artifact_id)

    def verify(self, receipt: str, citation: str, quote: str) -> Verdict:
        """Check exact exposure provenance, leaving claim interpretation to the caller."""
        return self.repository.verify(self.scope, receipt, citation, quote)

    def verify_answer(self, receipt: str, claims: list[dict[str, Any]]) -> dict[str, Any]:
        """Gate all submitted claims against one host-selected receipt; not semantic truth."""
        if not isinstance(receipt, str) or not receipt.strip() or len(receipt) > 256:
            raise ValueError("receipt must be nonblank text of at most 256 characters")
        validated = validate_claims(claims)
        results = []
        for claim in validated:
            citations = []
            for item in claim["citations"]:
                verdict = self.verify(receipt, item["citation"], item["quote"])
                citations.append(
                    {"citation": item["citation"], "valid": verdict.valid, "reason": verdict.reason}
                )
            valid = bool(citations) and all(item["valid"] for item in citations)
            results.append(
                {
                    "id": claim["id"],
                    "valid": valid,
                    "reason": "verified_quotes"
                    if valid
                    else "uncited_claim"
                    if not citations
                    else "rejected_quote",
                    "citations": citations,
                }
            )
        return {
            "valid": all(item["valid"] for item in results),
            "receipt": receipt,
            "claims": results,
            "rejected_claims": sum(not item["valid"] for item in results),
            "limits": "Checks submitted quote provenance only, not semantic entailment "
            "or omitted prose. "
            "The host must bind this claim list to the entire answer it accepts.",
        }

    def release(self, receipt: str) -> None:
        """End the retention pin once the host no longer needs this receipt."""
        self.repository.release(self.scope, receipt)

    def delete(self, artifact_id: str, *, force: bool = False) -> None:
        """Delete scoped evidence, respecting live references unless explicitly forced."""
        self.repository.delete(self.scope, artifact_id, force=force)

    def collect(self, *, before: float) -> int:
        """Collect old unpinned artifacts while preserving explicit deletion history."""
        return self.repository.collect(self.scope, before)
