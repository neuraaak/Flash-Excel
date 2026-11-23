# Contributing to Flash-Excel

Thanks for helping. This guide covers the development setup, the quality gate,
the documentation site and the maintainer-only release process. Project
conventions and architecture rules for code changes are in
[AGENTS.md](AGENTS.md).

## 🛠️ Development Setup

Requirements: Python 3.13+, [uv](https://github.com/astral-sh/uv), and Git.
Windows is the target platform; the test suite also runs on Linux in CI.

```bash
git clone https://github.com/neuraaak/Flash-Excel.git
cd Flash-Excel

# Install the app and every development group (test + docs + tooling)
uv sync

# Install the Git hooks (ruff, ty, import-linter, _version.py sync)
uv run pre-commit install

# Run the app (run-debug adds the devtools and verbose logs)
uv run poe run
uv run poe run-debug
```

Source code uses a `src/` layout (`src/flash_excel`). Every development command
is a [Poe the Poet](https://poethepoet.natn.io/) task defined in
`pyproject.toml`; `uv run poe` lists them all.

The front-end linter needs Node and `pnpm install` once per clone:

```bash
uv run poe lint-js       # ESLint on the web UI
uv run poe lint-js-fix   # same, with auto-fix
```

## 🧪 Testing

```bash
uv run poe test        # full test suite, no coverage floor
uv run poe test-unit   # unit tests only
uv run poe test-fast   # parallel, skips tests marked slow
uv run poe test-ci     # tests + the 70% coverage gate
```

Before opening a pull request, run the full local gate — the same sequence CI
runs:

```bash
uv run poe check   # format-check → lint → typecheck → security → imports → test-ci
```

## 📚 Documentation

The user documentation is a MkDocs Material site in `docs/`, configured by
`mkdocs.yml` and published to <https://neuraaak.github.io/Flash-Excel/>.

```bash
uv run poe docs         # serve the site locally with live reload
uv run poe docs-build   # strict build: any broken link or nav entry fails
```

A pull request that touches the docs runs `docs-build` in CI. The site itself
is deployed by the `04-docs` workflow after a push to `main`; see
[.github/workflows/README.md](.github/workflows/README.md).

## 📝 Commits and pull requests

- Write everything in English: code, comments, docstrings, commit messages and
  documentation.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/):
  `type(scope): imperative description`, with a body explaining the *why*.
- Fork → branch → commit → open a pull request against `main`.

## 🚢 Build & Release

Building and releasing is **maintainer-only and local — not CI**. A fresh clone
builds and tests the app fine, but it cannot publish: the TUF signing keys and
the Cloudflare R2 credentials are deliberately kept out of the repository.

`build.py` builds, and only builds — nothing it does leaves the machine:

```bash
uv run build.py                   # version → compile → zip → installer → signed TUF release
uv run build.py --skip-release    # rebuild an already published version
uv run build.py --skip-installer  # no Inno Setup stage
uv run build.py --skip-build      # reuse dist/ as-is, to iterate on the installer
```

Publishing is a separate, explicit step, run once the build has been checked.
Two helpers wrap it, so the project root and the credentials in the gitignored
`.env` do not have to be handled by hand — copy [example.env](example.env) to
`.env` and fill it in:

```bat
.scripts\build\publish-update.cmd     :: public TUF tree -> R2
.scripts\build\publish-release.cmd    :: installer + zip -> GitHub Release
```

Both forward any extra flag to the command they wrap (`--yes`, `--draft`,
`--notes-file`, …) and both ask for confirmation first, the publication being
irreversible on the remote side. `publish-update` transfers only the
**public** part of the signed TUF tree (`metadata/`, `targets/`,
`withdrawn.json`); the private keystore in `.tufup/keys` never leaves.

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
