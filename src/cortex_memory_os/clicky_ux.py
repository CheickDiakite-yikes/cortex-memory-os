"""Clicky-inspired UX adaptation contracts for Cortex surfaces."""

from __future__ import annotations

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.shadow_pointer_native_live_feed import (
    NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
    NativeShadowPointerLiveFeedReceipt,
)

CLICKY_UX_LESSONS_ID = "CLICKY-UX-LESSONS-001"
CLICKY_UX_LESSONS_POLICY_REF = "policy_clicky_ux_lessons_v1"
CLICKY_UX_COMPANION_ID = "CLICKY-UX-COMPANION-001"
CLICKY_UX_COMPANION_POLICY_REF = "policy_clicky_ux_companion_v1"


class ClickyUxLesson(StrictModel):
    lesson_id: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    observed_pattern: str = Field(min_length=1)
    cortex_adaptation: str = Field(min_length=1)
    external_source_untrusted: bool = True
    repo_code_executed: bool = False
    setup_commands_executed: bool = False
    blocked_borrowing: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(default_factory=lambda: [CLICKY_UX_LESSONS_POLICY_REF])

    @model_validator(mode="after")
    def keep_lesson_as_reference_only(self) -> ClickyUxLesson:
        if CLICKY_UX_LESSONS_POLICY_REF not in self.policy_refs:
            raise ValueError("Clicky UX lessons require policy ref")
        if not self.external_source_untrusted:
            raise ValueError("external UX reference must remain untrusted")
        if self.repo_code_executed or self.setup_commands_executed:
            raise ValueError("Clicky UX lesson intake cannot execute external repo code")
        required_blocked = {
            "raw_transcript_analytics",
            "direct_text_to_click_actions",
            "hardcoded_remote_proxy_for_memory",
        }
        if missing := sorted(required_blocked.difference(self.blocked_borrowing)):
            raise ValueError(f"Clicky UX lesson missing blocked borrowings: {missing}")
        return self


class ClickyUxCompanionPanel(StrictModel):
    panel_id: str = CLICKY_UX_COMPANION_ID
    title: str = "Cursor Companion"
    summary: str = Field(min_length=1)
    primary_status: str = Field(min_length=1)
    next_safe_action: str = Field(min_length=1)
    display_mode: str = "cursor_adjacent_receipt"
    compact_chip_labels: list[str] = Field(min_length=3, max_length=5)
    learned_from_patterns: list[str] = Field(min_length=3)
    native_feed_id: str
    receipt_count: int = Field(ge=1)
    display_only: bool = True
    content_redacted: bool = True
    source_refs_redacted: bool = True
    raw_payload_included: bool = False
    raw_ref_retained: bool = False
    voice_capture_enabled: bool = False
    real_screen_capture_started: bool = False
    memory_write_allowed: bool = False
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            CLICKY_UX_COMPANION_POLICY_REF,
            CLICKY_UX_LESSONS_POLICY_REF,
            NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
        ]
    )

    @model_validator(mode="after")
    def keep_companion_lightweight_and_safe(self) -> ClickyUxCompanionPanel:
        if CLICKY_UX_COMPANION_POLICY_REF not in self.policy_refs:
            raise ValueError("Clicky UX companion requires policy ref")
        if not self.display_only:
            raise ValueError("Clicky UX companion must be display-only")
        if not self.content_redacted or not self.source_refs_redacted:
            raise ValueError("Clicky UX companion cannot expose content/source refs")
        if self.raw_payload_included or self.raw_ref_retained:
            raise ValueError("Clicky UX companion cannot include raw payloads or refs")
        if self.voice_capture_enabled or self.real_screen_capture_started:
            raise ValueError("Clicky UX companion cannot enable live capture")
        if self.memory_write_allowed:
            raise ValueError("Clicky UX companion cannot write memory")
        allowed = set(self.allowed_effects)
        if allowed - {"render_cursor_companion", "open_compact_receipt_panel"}:
            raise ValueError("Clicky UX companion allowed effects are too broad")
        required_blocked = {
            "start_screen_capture",
            "start_microphone_capture",
            "execute_click",
            "type_text",
            "write_memory",
            "export_payload",
            "send_to_remote_proxy",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"Clicky UX companion missing blocked effects: {missing}")
        return self


