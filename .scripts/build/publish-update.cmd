@echo off
REM ///////////////////////////////////////////////////////////////
REM  PUBLISH-UPDATE - Publish the signed TUF tree to the update backend
REM ///////////////////////////////////////////////////////////////
REM
REM  Thin wrapper over `ezcompiler publish update`, which replaced the
REM  deprecated Python publication API. It only adds what the CLI cannot do
REM  by itself: run from the project root, and load the R2 credentials from
REM  the gitignored .env (ezcompiler reads os.environ, never a .env file).
REM
REM  Only the public part of the tree is transferred (metadata/, targets/,
REM  withdrawn.json); the private keystore in .tufup\keys never leaves.
REM
REM  Prerequisites:
REM    - `uv run build.py` ran, so a signed release exists locally
REM    - .env holds R2_ACCOUNT_ID (or R2_ENDPOINT), R2_ACCESS_KEY_ID,
REM      R2_SECRET_ACCESS_KEY
REM
REM  Usage:
REM    .scripts\build\publish-update.cmd            # asks for confirmation
REM    .scripts\build\publish-update.cmd --yes      # unattended
REM    .scripts\build\publish-update.cmd -rd disk   # any `publish update` flag
REM
REM  TUF metadata versions are monotonic and clients auto-update with no
REM  human action: a published tree is not unpublished, only republished
REM  higher. Hence the confirmation, unless --yes is passed.

setlocal
set "ROOT=%~dp0..\.."
pushd "%ROOT%" || exit /b 1

REM Credentials into the environment, values never echoed.
if exist ".env" (
    for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do (
        if not "%%~B"=="" set "%%~A=%%~B"
    )
)

uv run ezcompiler publish update %*
set RC=%ERRORLEVEL%

popd
exit /b %RC%
