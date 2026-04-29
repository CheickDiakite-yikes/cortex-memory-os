import pytest
from pydantic import ValidationError

from cortex_memory_os.shadow_pointer import (
    ShadowPointerControlAction,
    ShadowPointerControlCommand,
    ShadowPointerSnapshot,
    ShadowPointerState,
    apply_control,
    default_shadow_pointer_snapshot,
    transition,
)


def test_default_shadow_pointer_snapshot_is_observing():
    snapshot = default_shadow_pointer_snapshot()

    assert snapshot.state == ShadowPointerState.OBSERVING
    assert "Terminal" in snapshot.seeing
    assert "password fields" in snapshot.ignoring


def test_private_masking_requires_ignored_items():
    with pytest.raises(ValidationError, match="private masking"):
        ShadowPointerSnapshot(
            state=ShadowPointerState.PRIVATE_MASKING,
            workstream_label="Sensitive view",
        )


def test_remembering_requires_possible_memory():
    with pytest.raises(ValidationError, match="possible memory"):
        ShadowPointerSnapshot(
            state=ShadowPointerState.REMEMBERING,
            workstream_label="Research sprint",
            seeing=["Chrome"],
        )


def test_needs_approval_requires_reason():
    with pytest.raises(ValidationError, match="approval reason"):
        ShadowPointerSnapshot(
            state=ShadowPointerState.NEEDS_APPROVAL,
            workstream_label="Skill execution",
            seeing=["Gmail"],
        )


def test_transition_to_off_removes_observation_details():
    snapshot = default_shadow_pointer_snapshot()

    next_snapshot = transition(snapshot, ShadowPointerState.OFF)

    assert next_snapshot.state == ShadowPointerState.OFF
    assert next_snapshot.seeing == []
    assert next_snapshot.possible_memory is None


def test_pause_control_blocks_observation_and_memory_writes():
    snapshot = default_shadow_pointer_snapshot()
    command = ShadowPointerControlCommand(
        action=ShadowPointerControlAction.PAUSE_OBSERVATION,
        duration_minutes=60,
    )

    receipt = apply_control(snapshot, command)

    assert receipt.resulting_snapshot.state == ShadowPointerState.PAUSED
    assert receipt.observation_active is False
    assert receipt.memory_write_allowed is False
    assert receipt.audit_required is True
    assert receipt.audit_action == "pause_observation"
    assert receipt.expires_at is not None


def test_delete_recent_control_requires_confirmation():
    with pytest.raises(ValidationError, match="explicit user confirmation"):
        ShadowPointerControlCommand(
            action=ShadowPointerControlAction.DELETE_RECENT,
            delete_window_minutes=10,
        )


def test_delete_recent_control_masks_and_blocks_memory_writes():
    snapshot = default_shadow_pointer_snapshot()
    command = ShadowPointerControlCommand(
        action=ShadowPointerControlAction.DELETE_RECENT,
        delete_window_minutes=10,
        user_confirmed=True,
    )

    receipt = apply_control(snapshot, command)

    assert receipt.resulting_snapshot.state == ShadowPointerState.PRIVATE_MASKING
    assert receipt.deleted_window_minutes == 10
    assert receipt.memory_write_allowed is False
    assert receipt.audit_action == "delete_recent_observation"
    assert "last 10 minutes" in receipt.resulting_snapshot.ignoring


def test_ignore_app_control_removes_app_from_seen_context():
    snapshot = default_shadow_pointer_snapshot()
    command = ShadowPointerControlCommand(
        action=ShadowPointerControlAction.IGNORE_APP,
        app_name="Chrome",
        user_confirmed=True,
    )

    receipt = apply_control(snapshot, command)

    assert receipt.resulting_snapshot.state == ShadowPointerState.PRIVATE_MASKING
    assert "Chrome" not in receipt.resulting_snapshot.seeing
    assert "Chrome" in receipt.resulting_snapshot.ignoring
    assert receipt.affected_apps == ["Chrome"]
    assert receipt.memory_write_allowed is False


def test_ignore_app_control_requires_named_app():
    with pytest.raises(ValidationError, match="requires app_name"):
        ShadowPointerControlCommand(
            action=ShadowPointerControlAction.IGNORE_APP,
            app_name=" ",
            user_confirmed=True,
        )


def test_status_control_is_read_only():
    snapshot = default_shadow_pointer_snapshot()
    command = ShadowPointerControlCommand(action=ShadowPointerControlAction.STATUS)

    receipt = apply_control(snapshot, command)

    assert receipt.resulting_snapshot == snapshot
    assert receipt.audit_required is False
    assert receipt.observation_active is True
    assert receipt.memory_write_allowed is True
