# Run a preset

Apply a preset to one or several source files and write the transformed files. You choose the output format, the destination folder, the file names, and what happens when a file fails.

## 🔧 Prerequisites

- At least one source file loaded on the **Processing** page. See [Load source files](../files/load-source-files.md).
- A saved preset.

## 📝 Steps

1. In the sidebar, select **Processing**.
2. Under **Preset**, select the preset. Each entry shows the preset name, its source (**Local** or the label of a shared folder) and its number of actions. The box below lists the actions of the selected preset.
3. Under **Output**, set the output:

    | Field                  | What to enter                                                                                                         | Default                         |
    | :--------------------- | :-------------------------------------------------------------------------------------------------------------------- | :------------------------------ |
    | **Format**             | **Same as source**, **.xlsx (Excel)**, **.csv (UTF-8)** or **.parquet**.                                              | **Same as source**              |
    | **Destination folder** | The folder where the files are written. Type a path, or select the folder icon to pick one.                           | `Documents\flash-excel\output`  |
    | **Naming pattern**     | The output file name, without extension. `{name}` stands for the name of the source file.                             | `{name}_clean`                  |

4. Under **On error**, choose what happens when a file fails:
    - **Skip file** (continue queue): the failing file is not written and the run goes on with the next file;
    - **Stop all** (halt on first error): the run stops at the first failing file;
    - **Ignore** (write partial): the failing step is skipped, the other steps still apply and the file is written.
5. Select **Run preset**.

## ✅ Result

The files are processed one after the other. Each row shows its progress and its status: **Pending**, **Running**, **Done**, **Error** or **Skipped**. At the bottom of the panel, **Progress** covers the whole batch, with the counters **Rows out**, **Errors**, **Warnings** and **Elapsed**.

The **Console** logs each step with its row counts, then a line such as `Done in 0.42s → <output path>` for each written file. Use the **All**, **Info**, **Step**, **Warn** and **Err** filters to narrow the log.

With the default settings, `C:\Data\sales.xlsx` gives `Documents\flash-excel\output\sales_clean.xlsx`.

!!! warning "Existing files are replaced"
    A file with the same name in the destination folder is overwritten. Change the **Naming pattern** or the **Destination folder** to keep earlier results.

!!! note "Same as source with .xls and .xlsm files"
    **Same as source** writes only `.xlsx` and `.csv` files. For an `.xls` or `.xlsm` source, choose **.xlsx (Excel)** as the **Format**, or the file fails with [Unsupported format: 'xls'](../../troubleshooting.md#unsupported-format-xls).

!!! tip "Relative folder"
    A relative **Destination folder**, such as `monthly`, is created inside `Documents\flash-excel\output`.

If a file ends with **Error**, read its message in the **Console** and look it up in [Troubleshooting](../../troubleshooting.md): a missing column is covered in [A step cannot find a column](../../troubleshooting.md#column-not-found), a locked file in [Permission denied](../../troubleshooting.md#file-in-use).

## ➡️ Next steps

- [Stop a run](stop-a-run.md)
- [Schedule a preset](../automate/schedule-a-preset.md) to repeat this run every day.
- [Error handling](../../concepts/error-handling.md) — the three error modes in detail.
- [Set the CSV output format](../settings/set-the-csv-output-format.md)
