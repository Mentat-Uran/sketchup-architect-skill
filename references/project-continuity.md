# Project records and continuous modification

Store project artifacts in the user's output/workspace directory. Use a short `design.md` for brief, assumptions and rationale, `project.json` for quantities/identity, task-specific Ruby revision files, an `audit/` folder, and versioned model/exports. Combine files for a small study. Do not write project state into the installed skill or original source library.

## Precedent evidence and design decisions

For scheme design, keep `precedents.md` beside `design.md` (or combine them for a small task). Use the record described in [precedent research](precedent-research.md): actual opened sources, building identity/status, relevant evidence and gaps, comparison, and transferable principles. Keep source URLs and access dates; distinguish source facts, observations from drawings, interpretations, and proposed decisions. Do not store a growing case/image collection inside the skill or its official API library.

Give cases, source records and significant design decisions compact project-local IDs when useful, such as `P01`, `S01`, `D01`. In `design.md`, link each major adopted principle to its case/source, adaptation, affected spaces/assemblies and planned validation. Optional `project.json` fields may link the research file and decision IDs; no new mandatory geometry schema is required. Record deliberately rejected strategies as well as adopted ones.

On a follow-up design change, review which decisions and case assumptions still apply. Research new questions or refresh weak/outdated evidence as needed; preserve justified decisions and user-approved changes. Do not rerun searches for a mechanical edit or replace the user's scheme just because another precedent is attractive.

## Identity and ownership

Use one generated project UUID, independent of `model.guid` (the model GUID changes after modification and save). Name a dedicated top-level group and set attributes in dictionary `sketchup_architect`:

- root: `project_id`, `revision` (integer), `role = project_root`;
- editable elements: `semantic_id` (stable within an instance path), `role`, optional `level_id`, `space_id`, `expected_solid`;
- quantity faces: `quantity_kind = gfa` or `net`, `level_id`, and `space_id` for net areas.

Use semantic IDs such as `level-01/cafe/wall-east`; the vocabulary may vary with the design. Record persistent ID paths for actual instances in `project.json` after runtime inspection. Persistent IDs can disappear when entities are rebuilt; semantic IDs and reviewed instance paths provide recovery. Names alone are not identity. Component definition entities are shared: a definition-level semantic ID may legitimately appear in several distinct instance paths.

The audit measures marked **faces**, not group bounding boxes. Use exactly one horizontal counted floor boundary surface per counted zone, with holes where floors are absent. Mark real slab top faces or dedicated area-proxy faces on a hidden analysis tag. Never mark both representations or both sides of a slab. Net surfaces need the corresponding `space_id`. Quantity proxies are a checking representation; compare them visually and dimensionally against physical geometry.

On an unowned existing model, inventory first and adopt only the target scope. Do not relabel or wrap all content just to satisfy this convention. Selective revision helpers may be adapted to a reviewed existing group; unrelated material, tags, scenes, locked content, imported context and manual geometry stay intact.

## Flexible machine-readable ledger

`check_plan.py` accepts this small contract; extra fields are retained/ignored, so site polygons, room geometry, material schedules, decisions or structural strategy can be added freely. It never makes design geometry. Areas are in m² and elevations/dimensions in metres regardless of the user's display units.

```json
{
  "schema_version": 1,
  "project_id": "project-uuid",
  "revision": 0,
  "units": "m",
  "target_gfa_m2": 120,
  "tolerance_fraction": 0.03,
  "levels": [
    {"id": "L0", "elevation_m": 0, "gfa_m2": 120, "allowance_m2": 20}
  ],
  "spaces": [
    {"id": "entry", "level": "L0", "area_m2": 10, "kind": "circulation", "entry": true},
    {"id": "studio", "level": "L0", "area_m2": 75, "kind": "occupied"},
    {"id": "support", "level": "L0", "area_m2": 15, "kind": "service"}
  ],
  "connections": [
    {"from": "entry", "to": "studio", "kind": "door"},
    {"from": "entry", "to": "support", "kind": "door"}
  ],
  "assumptions": ["Area is conceptual gross floor area; local measurement rules unverified."]
}
```

Count non-overlapping enclosed spaces once. `allowance_m2` contains only unmodeled wall/structure or other **explicitly described** residual area, not corridors already listed as spaces. Courtyards/terraces outside GFA use `external: true` and do not count toward balance. Entry nodes can be external. `requires_access: false` is reserved for non-occupiable voids or intentional excluded elements with a reason. Connections are undirected access intents; a cross-level connection must use `stair`, `lift`, or `ramp`. The checker tests connectivity, not travel distances, accessible dimensions, capacity or exit independence.

Run:

```sh
python3 scripts/check_plan.py /absolute/project/project.json
python3 scripts/check_plan.py /absolute/project/project.json --audit /absolute/project/audit/model.json
```

With `--audit`, the checker compares runtime measured GFA per level and net area per space with the ledger, checks project/revision identity, and propagates audit errors. Missing measurement data fails instead of being treated as zero or success. Without an audit the result remains `plan_only`. A manual review still checks site fit, overlap, physical route continuity and quantities against built elements.

## Revision protocol

1. Read the latest ledger, revision note and live inventory. Record file path, GUID as a snapshot token, root PID, project UUID and revision. Inspect `active_path`, locks and relevant shared instances.
2. Interpret the requested delta and its dependencies (roof changes may affect walls, section, drainage and views; enlarging a room may affect neighbors, doors, area and structure). For a material design change, review the relevant precedent decisions and supplement research for newly unresolved issues before revising the scheme.
3. Compare owned elements against saved inventory and manual edits. A revision number is not a complete fingerprint. If an affected element was edited manually, preserve or integrate the edit; ask only when user intent cannot be inferred.
4. Save a checkpoint copy before a substantial live revision. Use a new path and verify `save_copy` and file size. For unsaved/user-changed files preserve current in-memory work, not just the old disk file.
5. Execute a scoped transaction. Do not delete the entire model, regenerate unrelated components, or purge definitions/materials globally. Make the edited instance and any shared ancestors unique when the change is instance-specific.
6. Audit, inspect views, reconcile the ledger, save the new revision and record the semantic IDs changed, model path, source evidence and unresolved items. Save/export failures do not mean the model transaction failed; recover the appropriate phase.
