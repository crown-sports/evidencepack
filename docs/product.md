# Product fit and evidence

EvidencePack serves developers who already have tool-using agents. Its narrow
job is to preserve tool output, fit selected evidence into an explicit allowance,
and let the trusted host reject unsupported submitted quotations. It does not
produce a diagnosis or establish that a supported quote entails a claim.
This target use is inferred from the workflow, not validated by user interviews.

## What is implemented

| Advantage over passing truncated text or saving an unlinked file | Evidence | Boundary |
| --- | --- | --- |
| Count the serialized evidence, including locators and metadata | [Selection tests](../tests/test_selection.py), [paired experiments](results.md) | Lexical retrieval can miss synonyms or omit large units |
| Bind quotations to the exact pack exposed to the host | [Integrity tests](../tests/test_integrity.py), [answer tests](../tests/test_answers.py) | The host must bind the full accepted answer; semantic truth is unchecked |
| Preserve capture references through scoped storage and collection | [Integrity tests](../tests/test_integrity.py), [integration contract](integration.md) | Scope is not authentication and SQLite deletion is not secure erasure |

The measured comparisons are selection-policy experiments on generated and
local-process fixtures. They do not show superiority to complete agent platforms;
BM25 matches the published aggregate model results. No customer outcome or
universal accuracy claim follows from those experiments.

## What could accumulate

The code and established retrieval methods are reproducible, not a demonstrated
moat. Priorities are: (1) adapters with tested full-answer binding in real hosts,
(2) consented failure fixtures covering retrieval misses and misleading-but-exact
quotes, (3) evaluation across actual tool schemas and tokenizer budgets.
Stable integration contracts and a maintained rejection corpus could become
valuable over time. Neither broad host adoption nor that external corpus exists
in the published evidence today.

Start with the [offline examples](../README.md#try-it); then wrap one tool with
[middleware](../examples/tool_middleware.py). Verify the rejection path before
letting an answer affect actions. Keep action authorization separate.

## Version availability

This document is new on main; the demonstrated APIs and examples already exist
in v0.2.0. Existing release archives are unchanged.
