# flash-excel

[![CI](https://img.shields.io/github/actions/workflow/status/neuraaak/flash-excel/01-ci.yml?style=flat&label=ci&logo=githubactions&logoColor=white)](https://github.com/neuraaak/flash-excel/actions/workflows/01-ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat&logo=github&logoColor=white)](https://github.com/neuraaak/flash-excel/blob/main/LICENSE)
[![uv](https://img.shields.io/badge/package%20manager-uv-DE5FE9?style=flat&logo=uv&logoColor=white)](https://github.com/astral-sh/uv)
[![linter](https://img.shields.io/badge/linter-ruff-orange?style=flat&logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![type checker](https://img.shields.io/badge/type%20checker-ty-orange?style=flat&logo=astral&logoColor=white)](https://github.com/astral-sh/ty)
[![test runner](https://img.shields.io/badge/test%20runner-pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)](https://pytest.org)

**flash-excel** — a Windows desktop utility to transform Excel/CSV files through declarative presets.

## 📦 Installation

Download the latest installer from the [Releases page](https://github.com/neuraaak/flash-excel/releases/latest) (`flash-excel-<version>-setup.exe`) and run it. The app auto-updates itself afterwards.

To run from source instead:

```bash
git clone https://github.com/neuraaak/flash-excel.git
cd flash-excel
uv sync
uv run python main.py
```

## 🚀 Quick Start

1. Launch the app and pick a source Excel/CSV file.
2. Choose an existing preset, or create a new one and add steps (rename, filter, cast types, add computed columns, …).
3. Run the preset — the transformed file is written next to the source (or to a folder you configure).

Presets are plain TOML files under `Documents\flash-excel\presets\`, so they can also be authored or version-controlled by hand.

## 🎯 Key Features

- **✅ Declarative presets**: chain rename, filter, cast, dedupe, sort and more steps in a reusable TOML file.
- **✅ Computed columns**: 16 Excel-style functions (`MAJUSCULE`, `CONCATENER`, `SI`, `ARRONDI`, …) evaluated in a sandboxed expression engine.
- **✅ Excel & CSV I/O**: reads/writes `.xlsx`, `.xls`, `.csv` via Polars + fastexcel/xlsxwriter.
- **✅ Auto-update**: signed updates (TUF) delivered from a private repository, no manual reinstall.
- **✅ Localized UI**: English and French.

## 🧪 Testing

```bash
# Install dev dependencies
uv sync

# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=src/flash_excel --cov-report=term-missing
```

## 🛠️ Development Setup

```bash
# Install in development mode with all dependencies
uv sync

# Install Git hooks
uv run pre-commit install
```

Source code uses a `src/` layout (`src/flash_excel`).

## 🚢 Build & Release

Building and releasing is **maintainer-only and local — not CI**. A fresh clone
builds and tests the app fine, but it cannot publish: the TUF signing keys and
the Cloudflare R2 credentials are deliberately kept out of the repository.

```bash
uv run build.py                 # version → compile → zip → installer → signed TUF release → publish
uv run build.py --no-upload     # everything but the publication stage
uv run build.py --skip-release  # rebuild an already published version (implies --no-upload)
uv run build.py --skip-build    # reuse dist/ as-is, to iterate on the installer
```

Publication is a stage of its own, run after the pipeline rather than inside
it. `build.py` ends on `publish_update()`, which transfers only the **public**
part of the signed TUF tree (`metadata/`, `targets/`, `withdrawn.json`) to R2;
the private keystore in `.tufup/keys` is never uploaded. The installer zip
stays local, `release_destination = "disk"` in `[tool.ezcompiler.upload]`.

Two helpers wrap the publication commands, so the project root and the
credentials in the gitignored `.env` do not have to be handled by hand:

```bat
.scripts\build\publish-update.cmd     :: public TUF tree -> R2
.scripts\build\publish-release.cmd    :: installer + zip -> GitHub Release
```

Both forward any extra flag to the command they wrap (`--yes`, `--draft`,
`--notes-file`, …) and both ask for confirmation first, the publication being
irreversible on the remote side.

The underlying [ezcompiler](https://github.com/neuraaak/ezcompiler) commands,
when a stage has to be run by hand:

| Command                        | What it does                                                 |
| ------------------------------ | ------------------------------------------------------------ |
| `ezcompiler tuf init`          | Create the signing keys and the repository skeleton (once)   |
| `ezcompiler tuf status`        | Show the state of the local TUF tree (read-only)             |
| `ezcompiler tuf refresh`       | Re-sign the metadata to push the expiry back, no new release |
| `ezcompiler tuf remove-latest` | Withdraw the latest version from the local tree              |
| `ezcompiler publish update`    | Publish the TUF tree to the update backend                   |
| `ezcompiler publish release`   | Publish the installer and the zip as a release               |

> ⚠️ **Never regenerate the signing keys.** New keys invalidate the trust
> anchor shipped with every installed client and break its auto-update
> permanently. A version already published must be withdrawn
> (`tuf remove-latest`) before it can be replaced — the tree refuses to
> re-release a withdrawn version under the same number.

## 📦 Dependencies

| Package      | Purpose                            |
| ------------ | ---------------------------------- |
| `pywebview`  | Desktop window (HTML/JS front-end) |
| `polars`     | DataFrame engine                   |
| `fastexcel`  | Fast Excel reading (Rust/calamine) |
| `xlsxwriter` | Excel writing                      |
| `pydantic`   | Preset & step validation           |
| `pyyaml`     | App config / theme files           |
| `ezplog`     | Logging                            |

## 📝 License

MIT License – See [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: [https://github.com/neuraaak/flash-excel](https://github.com/neuraaak/flash-excel)
- **Releases**: [https://github.com/neuraaak/flash-excel/releases](https://github.com/neuraaak/flash-excel/releases)
- **Issues**: [GitHub Issues](https://github.com/neuraaak/flash-excel/issues)

---

**flash-excel** – Declarative Excel/CSV transformations, one preset at a time.
