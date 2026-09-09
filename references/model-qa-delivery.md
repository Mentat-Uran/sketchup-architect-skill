# Model QA, iteration and delivery

## Two complementary reviews

Review the **architecture**: program completeness, gross/net budget, spatial dimensions and usable area, physical adjacency and circulation, floor-to-floor connections, daylight/privacy intent, likely load path, coherent envelope and facade, entrance/site relationship and consistency with user preferences. Separate verified dimensions from design assumptions and regulations not checked.

For a researched scheme, also review the [precedent handoff](precedent-research.md): can each important borrowed principle be traced to inspected evidence, and does its adaptation solve this brief's problem? Check the proposed thresholds, operating zones, shading, section or other affected geometry. Similar appearance is not validation; a source's claimed energy/acoustic performance does not become measured performance of the new model. Update the decision record when a principle is abandoned or modified during modeling.

Review the **model**: correct scale/datum, editable hierarchy, tagged assemblies with Untagged raw geometry, real openings, valid faces, appropriate face orientation, intentional solids, no duplicate/coincident surfaces, plausible intersections, no lost manual content, and useful scenes. Check a section through each stair and a representative facade opening. Bounding-box overlap is a clash candidate, not a proven clash; manifold geometry is not structural verification.

## Runtime audit

Load `scripts/model_audit.rb` through the authorized live Ruby Console and invoke `CodexSketchupArchitect.audit` for a whole-model inventory, or `save_audit('/fresh/absolute/model.json', root: actual_root)` for an owned top-level group. No app action occurs on file load. Saving an audit uses exclusive creation and never overwrites an existing file.

The audit reports version/platform, file/GUID, project/revision, entity counts, instance PID paths, semantic IDs, shared definitions, locks, transforms, expected solids, raw-geometry tags, loose/non-manifold edges and marked face quantities. It counts repeated component instances separately in their world transforms. Only mark assembly `expected_solid = true` if it should itself be a closed solid; a building parent containing nested groups is normally not one.

Mark counted horizontal faces as described in [continuity](project-continuity.md), then run `check_plan.py project.json --audit model.json`. Missing or extra quantity keys and mismatched identity/revision fail. The helper does not infer gross area from arbitrary model solids, detect all self-intersections, validate face normals globally, check occupied clearance, prove code compliance, or infer a circulation graph from walls. Those checks remain explicit visual/geometric work. Check proxies against built geometry; a correct proxy alone is not proof that a room exists.

Treat diagnostics by intent: loose construction/reference edges may be expected; a non-manifold wall marked as a solid requires investigation. Keep intentional exclusions with reasons. Do not auto-reverse all faces, erase all loose edges or purge all materials. Reject truncated audits, nil data or execution errors as incomplete.

## Physical checks beyond the ledger

Choose checks that fit the requested design depth and the actual risk. For a developed occupied building model, use the following evidence rather than substituting an intent graph or analytical proxy:

- **Rooms and routes:** compare actual finish/slab faces and wall/opening positions to the ledger. Inspect routes through door frames and open leaves, around columns and furniture, and through independent operating zones. When using a geometric free-space test, state detection-body width, elevation, included obstacles and exclusions; a centre-point route does not prove wheelchair access or evacuation capacity.
- **Stairs and vertical access:** inspect each core in section, including both runs, intermediate and floor landings, structural beams, slab openings and the roof exit. If using `Model#raytest` for headroom, start above the actual walking surface, include relevant overhead structure, identify the hit instance path, and sample landings and critical edges as well as the centreline. Record sample coverage and compare with the project's chosen criteria. Restore visibility/cut settings after diagnostics, including on exceptions; a clear ray through hidden structure is not a pass.
- **Vehicles, when provided:** verify the ramp mouth, apron, retaining walls, columns, occupied bays and connection to the site entrance. Use a declared vehicle envelope and turning path where a static plan cannot resolve the turn; distinguish a simplified swept rectangle from a vehicle-specific steering simulation. Check overhead clearance and vertical transitions separately.
- **Area and assembly reconciliation:** count roof stair enclosures and other late additions, distinguish external spaces from GFA, and state the gross/net/column deduction basis. A stair landing may already be formed by a floor slab; avoid duplicate coincident platforms. Trace multi-face-edge warnings to the affected assembly, including decorative text, rather than assuming every warning is structural or suppressing it globally.
- **Protection and environment:** inspect guardrail infill, opening edges, roof thresholds and usable landings, not merely the presence of a handrail. Daylight screening requires declared orientation, heights, receivers and sampling times; distinguish new-volume shading from an existing-baseline comparison and formal sunshine evaluation. Do not import a precedent's claimed performance as a result of this model.

