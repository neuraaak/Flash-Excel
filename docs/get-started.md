# Get started with Flash-Excel

At the end of this page, you have installed Flash-Excel, built a preset with one step, checked it on a preview and written your first transformed file.

## 🔧 Prerequisites

- A Windows PC. No administrator rights are needed: Flash-Excel installs for your Windows user only.
- An Excel or CSV file to transform (`.xlsx`, `.xls`, `.xlsm` or `.csv`).

## 📝 Steps

### Install Flash-Excel

1. Open the [latest release](https://github.com/neuraaak/Flash-Excel/releases/latest) and download `Flash-Excel-<version>-setup.exe`.
2. Run the installer and choose the wizard language. Flash-Excel starts in the language you pick here; you can change it later in **Settings**.
3. Follow the wizard. Keep the launch option checked on the last page to start Flash-Excel right away.

The window opens on **Processing**. The sidebar on the left gives access to **Processing**, **Presets** and **Settings**.

### Build a preset with one step

A preset is the list of transformations to apply. This example renames one column.

1. In the sidebar, select **Presets**.
2. Next to **Presets**, select the **+** button (**New preset**). A new preset named `Preset 1` (or the next free number) opens in the editor.
3. In the name field at the top, type a name for the preset, for example `My first preset`.
4. Under **Load the Excel template**, select **Load a file** and pick your source file. Flash-Excel reads its columns so the steps can offer them in their lists.
5. Under **Action configuration**, select **Rename columns** in the list of actions.
6. Select **Add a rule**. In **Source column**, pick the column to rename; in **New name**, type its new name.
7. Select **Save**. The message **Preset saved** confirms it, and the preset appears in the list on the left.

### Preview and run the preset

1. In the sidebar, select **Processing**.
2. Click the drop zone **Drop your Excel/CSV files here — or click to browse** and pick your source file. You can also drag the file onto the window.
3. Under **Preset**, open the list and select your preset.
4. Select **Preview**. The **Transformation preview** window shows the first 100 rows of the file after the transformation, without writing anything. Close it with **×**.
5. Under **Output**, look at **Destination folder**: by default it is `Documents\flash-excel\output`. Leave it as is for this first run. If your source file is an `.xls` or `.xlsm` file, set **Format** to **.xlsx (Excel)**: **Same as source** only writes `.xlsx` and `.csv` files.
6. Select **Run preset**.

## ✅ Result

The file row shows the status **Done**, and the **Console** ends with a line such as `Done in 0.42s → C:\Users\<you>\Documents\flash-excel\output\<file>_clean.xlsx`. Open that folder: your transformed file is there, named after the source file with `_clean` added, and the source file is unchanged.

If the run ends with **Error** instead, the **Console** shows the reason. See [Troubleshooting](troubleshooting.md).

## ➡️ Next steps

- [Add steps to a preset](tasks/presets/add-steps-to-a-preset.md) — filter, clean, sort and more.
- [Run a preset](tasks/run/run-a-preset.md) on several files, with your own output folder, format and naming pattern.
- [Schedule a preset](tasks/automate/schedule-a-preset.md) to run every day without opening Flash-Excel.
- [Presets](concepts/presets.md) — what a preset holds and where it is stored.
