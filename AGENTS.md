# AGENTS.md — flash-excel

Context file for AI agents. Read this before any code task.

---

## What this project is

**flash-excel** is a Windows desktop application that applies transformation pipelines
to Excel and CSV files using TOML-based configuration presets. The user loads a source
file, selects or creates a preset, and executes a sequence of typed steps
(rename, select, cast types, filter rows, clean text, deduplicate, sort…).

---

## Tech stack

| Layer       | Technology                                          |
| ----------- | --------------------------------------------------- |
| UI shell    | pywebview (native window hosting a local web page)  |
| Front-end   | Vue 3 (ESM browser build) + Tailwind, both vendored |
| Data engine | Polars + fastexcel (read) / xlsxwriter (write)      |
| Validation  | Pydantic v2 (discriminated unions)                  |
| Presets     | TOML                                                |
| Config      | YAML (`app.config.yaml`, `theme.config.yaml`)       |
| Logging     | ezplog                                              |
| Build       | ezcompiler (PyInstaller + Inno Setup + tufup/TUF)   |
| Toolchain   | uv, ruff, ty (pyright), pytest, import-linter       |

Python ≥ 3.13 · Windows-first · src layout (`src/flash_excel/`)

The UI is HTML/CSS/JS in a native window — **not** a native-widget GUI toolkit.
The table above is the whole stack: anything outside it is not a dependency of
this project, whatever an older note or a stale cache may suggest.

### Language conventions

This is a public repository: **write all new content in English** — commit
messages, docstrings, comments, documentation, and the source UI strings in
`locales/en.js` (`locales/fr.js` holds the French translations).

Some existing inline comments are in French, a leftover from an earlier phase.
Leave them alone: do not retro-translate a file you are editing for another
reason. New comments go in English, next to them if need be.

Commits follow Conventional Commits (`type(scope): imperative description`),
with a body explaining the *why* — see `git log` for the established tone.

---

## Module structure

```text
src/flash_excel/
├── core/
│   ├── models.py        # Pydantic discriminated-union models (Preset, steps)
│   ├── registry.py      # @action("name") decorator → REGISTRY dict
│   ├── pipeline.py      # run_pipeline() + compute_schema_at_step()
│   └── steps/           # One file per step: rename, select, drop, cast,
│                        #   replace, clean, fill, computed, filter,
│                        #   deduplicate, sort, reorder
├── io/
│   ├── loader.py        # File → Polars DataFrame (+ read_schema)
│   ├── writer.py        # DataFrame → output file
│   └── models.py        # I/O config models
├── presets/
│   ├── parser.py        # TOML → validated Preset
│   └── store.py         # Preset file storage / retrieval
├── ui/
│   ├── app.py           # pywebview bootstrap: create_window(js_api=…) + start()
│   ├── api.py           # FlashExcelAPI — the only Python↔JS bridge
│   └── web/             # Front-end served from disk via file:// URI
│       ├── index.html
│       ├── css/         # tokens.css (design tokens) + per-page sheets
│       └── js/
│           ├── api.js             # Thin wrapper over window.pywebview.api
│           ├── i18n.js            # Reactive t() + setLocale()
│           ├── steps-registry.js  # Canonical step order + i18n keys
│           ├── locales/           # en.js, fr.js (flat key → string maps)
│           ├── components/        # AppShell, FileLoader, ActionSteps, tables/
│           ├── pages/             # Processing.js, Presets.js
│           └── vendor/            # vue.esm-browser.prod.js, tailwind.js, icons.js
├── assets/config/       # Packaged config templates (app + theme)
├── config.py            # Load/save user config, theme resolution, installer locale
├── logs.py              # setup_logging() / log() — ezplog, rotating file
├── migration.py         # Moves legacy bin/ data to the user-data locations
└── paths.py             # Centralized path resolution (see "Where data lives")
```

---

## Core architecture pattern

### Registry + Discriminated Unions + Pipeline

Steps are defined as a **Pydantic discriminated union** on the `action` field.
Action names are **verb_noun and explicit** — never the short form:

```python
# core/models.py
class DropColumnsStep(BaseModel):
    action: Literal["drop_columns"]
    columns: list[str]


Step = Annotated[DropColumnsStep | FilterRowsStep | ..., Field(discriminator="action")]
```

Step implementations register themselves via decorator:

```python
# core/steps/drop.py
from flash_excel.core.registry import action


@action("drop_columns")
def drop_columns(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    return df.drop(columns)
```

The pipeline dispatches at runtime, raising `KeyError` on an unregistered action:

```python
# core/pipeline.py
for step in preset.steps:
    handler = REGISTRY.get(step.action)
    df = handler(df, **step.model_dump(exclude={"action"}))
```

**Registered actions** (12, all of them editable in the UI and covered by
`RECOMMENDED_ACTION_ORDER`): `rename_columns`, `select_columns`, `drop_columns`,
`cast_types`, `replace_values`, `clean_text`, `fill_nulls`,
`add_computed_column`, `filter_rows`, `deduplicate_rows`, `sort_rows`,
`reorder_columns`.

A step is only registered if `core/steps/__init__.py` imports its module, so a
new file must be added there too — `tests/unit/ui/test_steps_registry_parity.py`
enforces the whole chain (model, handler, editor, i18n keys in both locales).

`core/models.py` also exposes `RECOMMENDED_ACTION_ORDER` — a logical ordering used
for UI guidance only. The pipeline always executes steps in preset order.

