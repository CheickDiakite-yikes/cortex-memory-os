"""Shadow Pointer state contract."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
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


class ShadowPointerControlAction(str, Enum):
    STATUS = "status"
    PAUSE_OBSERVATION = "pause_observation"
    RESUME_OBSERVATION = "resume_observation"
    DELETE_RECENT = "delete_recent"
    IGNORE_APP = "ignore_app"


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


class ShadowPointerControlCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: ShadowPointerControlAction
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor: str = Field(default="user", min_length=1)
    duration_minutes: int | None = Field(default=None, ge=1, le=24 * 60)
    delete_window_minutes: int | None = Field(default=None, ge=1, le=24 * 60)
    app_name: str | None = None
    user_confirmed: bool = False

    @model_validator(mode="after")
    def require_action_specific_inputs(self) -> ShadowPointerControlCommand:
        if self.action == ShadowPointerControlAction.PAUSE_OBSERVATION:
            if self.duration_minutes is None:
                raise ValueError("pause observation requires duration_minutes")
        if self.action == ShadowPointerControlAction.DELETE_RECENT:
            if self.delete_window_minutes is None:
                raise ValueError("delete recent requires delete_window_minutes")
            if not self.user_confirmed:
                raise ValueError("delete recent requires explicit user confirmation")
        if self.action == ShadowPointerControlAction.IGNORE_APP:
            if not self.app_name or not self.app_name.strip():
                raise ValueError("ignore app requires app_name")
            if not self.user_confirmed:
                raise ValueError("ignore app requires explicit user confirmation")
        return self


class ShadowPointerControlReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receipt_id: str = Field(min_length=1)
    action: ShadowPointerControlAction
    resulting_snapshot: ShadowPointerSnapshot
    observation_active: bool
    memory_write_allowed: bool
    audit_required: bool
    audit_action: str | None = None
    confirmation_observed: bool
    affected_apps: list[str] = Field(default_factory=list)
    deleted_window_minutes: int | None = None
    expires_at: datetime | None = None
    safety_notes: list[str] = Field(min_length=1)


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


def apply_control(
    snapshot: ShadowPointerSnapshot,
    command: ShadowPointerControlCommand,
) -> ShadowPointerControlReceipt:
    """Apply a user-visible Shadow Pointer control command."""

    requested_at = _ensure_utc(command.requested_at)
    receipt_id = f"shadow_receipt_{command.action.value}_{int(requested_at.timestamp())}"

    if command.action == ShadowPointerControlAction.STATUS:
        return ShadowPointerControlReceipt(
            receipt_id=receipt_id,
            action=command.action,
            resulting_snapshot=snapshot,
            observation_active=_observation_active(snapshot.state),
            memory_write_allowed=_memory_write_allowed(snapshot.state),
            audit_required=False,
            confirmation_observed=command.user_confirmed,
            safety_notes=["status is read-only"],
        )

    if command.action == ShadowPointerControlAction.PAUSE_OBSERVATION:
        paused = ShadowPointerSnapshot(
            state=ShadowPointerState.PAUSED,
            workstream_label=f"Paused for {command.duration_minutes} min",
            seeing=[],
            ignoring=["all observation until resume or timeout"],
            possible_memory=None,
            possible_skill=snapshot.possible_skill,
        )
        return ShadowPointerControlReceipt(
            receipt_id=receipt_id,
            action=command.action,
            resulting_snapshot=paused,
            observation_active=False,
            memory_write_allowed=False,
            audit_required=True,
            audit_action="pause_observation",
            confirmation_observed=command.user_confirmed,
            expires_at=_minutes_from(requested_at, command.duration_minutes),
            safety_notes=[
                "observation disabled",
                "memory writes blocked while paused",
            ],
        )

    if command.action == ShadowPointerControlAction.RESUME_OBSERVATION:
        resumed = ShadowPointerSnapshot(
            state=ShadowPointerState.OBSERVING,
            workstream_label="Observation resumed",
            seeing=snapshot.seeing or ["authorized apps"],
            ignoring=snapshot.ignoring,
            possible_memory=snapshot.possible_memory,
            possible_skill=snapshot.possible_skill,
        )
        return ShadowPointerControlReceipt(
            receipt_id=receipt_id,
            action=command.action,
            resulting_snapshot=resumed,
            observation_active=True,
            memory_write_allowed=True,
            audit_required=True,
            audit_action="resume_observation",
            confirmation_observed=command.user_confirmed,
            safety_notes=["observation resumed within current consent scope"],
        )

    if command.action == ShadowPointerControlAction.DELETE_RECENT:
        deleted = ShadowPointerSnapshot(
            state=ShadowPointerState.PRIVATE_MASKING,
            workstream_label="Recent observation deletion",
            seeing=[],
            ignoring=[f"last {command.delete_window_minutes} minutes"],
            possible_memory=None,
            possible_skill=snapshot.possible_skill,
        )
        return ShadowPointerControlReceipt(
            receipt_id=receipt_id,
            action=command.action,
            resulting_snapshot=deleted,
            observation_active=_observation_active(snapshot.state),
            memory_write_allowed=False,
            audit_required=True,
            audit_action="delete_recent_observation",
            confirmation_observed=command.user_confirmed,
            deleted_window_minutes=command.delete_window_minutes,
            safety_notes=[
                "raw and derived observations in the selected window must be deleted or tombstoned",
                "new memory writes are blocked until deletion completes",
            ],
        )

    if command.action == ShadowPointerControlAction.IGNORE_APP:
        app_name = (command.app_name or "").strip()
        seeing = [item for item in snapshot.seeing if item != app_name]
        ignoring = _append_unique(snapshot.ignoring, app_name)
        ignored = ShadowPointerSnapshot(
            state=ShadowPointerState.PRIVATE_MASKING,
            workstream_label=f"Ignoring {app_name}",
            seeing=seeing,
            ignoring=ignoring,
            possible_memory=snapshot.possible_memory,
            possible_skill=snapshot.possible_skill,
        )
        return ShadowPointerControlReceipt(
            receipt_id=receipt_id,
            action=command.action,
            resulting_snapshot=ignored,
            observation_active=_observation_active(snapshot.state),
            memory_write_allowed=False,
            audit_required=True,
            audit_action="ignore_app_observation",
            confirmation_observed=command.user_confirmed,
            affected_apps=[app_name],
            safety_notes=[
                "ignored app must be excluded from capture adapters",
                "memory writes from ignored app are blocked",
            ],
        )

    raise ValueError(f"unsupported Shadow Pointer control action: {command.action}")


def default_shadow_pointer_snapshot() -> ShadowPointerSnapshot:
    return ShadowPointerSnapshot(
        state=ShadowPointerState.OBSERVING,
        workstream_label="Debugging auth flow",
        seeing=["VS Code", "Terminal", "Chrome"],
        ignoring=["password fields", "private messages"],
        possible_memory="Auth bug reproduction flow",
        possible_skill="Frontend auth debugging",
    )


def _append_unique(values: list[str], value: str) -> list[str]:
    if value in values:
        return list(values)
    return [*values, value]


def _memory_write_allowed(state: ShadowPointerState) -> bool:
    return state not in {
        ShadowPointerState.OFF,
        ShadowPointerState.PAUSED,
        ShadowPointerState.PRIVATE_MASKING,
        ShadowPointerState.NEEDS_APPROVAL,
    }


def _observation_active(state: ShadowPointerState) -> bool:
    return state not in {ShadowPointerState.OFF, ShadowPointerState.PAUSED}


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _minutes_from(start: datetime, minutes: int | None) -> datetime | None:
    if minutes is None:
        return None
    return start + timedelta(minutes=minutes)
