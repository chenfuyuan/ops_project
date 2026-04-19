---
name: "OPSX: Fast Forward"
description: Create a change and generate all artifacts needed for implementation in one go
category: Workflow
tags: [workflow, artifacts, experimental]
---

Fast-forward through artifact creation - generate everything needed to start implementation.

**Input**: The argument after `/opsx:ff` is the change name (kebab-case), OR a description of what the user wants to build.

**Steps**

1. **If no input provided, ask what they want to build**

   Use the **AskUserQuestion tool** (open-ended, no preset options) to ask:
   > "What change do you want to work on? Describe what you want to build or fix."

   From their description, derive a kebab-case name (e.g., "add user authentication" → `add-user-auth`).

   **IMPORTANT**: Do NOT proceed without understanding what the user wants to build.

2. **Create or reuse the change directory**

   Check if `openspec/changes/<name>/` already exists (e.g., created by `/opsx:pre-design`).
   - If it exists, reuse it — do NOT run `openspec new change` again
   - If it doesn't exist, create it:
     ```bash
     openspec new change "<name>"
     ```

3. **Check for pre_design**

   Check if `openspec/changes/<name>/pre_design.md` exists. If it does:
   - Read it (and any sibling `pre_design.*.md` volume files)
   - This is the **binding upstream input** for all subsequent artifact generation
   - Announce to user: "Found pre_design.md — all artifacts will be generated under its constraints."

   If `pre_design.md` does not exist, proceed without it (the classic flow).

4. **Get the artifact build order**
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse the JSON to get:
   - `applyRequires`: array of artifact IDs needed before implementation (e.g., `["tasks"]`)
   - `artifacts`: list of all artifacts with their status and dependencies

5. **Create artifacts in sequence until apply-ready**

   Use the **TodoWrite tool** to track progress through the artifacts.

   Loop through artifacts in dependency order (artifacts with no pending dependencies first):

   a. **For each artifact that is `ready` (dependencies satisfied)**:
      - Get instructions:
        ```bash
        openspec instructions <artifact-id> --change "<name>" --json
        ```
      - The instructions JSON includes:
        - `context`: Project background (constraints for you - do NOT include in output)
        - `rules`: Artifact-specific rules (constraints for you - do NOT include in output)
        - `template`: The structure to use for your output file
        - `instruction`: Schema-specific guidance for this artifact type
        - `outputPath`: Where to write the artifact
        - `dependencies`: Completed artifacts to read for context
      - Read any completed dependency files for context
      - **If pre_design exists**: apply `pre_design` constraints (see section below)
      - Create the artifact file using `template` as the structure
      - Apply `context` and `rules` as constraints - but do NOT copy them into the file
      - Show brief progress: "✓ Created <artifact-id>"

   b. **Continue until all `applyRequires` artifacts are complete**
      - After creating each artifact, re-run `openspec status --change "<name>" --json`
      - Check if every artifact ID in `applyRequires` has `status: "done"` in the artifacts array
      - Stop when all `applyRequires` artifacts are done

   c. **If an artifact requires user input** (unclear context):
      - Use **AskUserQuestion tool** to clarify
      - Then continue with creation

6. **Show final status**
   ```bash
   openspec status --change "<name>"
   ```

**Output**

After completing all artifacts, summarize:
- Change name and location
- Whether pre_design was used as upstream constraint
- List of artifacts created with brief descriptions
- What's ready: "All artifacts created! Ready for implementation."
- Prompt: "Run `/opsx:apply` to start implementing with the default TDD workflow."

**Artifact Creation Guidelines**

- Follow the `instruction` field from `openspec instructions` for each artifact type
- The schema defines what each artifact should contain - follow it
- Read dependency artifacts for context before creating new ones
- Use the `template` as a starting point, filling in based on context

**Pre-Design Constraint Rules**

When `pre_design.md` exists, it is the **primary upstream constraint** for all artifact generation. Apply the following rules:

1. **Binding sections** — The following sections in `pre_design` are hard constraints that downstream artifacts must not contradict:
   - Problem framing / Goals / Non-goals
   - Constraints / Invariants
   - Key decisions / Trade-offs
   - Generation guardrails → "Must follow" items
   - Generation guardrails → "Forbidden to invent" items

2. **Mapping guidance** — The `OpenSpec mapping` section in `pre_design` explicitly describes what each downstream artifact should focus on:
   - Use `What proposal.md should cover` to guide `proposal.md` content
   - Use `What design.md should cover` to guide `design.md` content
   - Use `What tasks.md should cover` to guide `tasks.md` content

3. **Allowed elaboration** — The "Allowed to elaborate" section defines the space where downstream artifacts may add detail without violating `pre_design` constraints.

4. **Scope control** — If `pre_design` lists explicit Non-goals, downstream artifacts must NOT introduce work that falls within those Non-goals.

5. **Contract fidelity** — If `pre_design` defines contract drafts (request/response fields, API surface), downstream artifacts must not expand the public contract beyond what `pre_design` specifies.

6. **Per-artifact application**:
   - **proposal.md**: Focus on the "why" as guided by `pre_design` mapping. Do not expand scope.
   - **specs/**: Define requirements within the boundaries set by `pre_design`. Do not add capabilities not mentioned in Goals.
   - **design.md**: Elaborate architecture within the direction set by `pre_design`. Follow key decisions. Do not introduce approaches that contradict Trade-offs.
   - **tasks.md**: Break down work within the scope defined by `pre_design`. Do not add tasks for Non-goals or Forbidden items.

**Guardrails**
- Create ALL artifacts needed for implementation (as defined by schema's `apply.requires`)
- Always read dependency artifacts before creating a new one
- If pre_design exists, treat it as the highest-priority constraint — above `openspec instructions` context
- If context is critically unclear, ask the user - but prefer making reasonable decisions to keep momentum
- If a change with that name already exists, ask if user wants to continue it or create a new one
- Verify each artifact file exists after writing before proceeding to next
