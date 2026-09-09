# SketchUp Architect

An evidence-led Codex skill for architectural precedent research, design reasoning, and editable SketchUp Desktop modeling.

[中文 README](README.zh-CN.md)

Demo: [Tangjianli spatial walkthrough](https://tangjianli-space.fxc060816.chatgpt.site)

## What it does

- turns an incomplete architectural brief into a reasoned program, area ledger, spatial organization, structure concept, envelope, circulation, and site relationship;
- researches real architectural precedents and records how their principles are adapted rather than copied;
- uses SketchUp's main-thread Ruby API for precise, semantic, editable model changes;
- separates offline/static checks from native SketchUp geometry, visual QA, save/reopen, and export evidence;
- provides small helpers for plan ledgers, source retrieval, model auditing, guarded revisions, and offline checks.

## Install manually

Clone this folder into the Codex skills directory:

```sh
git clone https://github.com/Mentat-Uran/sketchup-architect-skill.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/sketchup-architect"
```

Then invoke it with `$sketchup-architect` or let Codex discover it automatically.

## Install with an AI agent

Give your coding agent a request like this:

```text
Install the `sketchup-architect` Codex skill from
https://github.com/Mentat-Uran/sketchup-architect-skill.

Use the standard skill directory `${CODEX_HOME:-$HOME/.codex}/skills/sketchup-architect`.
Before changing an existing directory, inspect whether it is a Git checkout and
whether it has uncommitted changes; do not delete or overwrite user files.
After installation, run the repository's offline checks:

  python3 scripts/offline_checks.py
  ruby scripts/session_contract_test.rb

Report the exact installation path and the check results. Do not copy the
official SketchUp source corpus into the skill. Configure SKETCHUP_SOURCE_ROOT
only if exact local API lookup is needed.
```

An agent can perform the equivalent safe shell flow:

```sh
SKILL_ROOT="${CODEX_HOME:-$HOME/.codex}/skills/sketchup-architect"
if [ -e "$SKILL_ROOT" ]; then
  if [ -d "$SKILL_ROOT/.git" ]; then
    git -C "$SKILL_ROOT" status --short
    git -C "$SKILL_ROOT" pull --ff-only
  else
    echo "Refusing to overwrite existing non-Git directory: $SKILL_ROOT" >&2
    exit 1
  fi
else
  git clone https://github.com/Mentat-Uran/sketchup-architect-skill.git "$SKILL_ROOT"
fi

cd "$SKILL_ROOT"
python3 scripts/offline_checks.py
ruby scripts/session_contract_test.rb
```

Start a new agent session, or ask the agent to reload its available skills, after installation.

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
