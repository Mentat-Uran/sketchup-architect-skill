---
name: sketchup-architect
description: Research real architectural precedents, design buildings from sparse briefs, and create, inspect, revise, save, and export editable SketchUp Desktop models. Use for building case studies, architectural concepts, space planning, massing, site relationships, and continued changes to existing SketchUp designs. Combines source-backed precedent analysis, architectural reasoning, local official SketchUp documentation, precise Ruby API modeling, and Desktop visual review.
---

# SketchUp Architect

For installation and the user-facing operating contract, read [USAGE.md](USAGE.md) when the task involves setup, evidence, live execution, or delivery.

Turn the user's brief into a coherent architectural proposal and an editable SketchUp model. Explain how people use the building and how its spaces, circulation, structure, envelope, and site fit together. A decorated exterior box is not a complete building scheme. Match detail and deliverables to the requested stage; do not expand a massing study into construction documentation.

## Start with the task and evidence

1. Decide whether this is a new scheme, a design study, or a revision. Read project notes and model inventory before proposing changes. Preserve the user's constraints, approved decisions, and existing content.
2. For a new or materially changed scheme, read [architectural design](references/architectural-design.md). Fill reasonable gaps with explicit, reversible assumptions and proceed. Ask only when missing information prevents a useful or safe next step.
3. When the task involves architectural scheme design, **default to online research of several relevant real buildings before generating the scheme or modeling it**. Read [precedent research](references/precedent-research.md). Derive searches from the brief, building type, site, scale and core design questions; choose depth and count to resolve those questions. Verify sources and available drawings, compare strategies, then transfer principles with explicit adaptations rather than copying a building's form. Respect an explicit offline/no-research request. Pure implementation, dimension-only edits, export and API troubleshooting do not require a new precedent search.
4. Read [project continuity](references/project-continuity.md) when starting a project or modifying an existing one. Save the brief, precedent evidence, design rationale, quantitative ledger, and revisions beside the model, not inside this skill. For design revisions, reuse sound earlier research and supplement it for changed questions instead of repeating the entire study.
5. Use [local sources](references/local-sources.md) to retrieve exact APIs and relevant official guidance. Run `python3 scripts/source_library.py status` from this skill directory. The external library location is in `references/source-config.json`, overridable with `--root` or `SKETCHUP_SOURCE_ROOT`. This helper retrieves SketchUp technical documentation only; use web tools for building precedents. It never launches SketchUp or downloads sources.

## Design, then build in inspectable increments

- Start from the research synthesis: state which evidenced principles are adopted, adapted or rejected, why they suit this brief, and how they will be tested in the plan/section/model. Establish program and gross/net area accounting, adjacency and access, site orientation, buildable envelope, levels and section, structural concept, openings, facade rhythm, materials, and outdoor space. Choose geometry for these reasons rather than starting from a building preset.
- Resolve the largest uncertainties with a compact plan/section/volume comparison when useful. Select a workable direction autonomously unless the user wants alternatives or approval. Record what was chosen and why.
- Calculate dimensions and area budgets before detailed geometry. `scripts/check_plan.py project.json` checks the flexible area and circulation ledger described in [project continuity](references/project-continuity.md). It does not generate designs or prove geometric/code compliance.
- Read [Ruby modeling](references/ruby-modeling.md) before authoring or executing modeling code. Build site and levels, then spatial/structural organization, envelope and real openings, circulation, finishes, and views. Use named groups/components and semantic IDs so later changes remain local.
- Precision and repetition belong in task-specific Ruby run **inside SketchUp's main thread**. System Ruby and API stubs are for syntax/documentation checks only. Never load stubs in the running application.
- Use [Desktop operation](references/desktop-operation.md) for actual app control and visual QA. Discover the available Computer Use tool and read its current API documentation; do not assume old selectors or signatures. Respect analysis-only, dry-run, no-launch, and no-Computer-Use instructions.

## Verify and revise

Read [model QA and delivery](references/model-qa-delivery.md) before judging a model complete. Check both architecture and geometry, including whether transferred precedent principles actually work under this project's constraints. Verify measurable claims against actual model data and inspect plan, section, exterior, and important interiors. A nonempty file, successful Ruby return, or `manifold?` alone does not prove success.

`scripts/model_audit.rb` provides a read-only runtime inventory and limited geometry diagnostics. `scripts/model_session.rb` provides an explicit transaction guard, project identity/revision checks, first-save-aware checkpoints, scene inventories and failure reporting. Loading either file defines helpers only; it does not launch SketchUp or modify a model. Use them deliberately as documented in the Ruby reference. They do not sandbox arbitrary Ruby, guarantee scene/style rollback, or replace physical access and clearance checks.

For API mismatches, partial runs, exporter errors, or Desktop interruptions, use [compatibility and recovery](references/compatibility-recovery.md). Investigate the exact failure in local API docs, issue records and release notes; do not blindly rerun a whole build.

For continued changes, inspect the current model again, resolve IDs in their instance paths, preserve manual edits, make shared definitions unique when required, and change only affected elements. Reconcile both the model and the project ledger after each accepted revision.

## Finish

Save a versioned `.skp` and requested exports, inspect the written files, and report the outcome, location, key precedent sources and their influence, measured checks, assumptions, and remaining limitations. Keep conceptual structural and accessibility assumptions distinct from verified engineering or local legal compliance; neither precedents nor SketchUp documentation can certify a building design.

When live execution is prohibited or unavailable, deliver design/code/validation artifacts and label geometry, visual QA, save, and export as **not live-tested**. `scripts/offline_checks.py` runs deterministic helper checks without SketchUp. Passing it means readiness for a live test, not a completed model.
