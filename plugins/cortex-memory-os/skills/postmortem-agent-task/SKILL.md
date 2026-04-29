---
name: postmortem-agent-task
description: Propose Cortex self-lessons after agent work without silently changing permissions, values, or autonomy.
---

# Postmortem Agent Task

Use this skill after meaningful agent work, especially when the task involved a
failure, correction, repeated pattern, missing context, wrong tool choice, or
successful workflow worth preserving.

## Workflow

1. Summarize the outcome in neutral, evidence-backed terms.
2. Identify whether the lesson is about retrieval, context templates, tool
   choice, failure checklists, user preferences, safety filters, or evaluation.
3. Call `self_lesson.propose` when the lesson is useful and scoped.
4. Keep the proposal candidate-only. Promotion requires explicit review.
5. Use `self_lesson.review_queue` or `self_lesson.review_flow` for later user
   inspection when review is required.

## Guardrails

- Self-lessons can improve methods, not permissions, values, boundaries, or
  autonomy.
- Do not copy private task text, secrets, raw evidence, or long source content
  into a self-lesson.
- Scope narrowly: project-specific beats global when the lesson came from one
  repo or one workflow.
- Include source refs and confidence, and make rollback conditions visible.

Load `references/memory_policy.md` when deciding whether a lesson may influence
future context packs.
