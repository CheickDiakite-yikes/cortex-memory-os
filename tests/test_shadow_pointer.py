import pytest
from pydantic import ValidationError

from cortex_memory_os.shadow_pointer import (
    ShadowPointerSnapshot,
    ShadowPointerState,
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

