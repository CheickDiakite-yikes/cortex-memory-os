"""Shadow Pointer state contract."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ShadowPointerState(str, Enum):
    OFF = "off"
    OBSERVING = "observing"
    PRIVATE_MASKING = "private_masking"
    SEGMENTING = "segmenting"
    REMEMBERING = "remembering"
    LEARNING_SKILL = "learning_skill"
    AGENT_CONTEXTING = "agent_contexting"
    AGENT_ACTING = "agent_acting"
    NEEDS_APPROVAL = "needs_approval"
    PAUSED = "paused"


class ShadowPointerSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: ShadowPointerState
    workstream_label: str = Field(min_length=1)
    seeing: list[str] = Field(default_factory=list)
    ignoring: list[str] = Field(default_factory=list)
    possible_memory: str | None = None
    possible_skill: str | None = None
    approval_reason: str | None = None

    @model_validator(mode="after")
    def state_requires_matching_context(self) -> ShadowPointerSnapshot:
        if self.state == ShadowPointerState.PRIVATE_MASKING and not self.ignoring:
            raise ValueError("private masking state requires ignored/masked items")
        if self.state == ShadowPointerState.REMEMBERING and not self.possible_memory:
            raise ValueError("remembering state requires a possible memory")
        if self.state == ShadowPointerState.LEARNING_SKILL and not self.possible_skill:
            raise ValueError("learning skill state requires a possible skill")
        if self.state == ShadowPointerState.NEEDS_APPROVAL and not self.approval_reason:
            raise ValueError("needs approval state requires an approval reason")
        if self.state == ShadowPointerState.OFF and (self.seeing or self.possible_memory):
            raise ValueError("off state cannot include active observation details")
        return self


def transition(snapshot: ShadowPointerSnapshot, next_state: ShadowPointerState) -> ShadowPointerSnapshot:
    updates: dict[str, object] = {"state": next_state}
    if next_state == ShadowPointerState.OFF:
        updates.update(
            {
                "workstream_label": "Off",
                "seeing": [],
                "ignoring": [],
                "possible_memory": None,
                "possible_skill": None,
                "approval_reason": None,
            }
        )
    elif next_state == ShadowPointerState.PAUSED:
        updates.update(
            {
                "seeing": [],
                "possible_memory": None,
                "approval_reason": None,
            }
        )
    return snapshot.model_copy(update=updates)


def default_shadow_pointer_snapshot() -> ShadowPointerSnapshot:
    return ShadowPointerSnapshot(
        state=ShadowPointerState.OBSERVING,
        workstream_label="Debugging auth flow",
        seeing=["VS Code", "Terminal", "Chrome"],
        ignoring=["password fields", "private messages"],
        possible_memory="Auth bug reproduction flow",
        possible_skill="Frontend auth debugging",
    )

