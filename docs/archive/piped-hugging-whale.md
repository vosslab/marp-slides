# One application CLI: `deck_tools.py` and `slide_lib/`

## Context

Two complaints, both about entry points and names, not about behavior.

1. Every script in `tools/` is a thin wrapper that imports `marp_lib`, and six also hand-patch
   `sys.path` first (`tools/odp_to_djot.py:8`). That breaks the `tools/` policy -- standalone
   utilities, no imports from repository packages -- and it exists only because the repo has no
   application CLI. `docs/REPO_STYLE.md` says primary product workflows belong in the application
   CLI, with `tools/` and `devel/` as thin entry-point locations.
2. `tools/marp_to_odp.py` exists but nothing named djot-to-ODP does, so Djot reads as unable to
   reach ODP. It already can: `marp_lib/native_export.py:32` maps `.md` -> `marp_parser.parse_deck`
   and `.djot` -> `djot_parser.parse_deck`, and both run through one
   `marp_lib.terminal_output.run_build`. Only the command names say "marp".

The repo is pre-production with no external callers, so this fixes the boundary rather than layering
compatibility over it: one CLI owns user workflows, one package owns behavior, and the package name
stops claiming a Marp-only project.

## Decisions taken (confirmed with user)

- Root CLI `deck_tools.py` with subcommands. Root script budget
  (`tests/test_root_script_budget.py`) warns at 5 counted root scripts, fails at 7; this goes 2 -> 3.
- No `tools/` wrappers and no `launchers/` folder. The CLI is the sole entry point, with
  `build_slides.sh` kept as the folder-build convenience. `tools/` is deleted (its nine scripts are
  all wrappers); `TOOLS_README.md` moves to `docs/` as the placement policy it actually is.
- `git mv marp_lib slide_lib`. The package owns the Djot parser, native model, layouts, animation
  backend, and importers; Marp is one front end inside it (`slide_lib/marp_parser.py` stays
  correctly named). Distinct first word from `deck_tools.py`, so the root listing reads clearly.
- `build` is format-neutral and dispatches on suffix. No per-format verbs.

## Command surface

```bash
source source_me.sh && python3 deck_tools.py build genetics/djot/lect01b.djot -f odp
source source_me.sh && python3 deck_tools.py build genetics -f all
source source_me.sh && python3 deck_tools.py import genetics/lecture.odp
source source_me.sh && python3 deck_tools.py import genetics/lecture.pptx -t marp -o genetics/lecture.md
source source_me.sh && python3 deck_tools.py lint genetics/djot
source source_me.sh && python3 deck_tools.py visibility genetics/lecture.odp
```

`import` picks the importer from source suffix plus `--to`: `.odp`+djot -> `odp_to_djot`,
`.pptx`+djot -> `pptx_to_djot`, `.odp`+marp -> `odp_to_marp`, `.pptx`+marp -> `pptx_to_marp`.
Default `--to djot`, so the modern route is what you get by typing less. That, plus a `build` that
never says "marp", is the fix for complaint 2.

## Verified before planning

- `marp_lib/native_export.py:76-98` `discover_decks` already owns folder traversal, direct-child
  scope, `.djot` acceptance, `.md` gating on `marp: true` front matter, and the empty-folder error.
  `run_build` already returns an exit status and prints failures
  (`marp_lib/terminal_output.py:114-162`). `build` is therefore a rename of an existing entry point;
  this plan adds no traversal, format-inference, or output-path behavior.
- No packaging surface exposes the old script names: the repo has no `pyproject.toml`, `setup.py`,
  `setup.cfg`, or `Makefile`, so there are no console entry points to break. Every reference to
  `marp_export` / `marp_to_odp` / `marp_to_pptx` is in this repo's docs, `build_slides.sh`, and the
  two `tests/e2e/` runners.
- 60 tracked files mention `marp_lib`; none of them are `tests/conftest.py`, `devel/`, or
  `.gitignore`, so the package rename is confined to imports, tests, and prose.

## Changes

