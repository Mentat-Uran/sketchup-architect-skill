# SketchUp Desktop and Computer Use

Use Computer Use for application/document selection, Ruby Console access, menus/dialogs, export UI when required, and visual inspection. Use Ruby for numeric geometry and repeated operations. Respect a user's no-launch/no-Computer-Use scope even if SketchUp is already running: an offline dry run must not query or control the live app.

## Connect only for an authorized live task

Discover the current Computer Use capability and read its tool documentation. In this installation the available surface is `mcp__cua_repl`; follow the documented first-call entry point and subsequent returned APIs. Do not store fabricated CUA method signatures, AppleScript UI recipes, accessibility indices, screenshots or fixed coordinates in a reusable script. A successful read-only bundle-version check does not establish the running model or GUI state.

When live work is authorized, select the actual SketchUp application; inspect current windows, document name and unsaved state. Bring the correct document forward, resolve dialogs, and confirm active model identity through a small Ruby inspection before modeling. Do not close or discard unrelated unsaved work to obtain an empty model. Use a new document only when the task calls for one and the GUI can preserve current work.

On macOS, the Ruby Console may be under Extensions → Developer → Ruby Console (localized labels vary). Use the current accessibility tree or menu observation. The console is a window in SketchUp, not a separate application. Refresh UI state after menu changes, dialogs or an invalid/stale element error.

Write reviewed Ruby into an absolute project path, syntax-check it, then enter a short literal `load` command into the observed console input. Quote paths with a proper Ruby string literal (for example JSON encoding of a path), not shell interpolation. Read console output and the on-disk report after execution. A keypress returning success does not prove Ruby executed. Do not queue another command while SketchUp is busy.

## GUI actions that need observation

- Selecting and framing the correct model and owned project group.
- Inspecting Outliner hierarchy, entity info and tag visibility.
- Setting/reviewing section cuts, plan views, scenes, styles and materials.
- Saving or exporting via a dialog when the corresponding runtime API/format is unavailable.
- Inspecting geometry from independent views and reading actual dimensions.

Use the matching local Quick Reference PDF for modifiers. The downloaded cards are 2026; installed SketchUp may differ and user shortcuts may be customized. Mac uses Option/Command in places where Windows uses different keys. Do not paste keystrokes from the wrong platform. Menu/accessibility observations override assumed shortcut defaults.

## Visual review sequence

Frame the project; inspect an exterior perspective for proportions and overall completeness, orthographic plan for boundaries and doors, sections for heights/slabs/openings/stairs, and eye-level views for entrances and interior use. Toggle monochrome to reveal reversed faces and z-fighting, and show analysis/structure tags when checking area or load paths. Use a known dimension/scale object to detect inch/metre errors. Restore a useful presentation view after review.

Capture enough evidence to show important claims without filling the output directory with redundant screenshots. Ruby `view.write_image` provides reproducible images; also inspect the visible Desktop state when needed to establish that geometry is in the right live document. Follow current tool restrictions for captures; do not use voice-only screen tools in a text task.

## Recover without repeated blind actions

After stale UI elements, refresh once and locate the current target. After a modeling exception, read the report and inspect model state before any retry. For an unresponsive app, do not keep pasting commands or force quit unsaved work. For licensing, missing application or unresolvable modal state, finish the offline design/code work and report the concrete external blocker. Do not install extensions or change security settings just to make a GUI sequence work.
