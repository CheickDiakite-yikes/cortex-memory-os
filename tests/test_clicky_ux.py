import pytest
from pydantic import ValidationError

from cortex_memory_os.clicky_ux import (
    CLICKY_UX_COMPANION_ID,
    CLICKY_UX_COMPANION_POLICY_REF,
    CLICKY_UX_LESSONS_POLICY_REF,
    ClickyUxLesson,
    build_clicky_ux_companion_panel,
    clicky_ux_payload_is_safe,
    default_clicky_ux_lessons,
)
from cortex_memory_os.shadow_pointer_native_live_feed import (
    build_native_shadow_pointer_live_feed,
)
from cortex_memory_os.shadow_pointer import (
    ShadowPointerObservationMode,
    build_live_receipt,
    default_shadow_pointer_snapshot,
)
from cortex_memory_os.contracts import SourceTrust


def _native_feed():
    live_receipt = build_live_receipt(
        default_shadow_pointer_snapshot(),
        observation_mode=ShadowPointerObservationMode.SESSION,
        source_trust=SourceTrust.EXTERNAL_UNTRUSTED,
        firewall_decision="ephemeral_only",
        evidence_write_mode="derived_only",
        memory_eligible=False,
        raw_ref_retained=False,
    )
    return build_native_shadow_pointer_live_feed([live_receipt])


def test_clicky_ux_lessons_are_reference_only():
    lessons = default_clicky_ux_lessons()

    assert len(lessons) == 4
    assert all(CLICKY_UX_LESSONS_POLICY_REF in lesson.policy_refs for lesson in lessons)
    assert all(lesson.external_source_untrusted for lesson in lessons)
    assert all(not lesson.repo_code_executed for lesson in lessons)
    assert all(not lesson.setup_commands_executed for lesson in lessons)
    assert all("direct_text_to_click_actions" in lesson.blocked_borrowing for lesson in lessons)


def test_clicky_ux_companion_keeps_live_surface_small_and_safe():
    companion = build_clicky_ux_companion_panel(_native_feed())
    lessons = default_clicky_ux_lessons()
    payload = companion.model_dump_json()

    assert companion.panel_id == CLICKY_UX_COMPANION_ID
    assert CLICKY_UX_COMPANION_POLICY_REF in companion.policy_refs
    assert companion.title == "Cursor Companion"
    assert companion.display_mode == "cursor_adjacent_receipt"
    assert companion.display_only
    assert companion.content_redacted
    assert companion.source_refs_redacted
    assert not companion.raw_payload_included
    assert not companion.voice_capture_enabled
    assert not companion.real_screen_capture_started
    assert not companion.memory_write_allowed
    assert "render_cursor_companion" in companion.allowed_effects
    assert "execute_click" in companion.blocked_effects
    assert "send_to_remote_proxy" in companion.blocked_effects
    assert "raw://" not in payload
    assert clicky_ux_payload_is_safe(lessons, companion)


def test_clicky_ux_lesson_rejects_executed_external_code():
    with pytest.raises(ValidationError, match="cannot execute external repo code"):
        ClickyUxLesson(
            lesson_id="bad",
            source_url="https://github.com/farzaa/clicky",
            observed_pattern="bad",
            cortex_adaptation="bad",
            repo_code_executed=True,
            blocked_borrowing=[
                "raw_transcript_analytics",
                "direct_text_to_click_actions",
                "hardcoded_remote_proxy_for_memory",
            ],
        )
