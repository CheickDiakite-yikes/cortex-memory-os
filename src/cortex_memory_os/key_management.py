"""Production key lifecycle contract for Cortex memory storage."""

from __future__ import annotations

import argparse
import json
from enum import Enum

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.evidence_vault import EVIDENCE_VAULT_ENCRYPTION_POLICY_REF
from cortex_memory_os.encrypted_graph_index import UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF
from cortex_memory_os.memory_encryption import MEMORY_ENCRYPTION_DEFAULT_POLICY_REF

KEY_MANAGEMENT_PLAN_ID = "KEY-MANAGEMENT-PLAN-001"
KEY_MANAGEMENT_PLAN_POLICY_REF = "policy_key_management_plan_v1"


class KeyMaterialClass(str, Enum):
    MEMORY_PAYLOAD = "memory_payload"
    GRAPH_EDGE_PAYLOAD = "graph_edge_payload"
    HMAC_INDEX = "hmac_index"
    EVIDENCE_BLOB = "evidence_blob"


class KeyLifecycleBoundary(StrictModel):
    key_class: KeyMaterialClass
    key_id_ref: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    storage_backend: str = Field(min_length=1)
    wrapped_by: str = Field(min_length=1)
    rotation_days: int = Field(ge=1, le=366)
    production_required: bool = True
    key_material_included: bool = False
    allowed_effects: list[str] = Field(min_length=1)
    blocked_effects: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def keep_boundary_secret_free(self) -> KeyLifecycleBoundary:
        backend = self.storage_backend.lower()
        wrapped_by = self.wrapped_by.lower()
        if self.key_material_included:
            raise ValueError("key lifecycle boundaries cannot include raw key material")
        if any(marker in backend for marker in ["inline", ".env", "plaintext", "noop"]):
            raise ValueError("production key storage cannot use inline/env/plaintext/noop backends")
        if "keychain" not in backend and "hsm" not in backend and "kms" not in backend:
            raise ValueError("production key storage must use an OS or managed key boundary")
        if "keychain" not in wrapped_by and "hsm" not in wrapped_by and "kms" not in wrapped_by:
            raise ValueError("key wrapping must name an OS or managed key boundary")
        required_blocked = {
            "store_raw_key_material",
            "commit_key_material",
            "reuse_key_across_material_classes",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"key boundary missing blocked effects: {missing}")
        return self


class KeyManagementStep(StrictModel):
    step_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    proof: str = Field(min_length=1)
    required_for: list[KeyMaterialClass] = Field(min_length=1)
    allowed_effects: list[str] = Field(min_length=1)
    blocked_effects: list[str] = Field(default_factory=list)


class KeyManagementPlan(StrictModel):
    plan_id: str = KEY_MANAGEMENT_PLAN_ID
    runtime_boundary: str = "local_engine_with_native_keychain"
    production_allows_noop_cipher: bool = False
    local_dev_uses_test_keys: bool = True
    raw_key_material_included: bool = False
    default_rotation_days: int = Field(default=90, ge=1, le=366)
    key_boundaries: list[KeyLifecycleBoundary] = Field(min_length=4)
    lifecycle_steps: list[KeyManagementStep] = Field(min_length=5)
    recovery_controls: list[str] = Field(min_length=2)
    deletion_controls: list[str] = Field(min_length=2)
    audit_events: list[str] = Field(min_length=5)
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            KEY_MANAGEMENT_PLAN_POLICY_REF,
            MEMORY_ENCRYPTION_DEFAULT_POLICY_REF,
            UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF,
            EVIDENCE_VAULT_ENCRYPTION_POLICY_REF,
        ]
    )

    @model_validator(mode="after")
    def keep_plan_production_safe(self) -> KeyManagementPlan:
        if KEY_MANAGEMENT_PLAN_POLICY_REF not in self.policy_refs:
            raise ValueError("key management plan requires policy ref")
        if self.raw_key_material_included:
            raise ValueError("key management plan cannot include raw key material")
        if self.production_allows_noop_cipher:
            raise ValueError("production key plan cannot allow noop ciphers")
        required_classes = set(KeyMaterialClass)
        actual_classes = {boundary.key_class for boundary in self.key_boundaries}
        if missing := sorted(item.value for item in required_classes.difference(actual_classes)):
            raise ValueError(f"key management plan missing material classes: {missing}")
        if len(actual_classes) != len(self.key_boundaries):
            raise ValueError("key management plan requires one boundary per key class")
        step_ids = {step.step_id for step in self.lifecycle_steps}
        required_steps = {
            "generate_wrapped_key",
            "activate_key_version",
            "rotate_key_version",
            "revoke_key_version",
            "delete_key_version",
        }
        if missing := sorted(required_steps.difference(step_ids)):
            raise ValueError(f"key management plan missing lifecycle steps: {missing}")
        required_audits = {
            "key.created",
            "key.activated",
            "key.rotated",
            "key.revoked",
            "key.deleted",
        }
        if missing := sorted(required_audits.difference(self.audit_events)):
            raise ValueError(f"key management plan missing audit events: {missing}")
        return self


