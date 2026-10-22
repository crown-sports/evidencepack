"""Host-side all-claim gates preserve quote, scope, lifetime and receipt boundaries."""

import json
import subprocess
import sys

import pytest

from evidencepack import EvidenceService, Scope
from evidencepack.answers import load_claims


def claim(citation, quote="connection refused", identity="failure"):
    return {
        "id": identity,
        "text": "The service refused the connection",
        "citations": [{"citation": citation, "quote": quote}],
    }


def setup_pack(evidence):
    source = evidence.capture("probe", "ERROR connection refused\n")
    return source, evidence.pack("connection", [source.id], budget=2048)


def test_all_claims_must_pass_and_uncited_claim_is_not_vacuously_true(evidence):
    _, pack = setup_pack(evidence)
    claims = [
        claim(pack.excerpts[0].citation),
        {"id": "other", "text": "It recovered", "citations": []},
    ]
    result = evidence.verify_answer(pack.receipt, claims)
    assert not result["valid"] and result["rejected_claims"] == 1
    assert result["claims"][1]["reason"] == "uncited_claim"
    assert evidence.verify_answer(pack.receipt, claims[:1])["valid"]


def test_wrong_receipt_cross_scope_and_forged_quote_fail(evidence, repository):
    _, pack = setup_pack(evidence)
    second = evidence.capture("elsewhere", "ERROR connection refused\n")
    elsewhere = evidence.pack("connection", [second.id], budget=2048)
    submitted = [claim(pack.excerpts[0].citation)]
    assert not evidence.verify_answer(elsewhere.receipt, submitted)["valid"]
    assert not evidence.verify_answer(pack.receipt, [claim(pack.excerpts[0].citation, "healthy")])[
        "valid"
    ]
    other = EvidenceService(repository, Scope("another", "session"))
    assert not other.verify_answer(pack.receipt, submitted)["valid"]
    assert not evidence.verify_answer("missing", submitted)["valid"]


def test_every_quote_checked_and_deletion_invalidates_answer(evidence):
    source, pack = setup_pack(evidence)
    submitted = [claim(pack.excerpts[0].citation)]
    submitted[0]["citations"].append({"citation": "invented", "quote": "connection refused"})
    assert not evidence.verify_answer(pack.receipt, submitted)["valid"]
    evidence.delete(source.id, force=True)
    assert not evidence.verify_answer(pack.receipt, submitted)["valid"]


@pytest.mark.parametrize(
    "claims",
    [
        [],
        None,
        [{}],
        [claim("c"), claim("c")],
        [{"id": "x", "text": "claim", "citations": [{"citation": "c", "quote": " "}]}],
        [{"id": "x", "text": "claim", "citations": [], "unexpected": True}],
    ],
)
def test_ambiguous_or_unbounded_contract_rejected(evidence, claims):
    with pytest.raises(ValueError):
        evidence.verify_answer("receipt", claims)


def test_duplicate_json_keys_and_oversized_input_are_rejected():
    with pytest.raises(ValueError, match="Duplicate"):
        load_claims(b'[{"id":"one","id":"two","text":"x","citations":[]}]')
    with pytest.raises(ValueError, match="1 MiB"):
        load_claims(b" " * 1048577)


def test_cli_returns_machine_readable_rejections(evidence, tmp_path):
    _, pack = setup_pack(evidence)
    answer = tmp_path / "answer.json"
    answer.write_text(json.dumps([claim(pack.excerpts[0].citation, "invented")]))
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencepack.cli",
            "--vault",
            str(evidence.repository.path),
            "--tenant",
            "tenant-a",
            "--session",
            "session-a",
            "verify-answer",
            pack.receipt,
            str(answer),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1, result.stderr
    assert json.loads(result.stdout)["rejected_claims"] == 1
