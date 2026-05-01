from datetime import UTC, datetime, timedelta

import pytest

from cortex_memory_os.contracts import EvidenceRecord, RetentionPolicy
from cortex_memory_os.evidence_vault import (
    EvidenceVault,
    NoopDevCipher,
    RAW_EVIDENCE_EXPIRY_HARDENING_POLICY_REF,
    VaultRuntimeMode,
    assess_vault_cipher,
)
from cortex_memory_os.fixtures import load_json


def _evidence(**updates) -> EvidenceRecord:
    payload = load_json("tests/fixtures/evidence_screen.json")
    payload.update(updates)
    return EvidenceRecord.model_validate(payload)


def test_vault_stores_reads_and_checksums_raw_payload(tmp_path):
    vault = EvidenceVault(tmp_path)
    evidence = _evidence(evidence_id="ev_store_read")
    payload = b"synthetic screenshot bytes"

    metadata = vault.store(evidence, payload)

    assert metadata.raw_ref == "vault://evidence/ev_store_read"
    assert metadata.sha256
    assert metadata.byte_count == len(payload)
    assert metadata.retention_policy == RetentionPolicy.DELETE_RAW_AFTER_6H
    assert vault.read_raw("ev_store_read", now=evidence.timestamp) == payload


def test_vault_expires_raw_payload_but_keeps_metadata(tmp_path):
    vault = EvidenceVault(tmp_path)
    created_at = datetime(2026, 4, 27, 12, 0, tzinfo=UTC)
    evidence = _evidence(
        evidence_id="ev_expire",
        timestamp=created_at.isoformat(),
        retention_policy=RetentionPolicy.DELETE_RAW_AFTER_10M.value,
    )

    vault.store(evidence, b"short-lived raw bytes", now=created_at)
    expired = vault.expire(created_at + timedelta(minutes=11))
    metadata = vault.get_metadata("ev_expire")

    assert expired == ["ev_expire"]
    assert metadata is not None
    assert metadata.raw_ref is None
    assert metadata.blob_path is None
    assert metadata.raw_deleted_at is not None
    assert vault.read_raw("ev_expire", now=created_at + timedelta(minutes=11)) is None


def test_vault_expiry_receipt_survives_restart_without_raw_content(tmp_path):
    created_at = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    evidence = _evidence(
        evidence_id="ev_restart_expire",
        timestamp=created_at.isoformat(),
        retention_policy=RetentionPolicy.DELETE_RAW_AFTER_10M.value,
    )

    EvidenceVault(tmp_path).store(evidence, b"restart-expiring raw bytes", now=created_at)
    restarted = EvidenceVault(tmp_path)
    receipts = restarted.expire_with_receipts(
        created_at + timedelta(minutes=11),
        survived_restart=True,
    )
    metadata = restarted.get_metadata("ev_restart_expire")

    assert len(receipts) == 1
    receipt = receipts[0]
    assert receipt.evidence_id == "ev_restart_expire"
    assert receipt.raw_deleted is True
    assert receipt.metadata_retained is True
    assert receipt.survived_restart is True
    assert receipt.raw_ref_removed is True
    assert receipt.blob_removed is True
    assert receipt.content_redacted is True
    assert RAW_EVIDENCE_EXPIRY_HARDENING_POLICY_REF in receipt.policy_refs
    assert metadata is not None
    assert metadata.raw_ref is None
    assert metadata.blob_path is None
    assert restarted.read_raw("ev_restart_expire") is None


def test_discard_policy_never_writes_raw_blob(tmp_path):
    vault = EvidenceVault(tmp_path)
    created_at = datetime(2026, 4, 27, 12, 0, tzinfo=UTC)
    evidence = _evidence(
        evidence_id="ev_discard",
        raw_ref=None,
        retention_policy=RetentionPolicy.DISCARD.value,
        eligible_for_memory=False,
    )

    metadata = vault.store(evidence, b"discard me", now=created_at)

    assert metadata.raw_ref is None
    assert metadata.raw_deleted_at == created_at
    assert list((tmp_path / "blobs").glob("*")) == []
    assert vault.read_raw("ev_discard") is None


class _ToyAuthenticatedCipher:
    name = "toy-aead-test"
    authenticated_encryption = True

    def seal(self, plaintext: bytes) -> bytes:
        return b"sealed:" + plaintext[::-1]

    def open(self, ciphertext: bytes) -> bytes:
        assert ciphertext.startswith(b"sealed:")
        return ciphertext.removeprefix(b"sealed:")[::-1]


def test_noop_cipher_is_rejected_in_production(tmp_path):
    decision = assess_vault_cipher(NoopDevCipher(), VaultRuntimeMode.PRODUCTION)

    assert decision.allowed is False
    assert decision.reason == "noop_dev_cipher_forbidden_in_production"
    with pytest.raises(ValueError, match="noop_dev_cipher_forbidden_in_production"):
        EvidenceVault(tmp_path, mode=VaultRuntimeMode.PRODUCTION)


def test_authenticated_cipher_boundary_works_in_production(tmp_path):
    cipher = _ToyAuthenticatedCipher()
    vault = EvidenceVault(tmp_path, cipher=cipher, mode=VaultRuntimeMode.PRODUCTION)
    evidence = _evidence(evidence_id="ev_prod_cipher")
    payload = b"raw bytes behind production cipher boundary"

    metadata = vault.store(evidence, payload)
    sealed = (tmp_path / metadata.blob_path).read_bytes()

    assert vault.cipher_decision.allowed is True
    assert vault.cipher_decision.reason == "production_cipher_boundary_satisfied"
    assert metadata.cipher == cipher.name
    assert sealed != payload
    assert vault.read_raw("ev_prod_cipher", now=evidence.timestamp) == payload
