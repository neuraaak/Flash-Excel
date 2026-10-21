# Add steps to a preset

Add the transformations a preset applies: renaming, selecting or dropping columns, converting types, cleaning text, filtering, sorting and more. Each kind of step is configured once per preset, and Flash-Excel runs them in a fixed order.

## 🔧 Prerequisites

- A preset open on the **Presets** page. See [Create a preset](create-a-preset.md).
- A template file loaded under **Load the Excel template**, so that the steps can list the columns. Without it, the hint **Load a file to enable column mapping** is shown.

## 📝 Steps

1. In the sidebar, select **Presets**, then select the preset in the list on the left.
2. Under **Action configuration**, select an action in the list, for example **Filter rows**. Hover the **i** icon next to an action to read what it does.
3. Configure the action in the panel on the right. Most actions start with **Add a rule**; the panel header shows how many rules are **configured**.
4. Repeat for every action you need. An action with at least one rule shows its count in the list.
5. Select **Save**.

The twelve actions, in the order Flash-Excel runs them:

| Order | Action                  | What it does                                  |
| :---: | :---------------------- | :-------------------------------------------- |
| 1     | **Rename columns**      | Give one or more columns a new name.          |
| 2     | **Select columns**      | Keep only the columns you choose.             |
| 3     | **Drop columns**        | Remove the columns you choose.                |
| 4     | **Cast types**          | Convert columns to a target data type.        |
| 5     | **Replace values**      | Find and replace values inside columns.       |
| 6     | **Clean text**          | Trim, normalise and strip whitespace.         |
| 7     | **Fill empty cells**    | Replace null values using a strategy.         |
| 8     | **Add computed column** | Create a new column from an expression.       |
| 9     | **Filter rows**         | Keep only rows matching your conditions.      |
| 10    | **Deduplicate rows**    | Remove duplicate rows by key columns.         |
| 11    | **Sort rows**           | Order rows by one or more columns.            |
| 12    | **Reorder columns**     | Change the column order.                      |

Each step receives the result of the steps above it. The column lists of a step therefore show the columns as they are at that point: a column renamed in **Rename columns** appears under its new name in **Filter rows**, and a column added by **Add computed column** is available to **Sort rows**. When you rename a column, the later steps that use it are updated for you.

## ✅ Result

The message **Preset saved** appears and the step count of the preset is updated in the list. If a step is incomplete, the message **Preset saved, but these steps were refused and are not in the file: …** names it: complete it and save again.

!!! note "Changing the order of the steps"
    The **Presets** page always saves the steps in the order of the table above, and you cannot move a step in the editor. To run steps in another order, edit the preset file by hand: Flash-Excel runs the steps in the order they appear in the file. Saving that preset again from the **Presets** page puts the steps back in the standard order. See [Steps and order](../../concepts/steps-and-order.md) and [Preset file](../../reference/preset-file.md).

!!! tip "Column order in the output"
    To change the order of the columns in the output file, use the **Reorder columns** action.

!!! note "Loading a template with different columns"
    If you load a template file whose columns differ from those saved in the preset, the **Column layout changed** dialog lists the **Columns no longer in file** and the **New columns in file**. Select **Load & clean up references** to remove the missing columns from the steps, **Ignore differences** to keep the steps as they are, or **Cancel**.

## ➡️ Next steps

- [Add a computed column](add-a-computed-column.md)
- [Filter rows](filter-rows.md)
- [Preview a transformation](../run/preview-a-transformation.md)
- [Steps](../../reference/steps.md) — every option of every action.
