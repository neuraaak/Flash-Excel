# Load source files

Load the Excel or CSV files you want to transform on the **Processing** page. You can load one file or a whole batch that a preset processes one after the other.

## 🔧 Prerequisites

- Files in a supported format: `.xlsx`, `.xls`, `.xlsm` or `.csv`. See [File formats](../../reference/file-formats.md).
- For a batch, files with the same column layout: the step lists are built from the first file only.

## 📝 Steps

=== "Pick the files"

    1. In the sidebar, select **Processing**.
    2. Click the drop zone **Drop your Excel/CSV files here — or click to browse**.
    3. In the file dialog, select one file, or several with ++ctrl++ or ++shift++, then confirm.

=== "Drag and drop"

    1. In the sidebar, select **Processing**.
    2. Drag one or several files from the Windows Explorer and drop them onto the window.

    Files Flash-Excel cannot read are left out of the list.

To replace the list, select **Load file** above the list and pick other files: the new selection replaces the previous one. To empty the list, select **Clear**. Both are unavailable while a run is in progress.

## ✅ Result

Under **Input file**, each file appears as a row with its name, size and the status **Pending**. The header shows the number of files, for example **3 file(s)**, and the first row also shows its number of columns.

!!! note "How Flash-Excel reads the files"
    Only the first sheet of an Excel workbook is read. For a CSV file, the column separator is detected automatically, unless the preset file sets one (see [Preset file](../../reference/preset-file.md)).

## ➡️ Next steps

- [Preview a transformation](../run/preview-a-transformation.md)
- [Run a preset](../run/run-a-preset.md)
- If a file is refused, see [Unsupported file format](../../troubleshooting.md#unsupported-file-format); if a CSV loads as one column, see [A CSV source loads as a single column](../../troubleshooting.md#csv-source-single-column).
