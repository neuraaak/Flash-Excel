# Create a preset

Create a preset when you have a new kind of file to transform. A preset holds the steps to apply and remembers the columns of a template file, so you can edit it later without that file.

## 🔧 Prerequisites

- A template file: an Excel or CSV file with the same columns as the files you will process (`.xlsx`, `.xls`, `.xlsm` or `.csv`).

## 📝 Steps

1. In the sidebar, select **Presets**.
2. Next to **Presets**, select the **+** button (**New preset**). A new preset named `Preset 1` (or the next free number) opens in the editor.
3. In the name field of the toolbar, replace the default name with a name of your own.
4. Under **Load the Excel template**, select **Load a file** and pick your template file.
5. Under **Action configuration**, add at least one step. See [Add steps to a preset](add-and-reorder-steps.md).
6. Select **Save**.

## ✅ Result

The message **Preset saved** appears, and the preset is listed on the left with the label **Local** and its number of steps. It is also offered in the **Preset** list of the **Processing** page.

The preset is saved as a `.toml` file in `Documents\flash-excel\presets`. The file name comes from the preset name: `Monthly report` becomes `monthly_report.toml`.

!!! warning "A new preset is not saved until you select Save"
    Until then, it exists only in the editor and is not listed.

!!! note "Renaming a preset"
    To rename a preset, select it, change its name and select **Save**: its file is renamed too. If another preset already uses the same file name, Flash-Excel refuses the save and asks you to choose another name.

## ➡️ Next steps

- [Add steps to a preset](add-and-reorder-steps.md)
- [Preview a transformation](../run/preview-a-transformation.md)
- [Presets](../../concepts/presets.md) — what a preset contains.
- [Preset file](../../reference/preset-file.md) — the format of the `.toml` file.