class KeyManagementPlanSmokeResult(StrictModel):
    proof_id: str = KEY_MANAGEMENT_PLAN_ID
    policy_ref: str = KEY_MANAGEMENT_PLAN_POLICY_REF
    passed: bool
    key_class_count: int = Field(ge=0)
    lifecycle_step_count: int = Field(ge=0)
    raw_key_material_included: bool
    production_allows_noop_cipher: bool
    mandatory_key_classes_present: bool
    rotation_and_deletion_present: bool
    audit_events_present: bool
    key_material_redacted: bool
    missing_controls: list[str] = Field(default_factory=list)


def build_default_key_management_plan() -> KeyManagementPlan:
    """Return the production key lifecycle target without any key material."""

    boundary_defaults = {
        "storage_backend": "macos_keychain_secure_enclave_when_available",
        "wrapped_by": "macos_keychain_application_password_item",
        "rotation_days": 90,
        "allowed_effects": [
            "store_wrapped_key_metadata",
            "seal_payloads_with_active_key_version",
            "audit_key_version_use",
        ],
        "blocked_effects": [
            "store_raw_key_material",
            "commit_key_material",
            "reuse_key_across_material_classes",
            "export_unwrapped_key",
        ],
    }
    key_boundaries = [
        KeyLifecycleBoundary(
            key_class=KeyMaterialClass.MEMORY_PAYLOAD,
            key_id_ref="keyref_memory_payload_active",
            purpose="Seal durable MemoryRecord payload JSON.",
            **boundary_defaults,
        ),
        KeyLifecycleBoundary(
            key_class=KeyMaterialClass.GRAPH_EDGE_PAYLOAD,
            key_id_ref="keyref_graph_edge_payload_active",
            purpose="Seal temporal graph edge payload JSON.",
            **boundary_defaults,
        ),
        KeyLifecycleBoundary(
            key_class=KeyMaterialClass.HMAC_INDEX,
            key_id_ref="keyref_hmac_index_terms_active",
            purpose="Derive redacted token digests for memory and graph lookup.",
            **boundary_defaults,
        ),
        KeyLifecycleBoundary(
            key_class=KeyMaterialClass.EVIDENCE_BLOB,
            key_id_ref="keyref_evidence_blob_active",
            purpose="Seal short-retention raw evidence blobs before expiry.",
            **boundary_defaults,
        ),
    ]
    all_classes = list(KeyMaterialClass)
    steps = [
        KeyManagementStep(
            step_id="generate_wrapped_key",
            label="Generate wrapped key version",
            proof="New key material is generated inside the native key boundary and only a key ref is returned.",
            required_for=all_classes,
            allowed_effects=["create_key_ref", "write_key_audit"],
            blocked_effects=["return_unwrapped_key_material", "write_key_to_env_file"],
        ),
        KeyManagementStep(
            step_id="activate_key_version",
            label="Activate key version",
            proof="New writes use the active key ref while old versions remain readable until rotation closes.",
            required_for=all_classes,
            allowed_effects=["mark_active_key_ref", "seal_new_payloads"],
            blocked_effects=["rewrite_without_audit"],
        ),
        KeyManagementStep(
            step_id="rotate_key_version",
            label="Rotate key version",
            proof="Rotation creates a new key ref, reseals eligible payloads, and records old/new refs.",
            required_for=all_classes,
            allowed_effects=["reseal_payloads", "write_rotation_audit"],
            blocked_effects=["reuse_old_index_key", "drop_unmigrated_payloads"],
        ),
        KeyManagementStep(
            step_id="revoke_key_version",
            label="Revoke key version",
            proof="Revoked keys stop new writes and require explicit recovery or delete flow.",
            required_for=all_classes,
            allowed_effects=["block_new_writes", "write_revocation_audit"],
            blocked_effects=["silent_reactivation"],
        ),
        KeyManagementStep(
            step_id="delete_key_version",
            label="Delete key version",
            proof="Deleting a key version makes associated unrecovered payloads cryptographically unreadable.",
            required_for=all_classes,
            allowed_effects=["destroy_wrapped_key", "write_delete_audit"],
            blocked_effects=["retain_unwrapped_key_backup", "skip_user_visible_receipt"],
        ),
    ]
    return KeyManagementPlan(
        key_boundaries=key_boundaries,
        lifecycle_steps=steps,
        recovery_controls=[
            "recovery requires user-visible local backup policy",
            "payload recovery never exports unwrapped key material",
        ],
        deletion_controls=[
            "delete key ref after retention and user-confirmed forget flow",
            "retain redacted tombstone audit without decryptable payload",
        ],
        audit_events=[
            "key.created",
            "key.activated",
            "key.rotated",
            "key.revoked",
            "key.deleted",
            "payload.resealed",
        ],
    )


