# Presets

A **preset** is a saved list of transformations. You build it once on the **Presets** page, then apply it to as many files as you like from the **Processing** page, from a launcher, from a scheduled task or from the command line. The source file is never modified: every run writes a new output file.

## What a preset contains

A preset is a small text file in the TOML format, with the `.toml` extension. It holds two parts:

- **Metadata** — the preset name, an optional description, and options for reading CSV files (separator, encoding, decimal mark).
- **Steps** — the ordered list of transformations: rename columns, filter rows, add a computed column, and so on. Flash-Excel offers 12 kinds of step. See [Steps and their order](steps-and-order.md).

The preset also remembers the columns and their types of the file you loaded under **Load the Excel template**. This is why you can reopen a preset and edit its steps without loading the file again: the editor shows **Template model · file may no longer exist on this machine** and keeps offering the remembered columns.

The full file format is described in [Preset file format](../reference/preset-file.md).

## Where presets are stored

The presets you create are saved in your **Documents** folder, under `Documents\flash-excel\presets`. The file name comes from the preset name: lower case, punctuation removed, spaces replaced by underscores. `Monthly HR report` is saved as `monthly_hr_report.toml`.

Because they live in **Documents**, presets survive updates and uninstallation, and you can back them up, copy them or send them like any other document. See [Data locations](../reference/data-locations.md).

## Local and shared presets

Flash-Excel lists presets from two kinds of places:

| Kind       | Where it comes from                                                                 | What you can do                                     |
| :--------- | :---------------------------------------------------------------------------------- | :-------------------------------------------------- |
| **Local**  | `Documents\flash-excel\presets`                                                     | Edit, save, delete, export, run.                    |
| **Shared** | A folder you add under **Settings** › **Read-only preset sources**, with a label    | Run and preview. **Save** and **Delete** are disabled. |

Shared folders let a team use the same presets, for example from a network drive. Flash-Excel never writes to them: *Shared folders are read-only in Flash-Excel.* To change a shared preset, edit the file in the shared folder itself, or ask whoever maintains it. If a shared folder cannot be reached, its presets are simply not listed. See [Use shared preset folders](../tasks/presets/use-shared-preset-folders.md).

## Saved presets are what runs

**Run preset** and **Preview** read the preset file as it is saved on disk. Changes made in the editor apply only after you select **Save** on the **Presets** page.

A preset file that Flash-Excel cannot read still appears in the list, marked **unreadable**, so that a damaged file does not look like a deleted one. Hover over the marker to see the reason. See [Troubleshooting](../troubleshooting.md#a-preset-is-marked-unreadable).

!!! warning "Editing a preset file by hand"
    You can write or edit a preset file in a text editor. Keep in mind that saving that preset again from the **Presets** page rewrites its metadata: the description and the CSV reading options (`csv_separator`, `csv_encoding`, `csv_decimal_comma`) go back to their defaults. The editor also keeps only one step of each kind, in its own fixed order. See [Steps and their order](steps-and-order.md#presets-written-by-hand).

## ➡️ Next steps

- [Create a preset](../tasks/presets/create-a-preset.md)
- [Export a preset](../tasks/presets/export-a-preset.md)
- [Use shared preset folders](../tasks/presets/use-shared-preset-folders.md)
