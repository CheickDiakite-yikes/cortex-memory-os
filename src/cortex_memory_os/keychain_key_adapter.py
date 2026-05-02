"""macOS Keychain-backed key provider contract smoke."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
from datetime import UTC, datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.key_management import (
    KEY_MANAGEMENT_PLAN_POLICY_REF,
    KeyManagementPlan,
    KeyMaterialClass,
    build_default_key_management_plan,
)

KEYCHAIN_KEY_ADAPTER_ID = "KEYCHAIN-KEY-ADAPTER-001"
KEYCHAIN_KEY_ADAPTER_POLICY_REF = "policy_keychain_key_adapter_v1"


class KeychainKeyRef(StrictModel):
    key_class: KeyMaterialClass
    key_id_ref: str = Field(min_length=1)
    provider: str = "macos_keychain"
    backend_available: bool
    material_returned: bool = False
    wrapped_key_metadata_only: bool = True

    @model_validator(mode="after")
    def keep_ref_material_free(self) -> "KeychainKeyRef":
        if self.material_returned:
            raise ValueError("keychain key refs cannot return raw key material")
        if not self.wrapped_key_metadata_only:
            raise ValueError("keychain key refs must be metadata-only")
        if "keychain" not in self.provider.lower():
            raise ValueError("keychain key refs must use a keychain provider")
        return self


class KeychainKeyAdapterSmokeResult(StrictModel):
    proof_id: str = KEYCHAIN_KEY_ADAPTER_ID
    policy_ref: str = KEYCHAIN_KEY_ADAPTER_POLICY_REF
    checked_at: datetime
    platform_system: str = Field(min_length=1)
    security_cli_detected: bool
    native_backend_detected: bool
    key_ref_count: int = Field(ge=0)
    key_refs: list[KeychainKeyRef]
    read_only_probe_used: bool = True
    keychain_write_attempted: bool = False
    key_material_returned: bool = False
    env_secret_used: bool = False
    production_noop_allowed: bool = False
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            KEYCHAIN_KEY_ADAPTER_POLICY_REF,
            KEY_MANAGEMENT_PLAN_POLICY_REF,
        ]
    )
    passed: bool

    @model_validator(mode="after")
    def keep_adapter_safe(self) -> "KeychainKeyAdapterSmokeResult":
        if KEYCHAIN_KEY_ADAPTER_POLICY_REF not in self.policy_refs:
            raise ValueError("keychain adapter smoke requires policy ref")
        if not self.read_only_probe_used:
            raise ValueError("keychain adapter smoke must be read-only")
        if self.keychain_write_attempted:
            raise ValueError("keychain adapter smoke cannot write to keychain")
        if self.key_material_returned or self.env_secret_used:
            raise ValueError("keychain adapter smoke cannot expose key material or env secrets")
        if self.production_noop_allowed:
            raise ValueError("keychain adapter smoke cannot allow production noop keys")
        required_allowed = {
            "detect_keychain_backend",
            "return_key_ref_metadata",
            "validate_key_class_boundaries",
        }
        if missing := sorted(required_allowed.difference(self.allowed_effects)):
            raise ValueError(f"keychain adapter smoke missing allowed effects: {missing}")
        required_blocked = {
            "create_keychain_item",
            "read_keychain_secret",
            "export_unwrapped_key",
            "fallback_to_env_secret",
            "use_noop_production_cipher",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"keychain adapter smoke missing blocked effects: {missing}")
        return self


def build_keychain_key_refs(
    plan: KeyManagementPlan | None = None,
    *,
    backend_available: bool | None = None,
) -> list[KeychainKeyRef]:
    plan = plan or build_default_key_management_plan()
    backend = _keychain_backend_available() if backend_available is None else backend_available
    return [
        KeychainKeyRef(
            key_class=boundary.key_class,
            key_id_ref=boundary.key_id_ref,
            backend_available=backend,
        )
        for boundary in plan.key_boundaries
    ]


def run_keychain_key_adapter_smoke(
    *,
    now: datetime | None = None,
    security_cli_detected: bool | None = None,
    platform_system: str | None = None,
) -> KeychainKeyAdapterSmokeResult:
    timestamp = _timestamp(now)
    system = platform_system or platform.system() or "unknown"
    security_detected = (
        _security_cli_detected()
        if security_cli_detected is None
        else security_cli_detected
    )
    native_backend_detected = system == "Darwin" and security_detected
    refs = build_keychain_key_refs(backend_available=native_backend_detected)
    passed = (
        bool(refs)
        and len(refs) == len(set(KeyMaterialClass))
        and all(not ref.material_returned for ref in refs)
        and all(ref.wrapped_key_metadata_only for ref in refs)
        and not build_default_key_management_plan().production_allows_noop_cipher
    )
    return KeychainKeyAdapterSmokeResult(
        checked_at=timestamp,
        platform_system=system,
        security_cli_detected=security_detected,
        native_backend_detected=native_backend_detected,
        key_ref_count=len(refs),
        key_refs=refs,
        key_material_returned=False,
        production_noop_allowed=False,
        allowed_effects=[
            "detect_keychain_backend",
            "return_key_ref_metadata",
            "validate_key_class_boundaries",
        ],
        blocked_effects=[
            "create_keychain_item",
            "read_keychain_secret",
            "export_unwrapped_key",
            "fallback_to_env_secret",
            "use_noop_production_cipher",
        ],
        passed=passed,
    )


def _security_cli_detected() -> bool:
    return shutil.which("security") is not None


def _keychain_backend_available() -> bool:
    return platform.system() == "Darwin" and _security_cli_detected()


def _timestamp(now: datetime | None) -> datetime:
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run_keychain_key_adapter_smoke()
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        print(
            f"{KEYCHAIN_KEY_ADAPTER_ID}: {'passed' if result.passed else 'failed'}; "
            f"backend={result.native_backend_detected}; key_refs={result.key_ref_count}"
        )
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
