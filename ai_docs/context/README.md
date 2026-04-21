# Context

This directory is for task-scoped or phase-scoped AI context that is useful across a short period of work, but should not live as a long-term rule in `ai_docs/rules/`.

## What belongs here
- A concise summary of the current implementation focus when it spans multiple related tasks.
- Temporary project context that helps AI make better decisions during an active phase of work.
- Curated notes that connect several source documents into one short AI-readable task context.
- Short-lived migration, refactor, or rollout context that is broader than a single prompt but not stable enough for long-term rules.

## What does not belong here
- OpenSpec artifacts from `openspec/`.
- Stable coding rules that belong in `ai_docs/rules/`.
- Canonical implementation patterns that belong in `ai_docs/examples/`.
- Raw meeting notes, long transcripts, or large copied documents.
- Stale task notes that no longer affect current work.

## Writing guidance
Context files here should be:
- short
- explicit about scope
- explicit about why the context matters
- easy for AI to scan quickly

Prefer concise summaries over copied source material.

## Suggested file style
A context file should usually include:
- scope
- current objective
- constraints
- non-goals
- decisions already made
- links or paths to source documents when needed

## Naming guidance
Use names that describe the active topic or phase, for example:
- `bootstrap_context.md`
- `refactor_context.md`
- `migration_constraints.md`

Avoid vague names such as:
- `notes.md`
- `temp.md`
- `misc_context.md`

## Maintenance rule
Delete or rewrite context files when they stop being relevant. This directory should stay small and current.
