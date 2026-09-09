# Precise, editable modeling through Ruby

## Prepare and inspect

The API exists inside SketchUp Desktop and must run on its main thread. A system Ruby syntax pass and the downloaded stubs cannot execute or validate geometry. Do not load `sketchup-api-stubs`, install a background command listener, open network ports, patch the app bundle, or add startup plugins as part of an ordinary modeling task. Use a reviewed task Ruby file loaded via the live Ruby Console when app operation is authorized.

Inspect `Sketchup.version`, `RUBY_VERSION`, `RUBY_PLATFORM`, active model path/GUID, root entities, `active_path`, selection, locks, layers, materials, definitions and scenes before changes. A macOS session may have multiple models; `active_model` can be nil. Keep a fresh identity token to prevent executing against the wrong document. Inspect the subtree you will change, not merely its name.

Read exact methods through `source_library.py`. Relevant sources: published `Sketchup/Model.html`, `Entities.html`, `Face.html`, `Group.html`, `ComponentInstance.html`, `Page.html`; stubs `pages/generating_geometry.md`; Developer Guides `article-lengths-and-units.html` and `article-traversing-the-model.html`; official Hello Cube tutorial.

## Coordinates and geometry

- Use explicit `Numeric#m`, `#mm` or `#inch` for dimensions. Numeric internal coordinates are inches; display units do not change geometry. Convert areas with `square_inches * 0.0254**2` and volumes with `cubic_inches * 0.0254**3`. Store JSON lengths in metres and convert exactly once at the boundary. Never use locale-formatted length strings as machine state.
- Define project axes/datum and north in the design record. Work in local group coordinates; accumulate parent-to-child transforms for world positions. For nested geometry use `parent_transform * instance.transformation`. `face.area(total_transform)` handles instance scaling; local area and world bounds are different quantities.
- Create groups first and add geometry inside them. Keep raw edges/faces on `model.layers[0]` (Untagged) and assign visibility tags to groups/components. Do not rely on the user's active tag.
- `add_face` can return nil for invalid geometry. Test the returned face before use, inspect its normal, and reverse intentionally before push/pull. The official tutorial notes a special downward normal on the ground plane: never assume point winding alone guarantees an upward extrusion.
- Keep closed solids at a suitable detail scale. Avoid tiny edges, coincident faces, zero thickness, non-coplanar loops and zero-scale transforms. If tiny geometry fails, simplify or build a scoped temporary component at larger scale and restore dimensions, then verify; do not scale the whole user model.
- Normalize numeric types before deduplicating wall/height cuts: Ruby `uniq` can retain both `0` and `0.0`. Coalesce near-equal cuts and polygon vertices using a tolerance appropriate to the intended detail, then recheck closed loops, holes and positive segment dimensions. Do not blindly round the whole model or erase narrow intentional features. Syntax checks cannot catch these topology failures.
- Build actual wall/roof openings with reveals, jambs, head and sill relationships. For repeated wall openings, explicitly segment wall solids around openings or use a tested solid workflow. A glass rectangle covering an opaque wall is not an opening. Boolean methods require appropriate solid inputs and version/license support; inspect results and consumed operands.
- Use components for true repetitions (windows, bays, furniture), groups for independently edited assemblies. Orient component axes consistently. `make_unique` before editing a single shared instance, including shared ancestor groups where necessary. Do not explode everything for convenience.

## Choose the construction method

`Entities#add_face/add_edges` merge and split geometry like native drawing tools; they suit local changes and operations that need intersections. For large already-resolved geometry on SketchUp 2022+, `Entities#build`/`EntitiesBuilder` reduces overhead but does not provide the same splitting/intersection behavior. Do not mutate its vertex collection outside the builder during a build block. A fallback to ordinary Entities is valid only when precomputed topology is compatible with both.

For a mesh workflow, use the documented `PolygonMesh`/`fill_from_mesh` rules and material restrictions. Do not trade editable architectural assemblies for one anonymous mesh merely to save execution time. Establish a detail/segment budget based on the task; reuse definitions and stage expensive operations. SketchUp API calls do not belong on worker threads.

## Transaction and revision helper

The bundled Ruby files define methods only when loaded. Inspect first, then invoke deliberately:

