# Version compatibility and bounded recovery

The installed app, embedded Ruby, published API pages, stubs and release notes have separate versions. At each live session probe `Sketchup.version`, `RUBY_VERSION`, platform, relevant `respond_to?`/constants and actual exporter behavior. Record those observations. Do not treat system Ruby as SketchUp or a stub method as an available runtime method.

This skill's guarded runtime helpers target **SketchUp 2017+** (persistent IDs) using Ruby syntax parseable by Ruby 2.6. They have no dependency on 2025/2026-only APIs. This is a design compatibility target, not a claim of live tests on all versions. For older SketchUp adapt identity and inventory deliberately, or explain the unsupported helper requirement while continuing design work.

## Version-sensitive decisions

| Capability | Source-grounded handling |
| --- | --- |
| `Entities#build` / `EntitiesBuilder` | Introduced 2022. Feature-detect; ordinary Entities fallback only for topology not relying on builder-specific behavior |
| `Entity#persistent_id` and `Model#find_entity_by_persistent_id` | Introduced 2017, later expanded by type/overload. Use real runtime IDs and distinguish definition entities from instance paths |
| `Model#save_copy` | Documented since 2014. A never-saved model raised `Model must be saved before copying` in the 2025 live test. Branch on `model.path.empty?`: first `save`, otherwise `save_copy`; verify return, file and active path |
| Scene camera storage and Undo | Set active view camera, then `Page#update` with documented flags; no `Page#camera=`. In the 2025 live test, created pages survived a geometry abort. Track actual page/property changes separately; version-dependent Undo participation is not an application-wide rollback guarantee |
| Style persistence | Active style edits are temporary until `Styles#update_selected_style`; inspect shared-style users, commit intended edits, switch scenes and reopen to verify |
| Section deactivation | Set `Entities#active_section_plane = nil`; inspect cut direction visually from the saved camera |
| View screen coordinates | 2025 release notes describe logical-pixel changes. Do not mix GUI screenshot physical pixels, API logical coordinates and cached click positions |
| Singular transforms | 2026/2026.1 notes tighten errors for non-invertible transforms. Reject zero-scale transforms before mutation on all targets |
| PBR/material/environment and new export features | Probe the exact feature; preserve a meaningful basic-material fallback. Do not silently claim unavailable rendering fidelity |
| SKP save versions | Inspect the actual save API and Desktop Help. Modern versionless format and older version constants are not a guarantee that every feature survives on every old version |

Local evidence: `github/ruby-api-stubs/pages/ReleaseNotes.md`, generated `github/ruby-api-docs-gh-pages/file.ReleaseNotes.html`, per-method `Version`/`Known Bugs`, and `pages/exporter_options.md`. Stubs at this snapshot include 2026.1 placeholder build numbers; main-repository HTML includes 2016-generated pages. Prefer published `gh-pages` plus runtime probes. See [sources](local-sources.md).

## Failure handling

| Failure | Evidence and recovery |
| --- | --- |
| Missing method / wrong arguments | Stop the affected stage; inspect receiver class, actual runtime and exact method docs/version. Choose a documented fallback or remove the optional feature |
| `add_face` returns nil/duplicate-point error, tiny faces, wrong push/pull | Check coplanarity, self-crossing loops, repeated/near-coincident vertices, numeric cut deduplication, minimum detail scale and actual normal. Reproduce the smallest affected part in an isolated owned group; revalidate topology after tolerance-based cleanup |
| Boolean fails or changes operands | Restore the checkpoint/aborted operation; verify closed inputs and result type. Use explicit wall segments/opening geometry if adequate |
| Shared instances change unexpectedly | Stop; inspect definition instance paths, restore scoped work, make intended branch unique and revise only that branch |
| Abort during build | Read transaction report. After `aborted`, inspect geometry and separately compare scene/tag/style state before a changed retry; surviving pages must not accumulate on reruns. Name/order inventories do not detect every property change. After `rollback_failed`, preserve the model and inspect/recover from a checkpoint; state is uncertain. After `committed`/`post_commit_error`, inspect current revision and repair reporting/save instead of rebuilding |
| Crash or lost process during operation | A `prepared` report proves only intent. Check restored/recovered model and checkpoint; do not assume rollback or commit. Never overwrite the best recovery file blindly |
| Save/export false, unsupported extension, missing sidecars | Preserve in-memory model and valid `.skp`; inspect path/permissions/options/license, then retry only that export with a fresh path |
| CUA stale element / modal / busy state | Refresh observed UI and target. Never paste multiple commands into an uncertain console or force close unsaved models |
| Missing local library/cache | Check configured path and OneDrive availability; rebuild derived index if sources exist. Continue only the work supported by available evidence |

One failure should produce a hypothesis and changed action. After **two attempts with the same failure signature** in a stage, stop repeating it: inspect a minimal reproduction, choose another method, or report the external blocker. Continue independent design/offline work. A runtime exception needs report/console evidence, not only a screenshot of an idle window.

For issues, search exact methods/error terms in `issues-all.json`, then read the issue and its comments with the helper. Match OS/version and fix labels. Example #742 records active-group erasure crashes and a 2023 fix label, with comments about related exceptions; this supports checking `active_path` before mutation, not a claim that every erasure problem is fixed. Do not run issue reproductions in the user's model.

## Offline and live test separation

`scripts/offline_checks.py` validates source retrieval behavior, area/connectivity checks, helper loading/transaction contracts with test doubles, Ruby syntax and local link integrity. Test doubles do not model SketchUp's geometry kernel, Undo engine, UI or exporters. A live test should first use an isolated scratch model: create a small scheme with a real opening and measured floor, inspect/save/reopen, then revise only one owned assembly and confirm unrelated geometry remains. Obtain user direction only if that live scope is not already authorized.
