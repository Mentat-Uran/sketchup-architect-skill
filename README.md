# SketchUp Architect

An evidence-led Codex skill for architectural precedent research, design reasoning, and editable SketchUp Desktop modeling.

Demo: [Tangjianli spatial walkthrough](https://tangjianli-space.fxc060816.chatgpt.site)

## What it does

- turns an incomplete architectural brief into a reasoned program, area ledger, spatial organization, structure concept, envelope, circulation, and site relationship;
- researches real architectural precedents and records how their principles are adapted rather than copied;
- uses SketchUp's main-thread Ruby API for precise, semantic, editable model changes;
- separates offline/static checks from native SketchUp geometry, visual QA, save/reopen, and export evidence;
- provides small helpers for plan ledgers, source retrieval, model auditing, guarded revisions, and offline checks.

## Install

Clone this folder into the Codex skills directory:

```sh
git clone https://github.com/Mentat-Uran/sketchup-architect-skill.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/sketchup-architect"
```

Then invoke it with `$sketchup-architect` or let Codex discover it automatically.

## Official SketchUp sources

The repository intentionally does not bundle SketchUp's official manuals, Git repositories, PDFs, issue archives, or the derived SQLite index. Configure a local source corpus when exact API lookup is needed:

```sh
export SKETCHUP_SOURCE_ROOT=/path/to/sketchup-modeler-source
cd "${CODEX_HOME:-$HOME/.codex}/skills/sketchup-architect"
python3 scripts/source_library.py status
```

Alternatively pass `--root /path/to/sketchup-modeler-source` before a subcommand. The source corpus should be obtained from official SketchUp/Trimble/GitHub sources and kept outside this skill.

## Validation

These checks do not launch SketchUp or claim native geometry/visual QA:

```sh
python3 scripts/offline_checks.py
ruby scripts/session_contract_test.rb
```

For a live task, use the current SketchUp Desktop session, inspect the active model, and verify the saved `.skp` and requested exports independently.

## Scope

This skill supports architectural concept and editable-model workflows. It does not certify structural engineering, accessibility compliance, planning approval, fire safety, or local legal compliance.

