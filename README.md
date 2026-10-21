# Flash-Excel

[![CI](https://img.shields.io/github/actions/workflow/status/neuraaak/Flash-Excel/01-ci.yml?style=flat&label=ci&logo=githubactions&logoColor=white)](https://github.com/neuraaak/Flash-Excel/actions/workflows/01-ci.yml)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue?style=flat&logo=materialformkdocs&logoColor=white)](https://neuraaak.github.io/Flash-Excel/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat&logo=github&logoColor=white)](https://github.com/neuraaak/Flash-Excel/blob/main/LICENSE)
[![uv](https://img.shields.io/badge/package%20manager-uv-DE5FE9?style=flat&logo=uv&logoColor=white)](https://github.com/astral-sh/uv)
[![linter](https://img.shields.io/badge/linter-ruff-D7FF64?style=flat&logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![type checker](https://img.shields.io/badge/type%20checker-ty-261230?style=flat&logo=astral&logoColor=white)](https://github.com/astral-sh/ty)
[![test runner](https://img.shields.io/badge/test%20runner-pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)](https://pytest.org)

![Logo](docs/assets/logo-min.png)

**Flash-Excel** is a Windows desktop app that cleans and reshapes Excel and CSV files with reusable presets, so a repeated spreadsheet chore becomes one click.

## 📦 Installation

1. Download `Flash-Excel-<version>-setup.exe` from the
   [latest release](https://github.com/neuraaak/Flash-Excel/releases/latest).
2. Run it. The installer works per user and does not ask for administrator
   rights.

Flash-Excel then keeps itself up to date: new versions are downloaded and
applied from inside the app.

## 🚀 Quick Start

1. Launch Flash-Excel and load one or more source files (`.xlsx`, `.xls`,
   `.xlsm` or `.csv`) — browse for them or drop them on the window.
2. Pick an existing preset, or create one and add steps: rename columns,
   filter rows, cast types, add a computed column, deduplicate, sort…
3. Preview the result, then run the preset.

Each result is written to `Documents\flash-excel\output\` as `<name>_clean`,
unless you choose another folder, name pattern or output format in the run
settings. Presets are plain TOML files in `Documents\flash-excel\presets\`.

The [Get started](https://neuraaak.github.io/Flash-Excel/get-started/) guide
walks through a first preset end to end.

## 🎯 Key Features

- ✅ **Reusable presets**: chain 12 step types (rename, select, drop, cast,
  replace, clean text, fill nulls, computed column, filter, deduplicate, sort,
  reorder) in a TOML file you can save, export and share.
- ✅ **Computed columns**: 16 Excel-style functions (`CONCATENER`,
  `MAJUSCULE`, `SI`, `ARRONDI`…) evaluated in a restricted expression engine.
- ✅ **Preview before running**: see the effect of a preset on the first 100
  rows before writing anything.
- ✅ **Batch processing**: run one preset on several files in a row; a failing
  file does not stop the others unless you ask it to.
- ✅ **Formats**: reads `.xlsx`, `.xls`, `.xlsm` and `.csv`; writes `.xlsx`,
  `.csv` or `.parquet`, with a configurable CSV separator and decimal mark.
- ✅ **Scheduling and launchers**: register a daily Windows Task Scheduler
  task, or save a `.cmd` launcher that runs the preset on demand.
- ✅ **Command line**: run presets headless from a script, with an exit code.
- ✅ **Shared preset folders**: list presets from team folders, read-only,
  alongside your own.
- ✅ **Signed automatic updates**: updates are verified with TUF signatures
  before they are applied.
- ✅ **Themes and languages**: several colour palettes with dark and light
  variants; English and French interface.

## 📚 Documentation

Complete documentation is available at **[neuraaak.github.io/Flash-Excel](https://neuraaak.github.io/Flash-Excel/)**

| Section                                                                        | Description                                         |
| ------------------------------------------------------------------------------ | --------------------------------------------------- |
| **[Get started](https://neuraaak.github.io/Flash-Excel/get-started/)**         | Install Flash-Excel and run a first preset          |
| **[Guides](https://neuraaak.github.io/Flash-Excel/tasks/)**                    | Files, presets, runs, automation, settings, updates |
| **[Concepts](https://neuraaak.github.io/Flash-Excel/concepts/)**               | Presets, step order, error handling, updates        |
| **[Reference](https://neuraaak.github.io/Flash-Excel/reference/)**             | Steps, functions, preset file, command line, paths  |
| **[Troubleshooting](https://neuraaak.github.io/Flash-Excel/troubleshooting/)** | Fixes for common problems                           |
| **[FAQ](https://neuraaak.github.io/Flash-Excel/faq/)**                         | Short answers to frequent questions                 |
| **[Release notes](https://neuraaak.github.io/Flash-Excel/release-notes/)**     | What changed in each version                        |

## 💻 CLI Usage

The same executable runs a preset without opening a window when it gets
`--preset`:

```bat
Flash-Excel.exe --preset "%USERPROFILE%\Documents\flash-excel\presets\clean.toml" --input january.xlsx february.xlsx --output D:\reports --format csv
```

Each input file is processed independently. The exit code is `0` when every
file succeeded, `1` when at least one failed and `2` on invalid arguments. See
the [command-line reference](https://neuraaak.github.io/Flash-Excel/reference/command-line/)
for every option.

## 📦 Dependencies

| Package      | Purpose                                  |
| ------------ | ---------------------------------------- |
| `pywebview`  | Desktop window hosting the web interface |
| `polars`     | DataFrame engine                         |
| `fastexcel`  | Fast Excel reading (Rust/calamine)       |
| `xlsxwriter` | Excel writing                            |
| `pydantic`   | Preset and step validation               |
| `tomli-w`    | Preset writing (TOML)                    |
| `pyyaml`     | App configuration and theme files        |
| `ezplog`     | Logging                                  |

## 🤝 Contributing

Development setup, tests, quality checks and the release process are described
in [CONTRIBUTING.md](CONTRIBUTING.md).

## 📝 License

MIT License – See [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [https://neuraaak.github.io/Flash-Excel/](https://neuraaak.github.io/Flash-Excel/)
- **Repository**: [https://github.com/neuraaak/Flash-Excel](https://github.com/neuraaak/Flash-Excel)
- **Releases**: [https://github.com/neuraaak/Flash-Excel/releases](https://github.com/neuraaak/Flash-Excel/releases)
- **Issues**: [GitHub Issues](https://github.com/neuraaak/Flash-Excel/issues)

---

**Flash-Excel** – Declarative Excel and CSV transformations, one preset at a time.
