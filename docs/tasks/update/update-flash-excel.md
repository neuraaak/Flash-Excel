# Update Flash-Excel

Install a new version of Flash-Excel from inside the application, without downloading an installer again.

## 🔧 Prerequisites

- Flash-Excel installed with the installer. See [Get started](../../get-started.md).
- An internet connection when Flash-Excel starts.
- No run in progress: Flash-Excel closes during the update.

## 📝 Steps

1. Start Flash-Excel. It checks for a new version when it opens.
2. When a new version exists, a link **Update to v<version>** appears at the bottom right of the window, next to the current version number. Select it.
3. The link reads **Updating…** while the new version downloads. Flash-Excel then closes to install it.
4. Start Flash-Excel again if it does not reopen by itself.

## ✅ Result

The version number at the bottom right of the window shows the new version.

Your presets, settings and output files are kept: they are stored outside the installation folder. See [Data locations](../../reference/data-locations.md).

!!! note "No update link"
    Without a link, you already have the latest version, or the check could not reach the update server. You can also install a new version by running its installer from the [Releases page](https://github.com/neuraaak/Flash-Excel/releases/latest).

## ➡️ Next steps

- [Automatic updates](../../concepts/automatic-updates.md) — how updates are checked and verified.
- [Release notes](../../release-notes.md) — what changed in each version.
