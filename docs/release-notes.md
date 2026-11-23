# Release notes

What changed for you in each version of Flash-Excel, newest first. Installers for every version are on the [GitHub releases page](https://github.com/neuraaak/Flash-Excel/releases). To install the latest one, see [Update Flash-Excel](tasks/update/update-flash-excel.md).

## 1.5.0 — 2026-10-18

### New

- The footer shows a **Repository** link to the Flash-Excel project on GitHub.
- The run panel on the **Processing** page can be resized, and keeps its width the next time you open Flash-Excel.

### Improved

- New application icon and new icons for Excel and CSV files.

### Fixed

- Window preferences are now kept between sessions instead of being reset at every start.

## 1.4.0 — 2026-10-18

!!! warning "Presets saved before 1.4.0 and CSV files"
    CSV separators are now detected automatically, but presets saved by earlier versions contain `csv_separator = ";"`, which keeps forcing semicolons. If such a preset reads a comma-separated file as a single column, delete that line from the preset file. See [Troubleshooting](troubleshooting.md#csv-source-single-column).

### New

- Process several files in one run. Select or drop several files on the **Processing** page; each file has its own status in the queue, and **On error** › **Stop all** ends the whole run.
- Drop files onto the window, on the **Processing** and **Presets** pages.
- **Preview** shows the result of a preset on the first 100 rows without writing anything. See [Preview a transformation](tasks/run/preview-a-transformation.md).
- **Configure execution** creates a daily Windows scheduled task or a `.cmd` launcher for a preset and its files. See [Schedule a preset](tasks/automate/schedule-a-preset.md).
- Command-line mode: `Flash-Excel.exe --preset … --input …` runs a preset without opening the window. See [Command line](reference/command-line.md).
- **Read-only preset sources** in **Settings**: list presets from shared folders next to your own. See [Use shared preset folders](tasks/presets/use-shared-preset-folders.md).
- **CSV output** in **Settings**: choose the separator and decimal mark of output CSV files. **Auto** follows your Windows regional settings, so output files open in columns in Excel.
- New preset option `csv_decimal_comma` to read `1,5` as a number in CSV source files.

### Improved

- The separator of CSV source files is detected automatically instead of always being `;`.
- Column types of CSV files are guessed from every row, so a column that turns to text further down no longer makes the whole load fail.
- Loading a large Excel template no longer freezes the window.
- A damaged preset stays in the list, marked **unreadable**, instead of disappearing.
- **Save** tells you when steps were refused and left out of the file.
- Output files go to `Documents\flash-excel\output` by default, and the **Destination folder** field shows that full path.
- **Filter rows** with **contains** matches the text exactly as typed: `C++` no longer matches `C+ dev`.
- A non-numeric value in a filter on a numeric column gives a clear message.
- The palette cards in **Settings** preview the selected mode.

### Fixed

- Presets using **Value above** or **Value below** in **Fill empty cells** could not be read back after saving and vanished from the list.
- The template file name was lost each time a preset was saved.
- Renaming a preset could lose it if the save failed, and two names differing only by punctuation overwrote each other.
- Without a chosen destination, output files were written to the installation folder and lost at the next update.
- A run on a file locked by Excel with **On error** › **Ignore** never ended.
- `DROITE(column, 0)` returned the whole text instead of an empty text.

## 1.3.2

Maintenance version with no user-visible changes. It was not distributed through automatic updates.

## 1.3.1 — 2026-10-09

### New

- Editors for **Drop columns** and **Fill empty cells** on the **Presets** page.

### Improved

- The descriptions and examples of the computed column functions, and the messages of the **Presets** page, are translated into French.

## 1.3.0 — 2026-09-30

!!! warning "Settings reset when moving to 1.3.0"
    Settings moved to a new location and were not carried over: palette, mode and language return to their defaults once. Presets are carried over automatically.

### New

- An application log file records starts, runs and errors, in `%LOCALAPPDATA%\flash-excel\logs`. Start with `--debug` for more detail.
- Flash-Excel starts in the language chosen in the installer.

### Improved

- Your data now lives outside the installation folder, so updates and uninstalling no longer touch it: presets in `Documents\flash-excel\presets` (OneDrive redirection included), settings in `%APPDATA%\flash-excel`. Presets from earlier versions are copied there on the first start. See [Data locations](reference/data-locations.md).
- If the settings name a palette that does not exist, Flash-Excel uses the default palette instead of showing no colours.

### Fixed

- The automatic update to 1.2.3 could fail; it now installs correctly.

## 1.2.3 — 2026-07-16

### New

- Reorder columns by drag and drop in **Reorder columns**.
- The computed column editor has an edit button for each column and chips to insert separators (`_`, `-`, `/`, `.`, space).

### Improved

- Renaming a column, or a computed column, updates the steps that come after it.
- The **Console** and the preset summary show step names as in the editor, for example **Rename columns** instead of `rename_columns`.
- **Console** messages are translated.
- True/false values in Excel output follow the interface language: `True`/`False` in English, `VRAI`/`FAUX` in French.
- All the texts of the step editors are translated.

### Fixed

- The installed application could fail to read `.xlsx` files.

## 1.2.2 — 2026-07-13

### New

- Computed columns can use columns whose names contain spaces or symbols, written `[Column Name]`. The editor adds the brackets for you.
- The **Console** has a **Step** filter.

### Fixed

- Step messages in the **Console** were cut off.

## 1.2.1 — 2026-07-12

### Fixed

- The navigation menu and the footer were not translated.
- The preset list on the **Processing** page did not show presets created or deleted since the start.
- The **Settings** icon in the menu showed a sun instead of a gear.

## 1.2.0 — 2026-07-04

### New

- When a new version is available, an **Update to v*X.Y.Z*** link appears in the footer and installs it in one click. Updates are signed and verified before installation. See [Automatic updates](concepts/automatic-updates.md).
- The current version number is shown in the footer.

## 1.1.0 — 2026-06-02

### New

- Windows installer that installs Flash-Excel for the current user, without administrator rights.
- First version of automatic updates.
- Application icon.

## 1.0.0 — 2026-06-01

### New

- New interface with a **Processing** page to run presets and a **Presets** page to build them, with an editor for each kind of step.
- Colour palettes and interface settings.
