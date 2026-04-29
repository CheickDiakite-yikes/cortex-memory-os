# Robot Spatial Safety Contract

Last updated: 2026-04-29

`ROBOT-SPATIAL-SAFETY-001` defines the first embodied-action safety metadata
contract for Cortex. It does not connect to a robot yet. It defines what a
future robot adapter or planner must prove before any physical action can be
considered by the governance layer.

## Purpose

Laptop actions can usually be rolled back. Robot actions can touch people,
objects, heat, liquids, sharp edges, fragile materials, restricted spaces, and
unknown environments. Cortex therefore treats robot execution as a separate
safety boundary, even when a skill or memory is approved.

Every future robot action envelope must carry:

- explicit robot capability ref;
- source refs for the scene, plan, or user request;
- workspace bounds ref;
- target object ref when an object is involved;
- relevant affordances;
- material constraints;
- spatial hazards;
- bystander-present status;
- simulation status and simulation evidence refs;
- approval ref before physical effects;
- emergency stop ref;
- max force and speed metadata;
- `policy_robot_spatial_safety_v1`.

## Hard Boundaries

- Non-robot capabilities are rejected.
- Wildcard refs such as `all`, `global`, or `*` are rejected.
- Physical effects require emergency stop metadata.
- Physical effects require max force and max speed metadata.
- Physical effects must have passed simulation status with evidence refs.
- Physical effects require explicit approval before execution.
- Bystanders or spatial hazards force step-by-step review.
- High-risk actions force step-by-step review.
- Critical actions are blocked by default.
- Force and speed limits are bounded before execution.

## Decision Shape

The evaluator returns:

- `allowed`: whether the action may proceed inside the current envelope;
- `required_behavior`: audit-only, approval-before-physical-effect,
  fix-metadata-before-action, step-by-step-review, or blocked-by-default;
- `reason_codes`: machine-readable denial or review reasons;
- `policy_refs`: active policy IDs;
- `audit_tags`: capability, workspace, simulation, and hazard-count metadata.

## Benchmark Contract

`ROBOT-SAFE-001` now checks two levels:

- high-risk action gating still requires step-by-step review even with an
  approved skill;
- robot spatial safety metadata rejects missing simulation, hazards,
  bystanders, excessive force, excessive speed, wildcard scopes, and missing
  emergency-stop metadata.

This keeps Cortex robot-ready without pretending the laptop MVP can safely
operate physical hardware.
