# Budgeting and checking tool evidence

## What counts toward the budget

The allowance covers the serialized pack, including citation IDs, locations and
metadata. The default counter measures UTF-8 bytes. Token counters are optional;
use the tokenizer for the model receiving the pack. Oversized units may be
omitted, so inspect the selected excerpts before relying on a diagnosis.
[Selection behavior and tests](../tests/test_selection.py).

The quickstart supplies **55,945 bytes** of generated logs and configuration.
Its actual pack is **1,177 bytes** under a 2,000-byte allowance. The screenshot
shows the configuration excerpt and two verification results, not a separate GUI.
[Saved API output](assets/readme-demo.json) · [Recreate the figure](screenshots.md).

## Keep the receipt on the host

A receipt binds citations to the pack actually exposed to the model. Store it in
trusted host state, submit the entire structured answer to `verify_answer`, and
reject the answer when any required citation fails. Merely checking one quote
does not check the rest of the answer. An exact quote can still support a bad
conclusion; semantic entailment is outside this check.
[Integration and middleware](integration.md) · [Answer tests](../tests/test_answers.py).

## Rereads and retention

Capture preserves the full source. A locator can request another excerpt when
selection misses the needed lines. Release receipts when the host no longer
needs them, then collect eligible data under the documented retention rules.
Scope names separate records; they do not authenticate callers. Keep the SQLite
vault outside the agent's writable workspace. Deletion is not secure erasure.
[Storage and integrity](design.md) · [Integrity tests](../tests/test_integrity.py).

The published local fault experiments compare selection methods with the same
inputs and model. BM25 matches EvidencePack's aggregate model result; the
implementation adds explicit budgets, receipts and verifiable quotes.
[Full results, failures and reproduction](results.md).

The library examples work in v0.2.0. The new figure and its renderer are on main.
