from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cortex_memory_os.key_management import KeyMaterialClass
from cortex_memory_os.keychain_key_adapter import (
    KEYCHAIN_KEY_ADAPTER_ID,
    KEYCHAIN_KEY_ADAPTER_POLICY_REF,
    KeychainKeyAdapterSmokeResult,
    build_keychain_key_refs,
    run_keychain_key_adapter_smoke,
)


NOW = datetime(2026, 5, 2, 16, 10, tzinfo=UTC)


def test_keychain_key_adapter_returns_metadata_refs_for_each_key_class():
    refs = build_keychain_key_refs(backend_available=True)

    assert {ref.key_class for ref in refs} == set(KeyMaterialClass)
    assert all(ref.provider == "macos_keychain" for ref in refs)
    assert all(ref.backend_available for ref in refs)
    assert all(ref.wrapped_key_metadata_only for ref in refs)
    assert all(not ref.material_returned for ref in refs)


def test_keychain_key_adapter_smoke_is_read_only_and_secret_free():
    result = run_keychain_key_adapter_smoke(
        now=NOW,
        platform_system="Darwin",
        security_cli_detected=True,
    )
    payload = result.model_dump_json()

    assert result.proof_id == KEYCHAIN_KEY_ADAPTER_ID
    assert result.policy_ref == KEYCHAIN_KEY_ADAPTER_POLICY_REF
    assert result.passed is True
    assert result.native_backend_detected is True
    assert result.key_ref_count == len(KeyMaterialClass)
    assert result.read_only_probe_used is True
    assert result.keychain_write_attempted is False
    assert result.key_material_returned is False
    assert result.env_secret_used is False
    assert result.production_noop_allowed is False
    assert "create_keychain_item" in result.blocked_effects
    assert "read_keychain_secret" in result.blocked_effects
    assert "OPENAI_API_KEY=" not in payload
    assert "sk-" not in payload


def test_keychain_key_adapter_rejects_write_or_material_exposure():
    result = run_keychain_key_adapter_smoke(
        now=NOW,
        platform_system="Darwin",
        security_cli_detected=True,
    )

    with pytest.raises(ValidationError, match="cannot write"):
        KeychainKeyAdapterSmokeResult.model_validate(
            result.model_dump() | {"keychain_write_attempted": True}
        )

    with pytest.raises(ValidationError, match="cannot expose"):
        KeychainKeyAdapterSmokeResult.model_validate(
            result.model_dump() | {"key_material_returned": True}
        )
