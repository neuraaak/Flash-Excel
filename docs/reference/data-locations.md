# Data locations

Flash-Excel keeps your data outside its installation folder, so that updates — which replace that folder — never touch it.

## Overview

| What                          | Location                                       | Contents                                                     |
| :---------------------------- | :--------------------------------------------- | :----------------------------------------------------------- |
| Presets                       | `Documents\flash-excel\presets`                | Your local presets, one `.toml` file each.                   |
| Output files (default)        | `Documents\flash-excel\output`                 | Files written by runs when no other folder is chosen.        |
| Settings                      | `%APPDATA%\flash-excel`                        | `app.config.yaml`, `theme.config.yaml` and window data.      |
| Logs                          | `%LOCALAPPDATA%\flash-excel\logs`              | `flash-excel.log` and its archives.                          |
| Shared presets                | The folders listed under **Read-only preset sources** | Presets maintained by someone else. Flash-Excel only reads them. |
| Program                       | The installation folder                        | The application itself. Replaced by every update.            |

To open one of these folders, paste its location — for example `%APPDATA%\flash-excel` — into the address bar of File Explorer.

## Presets and output files

`Documents` is your real Documents folder, including when it is redirected to OneDrive (`%USERPROFILE%\OneDrive\Documents`). Presets and outputs are ordinary documents: open them, back them up, copy them to another PC.

The output folder is only the default. Each run can write elsewhere: **Destination folder** on the **Processing** page, or `--output` on the command line. A relative folder is created inside `Documents\flash-excel\output`.

## Settings

`%APPDATA%` is your roaming application data folder, usually `C:\Users\<you>\AppData\Roaming`. It contains:

| File or folder           | Contents                                                                                                |
| :----------------------- | :------------------------------------------------------------------------------------------------------ |
| `app.config.yaml`        | Palette, mode, language, CSV output and shared preset folders. See [Settings](settings.md).             |
| `theme.config.yaml`      | The colour palettes. `theme.config.yaml.bak` is the previous copy, kept when an update changes them.    |
| `.theme.source`          | Marker used to detect a newer palette file. Do not edit.                                                 |
| `webview\`               | Data of the application window.                                                                         |
| `installer.ini`          | Written by the installer with the language chosen in the wizard, read once at the next start, then deleted. |

If you delete `app.config.yaml`, Flash-Excel creates it again with the default settings at the next start.

## Logs

`%LOCALAPPDATA%` is your local application data folder, usually `C:\Users\<you>\AppData\Local`. The log file `%LOCALAPPDATA%\flash-excel\logs\flash-excel.log` records starts, runs, errors and update checks.

- A new log file is started every day; the previous one is renamed with its date and time.
- Log files older than 14 days are deleted.
- To record more detail, start Flash-Excel with `--debug`, or add `--debug` to a command-line run.

The log is the first place to look when something fails. See [Troubleshooting](../troubleshooting.md).

## Program

Flash-Excel installs for your Windows user only, by default under `%LOCALAPPDATA%\Programs`, without administrator rights. Do not store anything in the installation folder: every update replaces it.

## Uninstalling

Uninstall Flash-Excel from **Settings** › **Apps** in Windows (or **Programs and Features**). Uninstalling removes the installation folder only.

| Kept after uninstalling                         | Removed           |
| :---------------------------------------------- | :---------------- |
| Presets (`Documents\flash-excel\presets`)       | The program files |
| Output files (`Documents\flash-excel\output` and any other folder you used) | |
| Settings (`%APPDATA%\flash-excel`)              |                   |
| Logs (`%LOCALAPPDATA%\flash-excel\logs`)        |                   |
| Scheduled tasks and `.cmd` launchers you created |                  |

Reinstalling later picks up your presets and settings again. To remove everything, delete these folders by hand after uninstalling, and remove your scheduled tasks from the **Flash-Excel** folder of Task Scheduler (see [Schedule a preset](../tasks/automate/schedule-a-preset.md)).

## Presets from versions before 1.3.0

Versions before 1.3.0 stored presets inside the installation folder. On its first start, a newer version copies any preset still found there to `Documents\flash-excel\presets`, without overwriting a preset of the same name. Settings from those versions are not carried over.
