---
name: mutilagentsroleplay-memory
description: Persistent project memory for the D:\Cat_Codes\MutilAgentsRolePlay workspace. Use whenever the current task belongs to this repository, the user expects the AI to remember project background or progress, or the AI should follow project-specific development rules and maintain architecture and progress documentation after development work. Read docs/project-context.md, docs/project-progress.md, and docs/development-rules.md before substantive work, then update the project docs after meaningful implementation or decision changes.
---

# MutilAgentsRolePlay Project Memory

Read `docs/project-context.md`, `docs/project-progress.md`, and `docs/development-rules.md` before doing substantive work in `D:\Cat_Codes\MutilAgentsRolePlay`.

## Startup Workflow

1. Confirm the task is for `D:\Cat_Codes\MutilAgentsRolePlay`.
2. Read `docs/project-context.md` for product background, architecture, and team conventions.
3. Read `docs/project-progress.md` for current phase, recent changes, and next steps.
4. Read `docs/development-rules.md` for project-specific execution rules and constraints.
5. Use those documents as shared project memory so the user does not need to restate context.

## Update Workflow

Update the project docs before finishing when work changed the project state:

- Update `docs/project-progress.md` when implementation status, completed work, blockers, or next steps changed.
- Update `docs/project-context.md` when architecture, module boundaries, stack choices, integrations, or technical decisions changed.
- Update `docs/development-rules.md` when the user introduced new long-term development rules, constraints, or conventions that should persist across future sessions.
- Keep updates short, factual, and cumulative.
- Preserve user-written notes unless newer facts clearly supersede them.

## Editing Rules

- Prefer appending dated progress notes instead of rewriting history.
- Leave `TBD` or `待补充` placeholders when project facts are unknown instead of inventing details.
- Skip `docs/project-context.md` when no architecture or decision changed.
- Skip `docs/development-rules.md` unless the rule set itself changed.
- Skip doc edits after purely exploratory work unless the project state genuinely changed.

## Expected Doc Locations

- Context: `docs/project-context.md`
- Progress: `docs/project-progress.md`
- Rules: `docs/development-rules.md`