### 1. Root CLI `deck_tools.py`

Shebang `#!/usr/bin/env python3`, executable bit set (`tests/test_shebangs.py` enforces the pairing),
docstring, and nothing else:

```python
import slide_lib.cli

if __name__ == "__main__":
	raise SystemExit(slide_lib.cli.main())
```

It sits at the repo root, so Python puts the repo root on `sys.path` for it and the import resolves
with or without `source source_me.sh`. Documented invocation stays the repo standard,
`source source_me.sh && python3 deck_tools.py ...`, which is also what puts LibreOffice and Jotdown
on PATH.

### 2. New `slide_lib/cli.py`

Owns `parse_args(argv)` (one `ArgumentParser`, `add_subparsers(dest="command", required=True)`) and
`main(argv: list[str] | None = None) -> int`; the `argv` parameter exists so tests can drive it
without touching `sys.argv`.

Repo argparse rules: short plus long flag with explicit `dest=` -- `-f/--format` -> `output_format`
(choices `all`, `pptx`, `odp`, `pdf`, default `all`), `-o/--output` -> `output_file`, `-t/--to` ->
`target_format` (choices `djot`, `marp`, default `djot`). Lint keeps its existing
`--native-executable`, `--native-argument`, `--require-native`. No new tunables.

Dispatch calls reusable functions, never another module's `main()`:

| Subcommand | Calls |
| --- | --- |
| `build` | `slide_lib.terminal_output.run_build(input_path, output_format)` |
| `import` | the `run_import` chosen by `select_importer(suffix, target_format)` |
| `lint` | `slide_lib.djot_lint.run_lint(...)` |
| `visibility` | `slide_lib.importers.odp_visibility.run_visibility(...)` |

Return contract: `main()` forwards the integer status from operations that own one (`run_build`,
`run_lint`) and returns 0 after a successful void operation (`run_import`, `run_visibility`). Two
error classes stay separate: a CLI usage error -- a source suffix `import` does not accept -- is
reported as a one-line message on stderr with status 2, while genuine conversion and runtime
failures keep their existing exception and reporting behavior unchanged.

### 3. Extract reusable run functions (mechanical)

Each importer has `parse_args()` + `main()`, with `main()` also holding the default-output choice and
the summary printing (`marp_lib/importers/odp_to_djot.py:53-64`). Calling those `main()`s from the
CLI would re-parse `sys.argv`, so split each and delete the now-unreachable standalone
`parse_args()`/`main()`/`__main__` blocks, since the CLI is the only caller:

- `odp_to_djot.py`, `pptx_to_djot.py`, `odp_to_marp.py`, `pptx_to_marp.py`: add
  `run_import(input_file: pathlib.Path, output_file: pathlib.Path | None) -> None` holding the
  current `main()` body.
- `odp_visibility.py`: same split into `run_visibility(...)`.
- `djot_lint.py`: add `run_lint(sources, native_executable, native_arguments, require_native) -> int`
  holding the body of `marp_lib/djot_lint.py:180-198`, returning a status instead of raising
  `SystemExit`.

Preserve exactly: the default output path (`input.with_suffix(".djot")` / `".md"`), every printed
summary line and its wording, stdout versus stderr routing, the lint 0/1/2 statuses, and which
exceptions propagate. Extraction only -- no reworded messages, no new flags, no changed defaults.
The conversion cores (`convert_odp`, `convert_pptx`, `lint_paths`) are untouched.

### 4. Package rename and `tools/` removal

- `git mv marp_lib slide_lib`, then update every `import marp_lib...` / `from marp_lib import ...`
  site across the package, `tests/`, and `tests/e2e/`. `slide_lib/marp_parser.py` keeps its name; it
  really is the Marp front end.
- `git rm` the nine `tools/*.py` wrappers. `git mv tools/TOOLS_README.md docs/SUPPORT_SCRIPT_PLACEMENT.md`
  so the placement policy survives without an otherwise-empty folder, and update its text to describe
  the settled boundary: application CLI owns workflows, `slide_lib/` owns behavior, `tools/` is for
  future standalone user utilities, `devel/` for repository engineering.