def default_clicky_ux_lessons() -> list[ClickyUxLesson]:
    source = "https://github.com/farzaa/clicky"
    blocked = [
        "raw_transcript_analytics",
        "direct_text_to_click_actions",
        "hardcoded_remote_proxy_for_memory",
    ]
    return [
        ClickyUxLesson(
            lesson_id="clicky_cursor_adjacent_presence",
            source_url=source,
            observed_pattern="A small companion lives near the cursor instead of forcing dashboard-first interaction.",
            cortex_adaptation="Keep Shadow Pointer status close to the task surface and make the dashboard a review surface.",
            blocked_borrowing=blocked,
        ),
        ClickyUxLesson(
            lesson_id="clicky_small_control_panel",
            source_url=source,
            observed_pattern="A transient compact panel carries permissions and current status.",
            cortex_adaptation="Use one compact receipt panel for trust, memory eligibility, raw refs, and policy.",
            blocked_borrowing=blocked,
        ),
        ClickyUxLesson(
            lesson_id="clicky_spatial_pointing_language",
            source_url=source,
            observed_pattern="Spatial pointing is visible and direct, but separate from the chat text.",
            cortex_adaptation="Keep spatial intent as validated display-only proposals before any action authority.",
            blocked_borrowing=blocked,
        ),
        ClickyUxLesson(
            lesson_id="clicky_onboarding_by_demonstration",
            source_url=source,
            observed_pattern="The product teaches itself through a short live-feeling demonstration.",
            cortex_adaptation="Teach Cortex through synthetic observe, mask, candidate-memory, delete, and audit receipts.",
            blocked_borrowing=blocked,
        ),
    ]


def build_clicky_ux_companion_panel(
    native_feed: NativeShadowPointerLiveFeedReceipt,
) -> ClickyUxCompanionPanel:
    return ClickyUxCompanionPanel(
        summary=(
            "A small cursor-adjacent status surface shows what Cortex is doing "
            "without turning the dashboard into the live interaction."
        ),
        primary_status=(
            f"{native_feed.latest_state.value.replace('_', ' ')}; "
            f"{native_feed.receipt_count} redacted receipt"
            f"{'' if native_feed.receipt_count == 1 else 's'} ready"
        ),
        next_safe_action="Open receipt details or pause observation; no memory write happens here.",
        compact_chip_labels=["State", "Trust", "Memory", "Raw refs"],
        learned_from_patterns=[
            "cursor-adjacent presence",
            "compact control panel",
            "visible spatial pointing",
            "onboarding by demonstration",
        ],
        native_feed_id=native_feed.feed_id,
        receipt_count=native_feed.receipt_count,
        raw_ref_retained=native_feed.raw_ref_retained,
        raw_payload_included=native_feed.raw_payload_included,
        allowed_effects=["render_cursor_companion", "open_compact_receipt_panel"],
        blocked_effects=[
            "start_screen_capture",
            "start_microphone_capture",
            "execute_click",
            "type_text",
            "write_memory",
            "export_payload",
            "send_to_remote_proxy",
        ],
    )


def clicky_ux_payload_is_safe(
    lessons: list[ClickyUxLesson],
    companion: ClickyUxCompanionPanel,
) -> bool:
    payload = "\n".join([*(lesson.model_dump_json() for lesson in lessons), companion.model_dump_json()])
    prohibited = [
        "OPENAI_API_KEY=",
        "CORTEX_FAKE_TOKEN",
        "sk-",
        "raw://",
        "encrypted_blob://",
        "Ignore previous instructions",
    ]
    return not any(marker in payload for marker in prohibited)
