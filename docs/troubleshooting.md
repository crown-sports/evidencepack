# Debug the first pack

Start with `python -m examples.quickstart` from the source checkout. It calls no
model and uses a temporary vault. For your own tool, keep the vault path, tenant,
session and receipt in host state; do not ask the model to choose them.

## A budget can fit the envelope but no excerpt

With the default counter, the budget is UTF-8 bytes of the entire JSON pack.
`BudgetTooSmall.required` is the size needed for the representation that failed;
for `pack()` it may only describe the empty envelope. It does not promise that
any excerpt fits. Check `pack.excerpts` before indexing it or sending it to a model.

This complete example works in v0.2.0 and later:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from evidencepack import EvidenceService, Scope, SQLiteRepository

with TemporaryDirectory() as directory:
    service = EvidenceService(
        SQLiteRepository(Path(directory) / "vault.sqlite"), Scope("local", "first-run")
    )
    artifact = service.capture("probe", "INFO starting\nERROR connection refused port=8080\n")
    small = service.pack("connection refused", [artifact.id], budget=200)
    print("Selected:", len(small.excerpts), "omitted:", small.omitted)
    service.release(small.receipt)
    pack = service.read(artifact.id, "L2-L2", budget=512)
    citation = pack.excerpts[0].citation
    print(service.verify(pack.receipt, citation, "port=8080"))
    print(service.verify(pack.receipt, citation, "port=9999"))
    service.release(pack.receipt)
    print("After release:", service.verify(pack.receipt, citation, "port=8080"))
    service.delete(artifact.id)
    print("After deletion:", service.verify(pack.receipt, citation, "port=8080"))
```

The 200-byte pack is empty. The 512-byte reread exposes the requested line.
Only increase a budget within the host's allowance; otherwise request a smaller
complete line range or deeper JSON pointer. An empty pack can also mean no units
matched the query. Inspect the captured source and choose a relevant query or locator.

## A quote or receipt is rejected

| Result | Next step |
| --- | --- |
| `quote_mismatch` | Copy an exact substring from an exposed excerpt. Do not normalize or rewrite a port, sign or whitespace. |
| `unknown_receipt` | Check the host's vault, tenant/session and receipt. A receipt from another scope is unavailable. |
| `not_exposed` | Use a citation from that exact pack, or reread the source and keep the new receipt. |
| `artifact_deleted` | Recapture available original evidence, then make a new pack and check the answer again. Do not accept the stale verdict. |

Receipts have no time-based expiry. `release()` removes a retention pin; the quote
still verifies until its evidence is deleted. Collection or forced deletion can
invalidate it. Check before releasing/collecting evidence needed by an answer.
`verify()` checks one quote; use `verify_answer()` for all submitted structured claims.

## The vault cannot be opened

`--vault` names a database **file**, such as `.evidencepack/vault.sqlite`, not a
directory. A non-SQLite file is not a valid vault. Preserve it and choose the
correct database or a new filename. Since v0.2.1, directory and SQLite failures return
structured errors with exit `2`; v0.2.0 may show a Python traceback for these failures.
Quote rejection exits `1`, while valid verification exits `0`.