Keep these measurements and their limitations beside the model, with affected semantic IDs/instance paths. Do not make one project's dimensions, sampling spacing, vehicle radius or numerical thresholds into a generic preset.

## Iterate against evidence

Maintain a short defect list with affected semantic IDs, severity, evidence, intended fix and recheck. Fix blocking spatial/model problems before material polish. Recheck the affected plan/section/area and any dependent elements after a change. Broaden testing only when shared definitions, structure, levels or envelope dependencies changed. Store a new revision and preserve previous checkpoints.

## Save and export

1. Complete/commit the modeling operation. Audit and record the active model identity and expected revision.
2. Save to a fresh, explicit `.skp` revision path with `model.save(path)`, or a deliberate user-requested overwrite. Check the boolean return, actual path, existence and plausible nonzero file size. Before major edits, follow the first-save versus save-copy branch in [Ruby modeling](ruby-modeling.md). Do not claim OneDrive synchronization from local file existence.
3. Export requested formats only. Read published `file.exporter_options.html` or stubs `pages/exporter_options.md` plus the format's Desktop Help. Check actual version/platform/license and option keys. `Model#export` may reject an extension or return false; there is no universal options hash valid for every exporter.
4. For PNG/JPEG, use `View#write_image` with explicit dimensions/options supported by the target; inspect image content for framing, blankness, clipping and missing tags/materials. For scenes, verify the correct camera/visibility/section properties were saved.
5. For geometry exports, verify files and material/texture sidecars and, where feasible, inspect or re-import into a separate document without disturbing the working model. IFC output requires meaningful classification/hierarchy if semantic interoperability is expected; an `.ifc` extension alone does not establish BIM quality.
6. When allowed and practical, verify a real disk reload: opening a path already open in Desktop may only focus that document. Save pending work successfully, then close/reopen that model or open a verified copy in another document. Never discard unsaved user work for this check. Compare project/revision, entity counts, measured quantities and scene inventory; switch representative plan, section and interior scenes to verify stored cameras, tags, active cuts and committed styles. If reopening was not done, state that limitation. Saving compatibility and visual/material fidelity are separate checks; do not promise unsupported downgrades.

For an animation request, create/update scenes correctly and try the documented Desktop export workflow. If unavailable, render a controlled camera sequence with `view.write_image` and encode locally using an available encoder. Inspect first, middle, last and transition frames **before** encoding, then verify playback/duration/resolution. Do not describe a camera path script as a delivered video.

## Completion report

Report the architectural result and the editable model path first. Include requested export links, key dimensions/areas, a concise explanation of the main precedent influences with direct source links or the project research record, assumptions and intentional simplifications, actual validation performed, remaining issues and current revision. Avoid presenting conceptual structural sizes as engineered design.

Distinguish evidence levels:

| State | What it establishes |
| --- | --- |
| Syntax/static pass | Files and references are well-formed; APIs were checked against local sources |
| Offline dry run | Design reasoning, arithmetic, retrieval and helper contracts exercised; no native geometry proof |
| Online precedent research | Listed project sources were actually opened and stated visual evidence inspected; facts, interpretations and evidence gaps remain distinguishable. This does not establish SketchUp execution or measured building performance |
| Runtime audit | Code executed in the observed SketchUp version and reported model measurements |
| Visual pass | Inspected views support the listed geometry and spatial claims |
| Saved/export verified | Actual files exist and specified persistence/import/playback checks passed |

`READY FOR LIVE TEST` is appropriate after static and offline checks pass with live checks explicitly pending. It must never be reported as “live modeling tested” or “ready for construction.”