def run_key_management_plan_smoke() -> KeyManagementPlanSmokeResult:
    plan = build_default_key_management_plan()
    payload = plan.model_dump_json()
    prohibited_markers = [
        "OPENAI_API_KEY=",
        "CORTEX_FAKE_TOKEN",
        "sk-",
        "-----BEGIN",
        "raw_key_bytes",
    ]
    missing_controls: list[str] = []
    mandatory_key_classes_present = {boundary.key_class for boundary in plan.key_boundaries} == set(
        KeyMaterialClass
    )
    rotation_and_deletion_present = {"rotate_key_version", "delete_key_version"}.issubset(
        {step.step_id for step in plan.lifecycle_steps}
    )
    audit_events_present = {"key.created", "key.rotated", "key.deleted"}.issubset(
        set(plan.audit_events)
    )
    key_material_redacted = not any(marker in payload for marker in prohibited_markers)
    checks = {
        "mandatory_key_classes_present": mandatory_key_classes_present,
        "rotation_and_deletion_present": rotation_and_deletion_present,
        "audit_events_present": audit_events_present,
        "key_material_redacted": key_material_redacted,
        "raw_key_material_absent": not plan.raw_key_material_included,
        "noop_cipher_blocked": not plan.production_allows_noop_cipher,
    }
    missing_controls.extend(name for name, passed in checks.items() if not passed)
    return KeyManagementPlanSmokeResult(
        passed=not missing_controls,
        key_class_count=len(plan.key_boundaries),
        lifecycle_step_count=len(plan.lifecycle_steps),
        raw_key_material_included=plan.raw_key_material_included,
        production_allows_noop_cipher=plan.production_allows_noop_cipher,
        mandatory_key_classes_present=mandatory_key_classes_present,
        rotation_and_deletion_present=rotation_and_deletion_present,
        audit_events_present=audit_events_present,
        key_material_redacted=key_material_redacted,
        missing_controls=missing_controls,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run_key_management_plan_smoke()
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        status = "passed" if result.passed else "failed"
        print(
            f"{KEY_MANAGEMENT_PLAN_ID}: {status}; "
            f"classes={result.key_class_count}; steps={result.lifecycle_step_count}; "
            f"missing={len(result.missing_controls)}"
        )
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
