# CI/CD Pipeline

Numbered reusable workflows, one responsibility each, numbered by dependency
order. The number sorts them in the file tree and documents the cascade.

```text
00-install-deps  ← primes the uv cache (keyed on uv.lock)
01-ci            ← quality + type-check + security in parallel → test
                   (quality covers both toolchains: ruff and ESLint)
02-tag-sync      ← orchestrator: CI gate → tag_action (create|skip|preview)
                   └─→ 04-docs (via uses:)
04-docs          ← PR: mkdocs build --strict │ cascade: mike deploy to gh-pages
```

Number `03` is deliberately unused: it is the publish stage in sibling
projects. There is **no publish stage** here: Flash-Excel is a Windows desktop app, not a
published package. Distribution (PyInstaller build, TUF signing, upload to R2)
runs **locally** via `build.py` at the repo root — never in CI, because the
TUF signing keys are never uploaded as CI secrets. See
`[tool.ezcompiler]` in `pyproject.toml`.

## Tagging: `main` vs preview

`02-tag-sync` does **not** bump the version — a human writes it in
`pyproject.toml` (read by `poe -q read-version`, the single source). It then
resolves a three-state `tag_action`:

| Ref / state                        | `tag_action` | Effect                     |
| ---------------------------------- | ------------ | -------------------------- |
| push to `main`, version untagged   | `create`     | `vX.Y.Z` + `vX-latest`     |
| push to `main`, tag already exists | `skip`       | nothing (already released) |
| `workflow_dispatch` off `main`     | `preview`    | dry-run, nothing mutating  |

## Documentation (`04`)

`04-docs` runs in two modes:

- **Pull request** touching `docs/`, `mkdocs.yml`, `pyproject.toml` or
  `uv.lock` → `build` job: `poe docs-build` (`mkdocs build --strict`), read-only.
- **Cascade from `02-tag-sync`**, keyed on `tag_action`:

| `tag_action` | Effect                                                     |
| ------------ | ---------------------------------------------------------- |
| `create`     | `mike deploy <version>` + move the `latest` alias (pushes) |
| `skip`       | refresh the `dev` alias with the state of `main` (pushes)  |
| `preview`    | `mike deploy` without `--push`: validates the build only   |

mike writes the versioned site to the `gh-pages` branch. GitHub Pages must be
enabled **once, by hand**, in the repository settings (source: `gh-pages`
branch); until then the deploy succeeds but nothing is served. The site lives
at <https://neuraaak.github.io/Flash-Excel/>.

## Tag immutability

- **`vX.Y.Z`** — created once, **never force-pushed**. If a tag with this name
  exists and points elsewhere, the job **fails on purpose** rather than moving
  it — bump the version to release again.
- **`vX-latest`** — floating major alias, force-pushed on every release on
  `main`.

## Why a single orchestrator (`02`)

A tag pushed by `GITHUB_TOKEN` does **not** trigger another workflow (loop
protection). So `02-tag-sync` calls `01-ci` and `04-docs` directly via `uses:` rather than
relying on a `push: tags` event that would never fire.

## CI gates the release

`tag-sync` runs `needs: ci`, where `ci: uses: ./01-ci.yml`. A failing
quality, type-check, security or test job blocks tag creation — the release is never cut
on a broken build.

## Local equivalents

Every CI step is a Poe task, so the local gate and CI cannot drift:

```bash
uv run poe check        # format-check → lint → typecheck → security → imports → test-ci
uv run poe lint-js      # front-end lint, kept out of `check` (needs pnpm install)
uv run poe docs-build   # what 04-docs runs on a pull request
uv run poe docs         # serve the documentation site locally

# Local release (never in CI)
uv run build.py
```
