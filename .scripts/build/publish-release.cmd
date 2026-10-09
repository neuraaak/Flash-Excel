@echo off
REM ///////////////////////////////////////////////////////////////
REM  PUBLISH-RELEASE - Publish the installer and the zip as a GitHub Release
REM ///////////////////////////////////////////////////////////////
REM
REM  Thin wrapper over `ezcompiler publish release`, which replaced the
REM  deprecated Python publication API. It only adds what the CLI cannot do
REM  by itself: run from the project root, force the github backend, and
REM  load the credentials from the gitignored .env (ezcompiler reads
REM  os.environ, never a .env file).
REM
REM  The github backend is forced because [tool.ezcompiler.upload] sets
REM  release_destination = "disk": the build keeps the installer local, and
REM  publishing it is this explicit, separate step. Pass another -rld after
REM  the script name to override it.
REM
REM  Prerequisites:
REM    - `uv run build.py` ran, so dist\installer\ holds the installer
REM    - `gh` installed and authenticated (`gh auth login`)
REM
REM  Usage:
REM    .scripts\build\publish-release.cmd                     # recap, then confirm
REM    .scripts\build\publish-release.cmd --yes                # unattended
REM    .scripts\build\publish-release.cmd --notes-file NOTES.md
REM    .scripts\build\publish-release.cmd --draft              # unpublished
REM
REM  The CLI runs its own preflight before touching GitHub: it checks the
REM  authentication, refuses an existing tag, and refuses a missing
REM  installer. The tag, the title and the pre-release label all default
REM  from the project version.

setlocal
set "ROOT=%~dp0..\.."
pushd "%ROOT%" || exit /b 1

REM Credentials into the environment, values never echoed.
if exist ".env" (
    for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do (
        if not "%%~B"=="" set "%%~A=%%~B"
    )
)

REM -rld first, so a -rld passed by the caller wins.
uv run ezcompiler publish release --release-destination github %*
set RC=%ERRORLEVEL%

popd
exit /b %RC%