- `devel/DEVEL_README.md`: one short section pointing at that same classification so the two policy
  docs agree.

### 5. `build_slides.sh`

`exec python3 "$repo_root/deck_tools.py" build --format all "$1"`, with usage text naming
`deck_tools.py build` and stating decks may be `.md` or `.djot`.

### 6. Callers and docs

- `tests/e2e/e2e_all_native_layouts.py:275` and `tests/e2e/e2e_djot_native_layouts.py:205` invoke
  `tools/marp_export.py`; switch both to `deck_tools.py build ... --format pdf`.
- `README.md` quick start and migration blocks; `docs/USAGE.md` (every command block);
  `docs/PIPELINE.md` component tables (lines 41-44, 57-59); `docs/INSTALL.md:38`;
  `genetics/djot/README.md` lint commands; `docs/DESIGN_DECISIONS.md:506,518` owner lines.
- Then sweep once for stragglers: `grep -rn "tools/\|marp_lib" ` over tracked files, excluding
  `graphify-out/` and `OTHER_REPOS/`, and fix whatever the enumerated locations missed.
- `docs/CHANGELOG.md`: entry under today's date under `### Additions and New Features`,
  `### Behavior or Interface Changes`, `### Removals and Deprecations`, and
  `### Developer Tests and Notes`.
- `docs/HUMAN_GUIDANCE.md`: the stated guidance in the user's own words -- `tools/` scripts must not
  import repository packages; a main launcher belongs at the repo root; Djot-to-ODP must be obvious;
  the pre-production window is for fixing boundaries rather than adding compatibility layers.
- `docs/DESIGN_DECISIONS.md`: one entry for the settled boundary (`deck_tools.py` owns user
  workflows, `slide_lib/` owns behavior, no wrapper folders), `Owner` naming `deck_tools.py` and
  `slide_lib/cli.py`.

## Tests

Two additions in a new `tests/test_cli.py`, both fast, offline, `tmp_path`-only, one or two asserts
each:

- `select_importer` returns the djot importer for `.odp` and `.pptx` by default and the marp
  importer under `-t marp`; an unsupported source suffix raises the CLI error instead of returning
  something. This is real branching logic that could plausibly be wrong.
- `main(["build", str(deck), "-f", "odp"])` reaches `run_build` with the parsed path and format,
  using a monkeypatched recorder so no LibreOffice runs. This proves arguments actually arrive at
  the operation.

Nothing else. No tests of subcommand name lists, option counts, help text, `--to` choices already
enforced by argparse, or the wrapper shape of `deck_tools.py` -- those are the brittle shapes
`docs/PYTEST_STYLE.md` rejects. Existing `tests/test_terminal_output.py` and
`tests/test_marp_export.py` call `run_build` directly and need only their import lines updated for
the package rename.

## Verification

```bash
source source_me.sh && pytest tests/
source source_me.sh && python3 deck_tools.py --help
source source_me.sh && python3 deck_tools.py build genetics/djot/<one_deck>.djot -f odp
source source_me.sh && python3 deck_tools.py build genetics/<one_marp_deck>.md -f odp
source source_me.sh && python3 deck_tools.py lint genetics/djot
```

The two builds are the central evidence: one `.djot` and one `.md` through the same format-neutral
command, each producing its `output/odp/` artifact. `./build_slides.sh genetics` and the two
`tests/e2e/` runners are one-time integration evidence on top of that, not substitutes for it, and
stay outside the pytest lane per `docs/E2E_TESTS.md`.

`pytest tests/` must stay clean on the gates this touches: `test_root_script_budget.py` (silent at 3
counted root scripts), `test_shebangs.py`, `test_support_dirs_not_imported.py`,
`test_pyflakes_code_lint.py`, `test_function_typing.py`, `test_import_requirements.py`,
`test_markdown_links.py`, `test_source_file_line_limit.py`.