**Extending the pipeline = 1 new model (added to the `Step` union) + 1 `@action`
function + 1 entry in `web/js/steps-registry.js` + a table component if it needs
an editor + the i18n keys in both locale files.**

### Schema tracking without data loading

`compute_schema_at_step(preset, step_index)` simulates structural transformations
(drop, select, rename, reorder) against a schema snapshot — no file I/O.
Used by the front-end to show the columns available at each step.

---

## pywebview + Vue workflow

### Startup sequence

```text
setup_logging(debug)       # ezplog → %LOCALAPPDATA%\flash-excel\logs\
migrate_legacy_presets()   # One-shot move of pre-1.3.0 bin/ data
consume_installer_locale() # Reads installer.ini once, then deletes the marker
FlashExcelAPI()            # Stateful bridge instance, one per app lifetime
webview.create_window(url=index.html.as_uri(), js_api=api, …)
webview.start(debug=…, icon=…)
```

Run with `--debug` to enable the pywebview devtools and verbose logging.

### The Python↔JS bridge

`ui/api.py` is the **entire** surface between the two worlds. Every public method
of `FlashExcelAPI` becomes `await window.pywebview.api.<method>()` in JS.

- Methods must be **synchronous** from Python's perspective — pywebview wraps them
  in promises on the JS side. Long work (running a pipeline) goes on a thread with
  a `threading.Event` for cancellation, as `_run_thread` / `_stop_event` do.
- **Return convention, always a dict:** `{"ok": True, "data": …}` on success,
  `{"ok": False, "error": "<message>"}` on failure. Never raise across the bridge.
- The local web page is loaded through `Path.as_uri()` — never a hand-built
  `file://` string, which breaks on Windows drive letters.

### Styling — design tokens, no hardcoded colors

Colors live as CSS custom properties in `web/css/tokens.css`
(`--surface_base`, `--surface_raised`, `--border_subtle`, `--accent_brand`,
`--text_primary`, `--semantic_error`…). Use `var(--token)`; never inline a hex or
`rgb()` value in a component or page sheet.

The same palette names are declared per theme in `assets/config/theme.config.yaml`
(one block per palette, `dark` and `light` variants) and resolved by `config.py`.
A new color means a new token in both places, not a literal at the call site.

### Translation system

All visible text goes through the i18n module — no literal strings in templates:

```js
import { i18n } from '../i18n.js';
// in a component: this.t = i18n.t
// in a template:  {{ t('nav.processing') }}
```

Keys are flat strings (`'app.title'`, `'steps.rename'`) and must be added to
**both** `web/js/locales/en.js` and `fr.js`. English is the source language;
a missing key falls back to English, then to the key itself.

---

## Where data lives

Nothing is written inside the installation folder — an auto-update replaces it.
All paths come from `paths.py`; never rebuild them by hand.

| What                | Constant               | Location                           |
| ------------------- | ---------------------- | ---------------------------------- |
| Config templates    | `CONFIG_TEMPLATES_DIR` | Packaged in `assets/config/`       |
| User config + theme | `USER_CONFIG_DIR`      | `%APPDATA%\flash-excel\`           |
| Logs                | `LOG_DIR`              | `%LOCALAPPDATA%\flash-excel\logs\` |
| Presets             | `PRESETS_DIR`          | `Documents\flash-excel\presets\`   |
| Install folder (RO) | `BIN_DIR`              | Alongside the executable           |

`LEGACY_APP_CONFIG` / `LEGACY_PRESETS_DIR` point at the pre-1.3.0 `bin/` locations
and exist only for `migration.py`.

---

## Development workflow

```bash
uv sync                    # Install everything (dev group, which includes test)
uv run python main.py      # Run the app
uv run pytest              # Run tests (coverage gate: 70%)
uv run ruff check .        # Lint
uv run ruff format .       # Format
uv run ty check            # Type check
uv run lint-imports        # Layer dependency contracts
```

Pre-commit hooks run ruff, ty, import-linter and a `_version.py` sync on every
commit (`uv run pre-commit install` once, after cloning).

A plain clone runs and tests fine. Only the auto-update path is inert: it is
guarded by `sys.frozen`, because the tufup client module is generated at build
time and bundled, so `check_update` / `apply_update` are no-ops outside the
packaged app.

Build and release are **maintainer-only and local, not CI**: `build.py` runs the
whole pipeline (version → compile → installer → signed TUF release → upload).
See its module docstring for the prerequisites — they include signing keys and
upload credentials that are deliberately **not** in the repository, so a fresh
clone can build and test the app but cannot publish a release.

If you do hold the signing keys: never regenerate them. New keys invalidate the
trust anchor shipped with every installed client and break their auto-update
permanently.

---

## Key constraints

- **Windows-only** target (registry lookups for Documents, `%APPDATA%` paths,
  Inno Setup per-user install).
- **No hardcoded colors** anywhere — always `var(--token)` from `tokens.css`.
- **No literal UI strings** — every visible string is an i18n key in `en.js` + `fr.js`.
- **Nothing written to the install folder** — use the `paths.py` constants.
- **Bridge methods return `{ok, data|error}`** and never raise across the boundary.
- **Schema-aware UI**: when building step editors, use `compute_schema_at_step()`
  to populate column dropdowns, not the raw source file schema.
- **Layer contracts** (enforced by import-linter, see `pyproject.toml`):
  `ui` → `presets`/`io` → `core` → `migration` → `config` → `logs` → `paths`.
  `presets` and `io` are independent siblings; `core` must never import `ui`.
