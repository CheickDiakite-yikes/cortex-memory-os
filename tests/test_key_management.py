import pytest
from pydantic import ValidationError

from cortex_memory_os.key_management import (
    KEY_MANAGEMENT_PLAN_ID,
    KEY_MANAGEMENT_PLAN_POLICY_REF,
    KeyLifecycleBoundary,
    KeyMaterialClass,
    build_default_key_management_plan,
    run_key_management_plan_smoke,
)


def test_default_key_management_plan_covers_all_material_classes_without_keys():
    plan = build_default_key_management_plan()
    payload = plan.model_dump_json()

    assert plan.plan_id == KEY_MANAGEMENT_PLAN_ID
    assert KEY_MANAGEMENT_PLAN_POLICY_REF in plan.policy_refs
    assert {boundary.key_class for boundary in plan.key_boundaries} == set(KeyMaterialClass)
    assert not plan.raw_key_material_included
    assert not plan.production_allows_noop_cipher
    assert {"key.created", "key.rotated", "key.deleted"}.issubset(plan.audit_events)
    assert "OPENAI_API_KEY=" not in payload
    assert "sk-" not in payload
    assert "raw_key_bytes" not in payload


def test_key_boundary_rejects_inline_or_noop_key_storage():
    with pytest.raises(ValidationError, match="inline/env/plaintext/noop"):
        KeyLifecycleBoundary(
            key_class=KeyMaterialClass.MEMORY_PAYLOAD,
            key_id_ref="keyref_bad",
            purpose="bad production key storage",
            storage_backend="inline .env plaintext",
            wrapped_by="macos_keychain",
            rotation_days=90,
            allowed_effects=["store_wrapped_key_metadata"],
            blocked_effects=[
                "store_raw_key_material",
                "commit_key_material",
                "reuse_key_across_material_classes",
            ],
        )


def test_key_management_plan_smoke_passes():
    result = run_key_management_plan_smoke()

    assert result.passed
    assert result.proof_id == KEY_MANAGEMENT_PLAN_ID
    assert result.key_class_count == 4
    assert result.lifecycle_step_count >= 5
    assert result.mandatory_key_classes_present
    assert result.rotation_and_deletion_present
    assert result.audit_events_present
    assert result.key_material_redacted
    assert result.missing_controls == []