```ruby
load '/absolute/skill/scripts/model_session.rb'
load '/absolute/skill/scripts/model_audit.rb'
model = Sketchup.active_model
puts JSON.pretty_generate(CodexSketchupArchitect.audit)
```

In a task-specific revision file, invoke `CodexSketchupArchitect.run` with `project_id`, freshly inspected `expected_guid`, integer `expected_revision`, fresh absolute `report_path`, and `root_pid` for an existing project. The block receives `(model, root)`; implement this task's design using `root.entities`. Omit `root_pid` only for a new UUID at revision zero. The helper creates one owned group, checks identity and edit context, makes an existing root unique, starts one operation, yields, increments revision and commits. Failure before commit aborts; failure after commit is reported separately. The report directory must already exist.

The helper is an execution guard, **not a sandbox or automatic building generator**. Review the block's scope. Do not start/commit/abort another operation inside it; nested SketchUp operations implicitly interfere. Avoid transparent operations for ordinary modeling. Do not save files, export or start asynchronous callbacks inside the transaction. Group separate expensive stages into individual intentional revisions if needed; do not leave an operation open while waiting for user/GUI interaction.

For substantial changes, create and verify a fresh checkpoint before the transaction. `save_copy` requires a previously saved model in the tested Desktop version: when `model.path.empty?`, first use `model.save(fresh_path)`; otherwise use `model.save_copy(fresh_path)` to preserve the existing active path and its on-disk file, including when the model has unsaved changes. The explicit helper `CodexSketchupArchitect.save_checkpoint(path: checkpoint_path, expected_guid: model.guid)` implements this branch, rejects an existing destination, checks the return/file size/path, and returns a record to keep with the project. Inspect first and refresh the GUID after saving before calling `run`. A failed save may leave a partial file or a changed active path; inspect rather than deleting or overwriting automatically. A successful transaction is not a successful disk save.

Scene creation and style changes are not guaranteed to roll back with geometry. Before changing them, retain the actual target pages and the properties being changed; names alone are not unique identities. `run` records before/after scene name/order inventories and flags failure for scene review, but does not snapshot scene properties or erase pages. After an abort, compare actual pages, active cut, tags and style to the pre-stage state. Restore only changes attributable to this task. Keep geometry and view setup as separately recoverable stages where their Undo behavior differs; do not retry an entire build to repair surviving scenes.

Run `ruby -c revision.rb` outside SketchUp before loading it. Also inspect referenced APIs for version support, data values, nil returns, units and destructive scope. System Ruby may be older than embedded Ruby; prefer syntax compatible with the target rather than assuming the system interpreter represents it.

## Model organization and views

Use a readable hierarchy appropriate to the scheme: project/site/buildings/levels/assemblies, with meaningful role/level/space IDs. Keep analytical area surfaces and circulation guides separate from presentation geometry. Do not create duplicate floor quantity surfaces per repeated representation.

Create scenes from actual views. Set `model.active_view.camera = Sketchup::Camera.new(eye, target, up)` and save desired properties with `page.update(flags)`, e.g. `PAGE_USE_CAMERA`. `Page#camera=` is not a supported setter. Use documented constants rather than numeric flag magic. Ensure view up is not parallel to the viewing direction. Distinguish perspective exterior/interior scenes from orthographic plan/section views. Deliberately set tag/section/style visibility before saving those scene properties; avoid overwriting unrelated scenes.

Commit intended style edits with `model.styles.update_selected_style` before relying on scene switches or disk persistence. Check which other scenes share that style before editing it; use a separate style when needed to preserve them. For a deliberately shared inspection style, scenes may disable `use_rendering_options` while retaining their own camera, tag and active-section settings. Use documented rendering-option keys for the installed version. Switch away and back to verify the stored result, not just the current viewport.

Use `entities.active_section_plane = nil` to deactivate a cut; do not invent `SectionPlane#deactivate`. Inspect the retained half-space from the saved camera. In a floor plan, choose visibility for adjoining lower roofs and the accessible roof terrace explicitly; hidden floor plates can make a roof stair appear to float. Match framing to the actual viewport and inspect the entire intended scope again after reopening.

Finish with a runtime audit, targeted visual QA and verified save/export as described in [delivery](model-qa-delivery.md).
