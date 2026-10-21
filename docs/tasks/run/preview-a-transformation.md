# Preview a transformation

Check what a preset does to your data before writing any file. The preview applies the preset to the first 100 rows of a source file and shows the result in a table.

## 🔧 Prerequisites

- At least one source file loaded on the **Processing** page. See [Load source files](../files/load-source-files.md).
- A saved preset. Changes made on the **Presets** page are previewed only once you select **Save** there.

## 📝 Steps

1. In the sidebar, select **Processing**.
2. Under **Preset**, select the preset to check.
3. Select **Preview**.

## ✅ Result

The **Transformation preview** window opens. It shows the columns and rows after the transformation, and the number of rows left, for example **87 rows after transformation**. Empty cells read `null`. No output file is written.

Close the window with **×**, ++esc++, or by clicking outside it.

!!! note "What the preview covers"
    - Only the first file of the list is previewed, even when several files are loaded.
    - Only the first 100 rows of that file are read. **Filter rows**, **Deduplicate rows** and **Sort rows** therefore act on this sample only: a row beyond the first 100 can still match your filters in a real run.
    - If no row of the sample is left, the window says **No rows remain in this sample after transformation.**

If the preview fails, the window shows **Preview failed:** followed by the reason. See [Troubleshooting](../../troubleshooting.md).

## ➡️ Next steps

- [Run a preset](run-a-preset.md)
- [Add steps to a preset](../presets/add-and-reorder-steps.md) to adjust the preset.
