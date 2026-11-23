# Automatic updates

Flash-Excel keeps itself up to date from inside the application. You do not need to download a new installer for each version.

## How a new version is found

Each time Flash-Excel starts, it asks the update server whether a newer version exists. The check runs in the background and does not slow down your work.

When a newer version is available, the bottom-right corner of the window shows **Update to v*X.Y.Z*** next to the current version number. Nothing is installed until you select it. When no update is available, or when the check cannot reach the server (for example without an internet connection), only the version number is shown.

## How an update is installed

When you select **Update to v*X.Y.Z***, the link changes to **Updating…** while Flash-Excel:

1. downloads the new version — often as a small patch rather than the whole application;
2. checks that the download is genuine;
3. closes the window, so that its files can be replaced, and installs the new version in its installation folder.

Start Flash-Excel again if it does not reopen by itself. No administrator rights are needed, because Flash-Excel is installed for your Windows user only.

## Signed updates

Every release is signed by the publisher, and the update metadata is signed too (Flash-Excel uses [The Update Framework](https://theupdateframework.io/), a standard for secure software updates). Before installing anything, Flash-Excel checks those signatures against the trusted keys shipped with the application. A download that was altered, or that does not come from the publisher, is refused and nothing is installed.

## What an update keeps

An update replaces only the installation folder. Your settings, presets, output files and logs are stored elsewhere and are left untouched. See [Data locations](../reference/data-locations.md).

## When automatic updates do not apply

Updates only work in the installed application. If an update fails, the reason is written to the application log, and you can always install the latest version by hand from the [GitHub releases page](https://github.com/neuraaak/Flash-Excel/releases). See [Troubleshooting](../troubleshooting.md#the-update-link-never-appears-or-the-update-fails).

## ➡️ Next steps

- [Update Flash-Excel](../tasks/update/update-flash-excel.md)
- [Release notes](../release-notes.md)
