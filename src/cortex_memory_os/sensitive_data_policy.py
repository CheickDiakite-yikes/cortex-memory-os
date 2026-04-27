"""Code-facing constants for secret, PII, and local-data handling."""

from __future__ import annotations

SECRET_PII_POLICY_REF = "policy_secret_pii_local_data_v1"
FIREWALL_POLICY_REF = "policy_firewall_synthetic_v1"
REDACTED_SECRET_PLACEHOLDER = "[REDACTED_SECRET]"

REQUIRED_NON_COMMIT_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "secrets/",
    "private/",
    "data/",
    "local-data/",
    "memory-store/",
    "vector-store/",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    "*.log",
    "benchmarks/runs/*",
)

RAW_EVIDENCE_DEFAULT = "expire_raw_before_memory_promotion"
MODEL_TRAINING_DEFAULT = "never_eligible"
