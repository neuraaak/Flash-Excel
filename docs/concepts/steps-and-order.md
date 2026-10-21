# Steps and their order

A preset is a chain of **steps**. Each step does one kind of transformation — rename columns, filter rows, sort rows — and hands its result to the next one. The output file is what comes out of the last step.

## Steps run one after the other

Steps never see the source file directly: each one works on the result of the steps before it. This has three practical effects:

- **Removed columns are gone for later steps.** After **Select columns** or **Drop columns**, a later step cannot use a column that was left out.
- **Renamed columns change name for later steps.** After **Rename columns**, later steps refer to the new name.
- **Added columns exist only for later steps.** A column created by **Add computed column** can be filtered, sorted or reordered, because those steps come after it.

The editor follows this chain for you. The column lists offered by each step show the columns as they are *at that point*, not as they are in the source file. When you rename a column, the steps after it are updated to use the new name. When a newly loaded template file no longer contains some columns, the **Column layout changed** dialog offers **Load & clean up references** to remove them from your steps.

If a step still refers to a column that no longer exists when the preset runs, that step fails and the file is handled according to the **On error** choice. See [Error handling](error-handling.md).

## The order used by the editor

On the **Presets** page, the **Action configuration** list shows the 12 kinds of step in a fixed order. You configure each kind at most once, and the preset runs the configured ones in this order:

| Order | Step (as shown in the app) | Typical use                                              |
| :---: | :------------------------- | :------------------------------------------------------- |
| 1     | **Rename columns**         | Give the source columns the names you want to work with. |
| 2     | **Select columns**         | Keep only the columns you need.                          |
| 3     | **Drop columns**           | Remove a few columns.                                    |
| 4     | **Cast types**             | Turn text into numbers, dates or booleans.               |
| 5     | **Replace values**         | Swap exact values, such as codes for labels.             |
| 6     | **Clean text**             | Trim spaces, remove accents, change case.                |
| 7     | **Fill empty cells**       | Replace empty cells with a value or a neighbour.         |
| 8     | **Add computed column**    | Build a new column from a formula.                       |
| 9     | **Filter rows**            | Keep only the rows that match conditions.                |
| 10    | **Deduplicate rows**       | Remove duplicate rows.                                   |
| 11    | **Sort rows**              | Order the rows.                                          |
| 12    | **Reorder columns**        | Set the final column order.                              |

A step you leave empty is not saved and does not run; if it was only partly filled in, **Save** tells you it was refused (**Preset saved, but these steps were refused and are not in the file**). The steps cannot be dragged into another order in the editor: the order above is designed so that each step finds the columns and types it needs.

Three kinds of step hold several rules: **Replace values** (one rule per column), **Clean text** (one clean action per group of columns) and **Add computed column** (one rule per new column). Each rule is saved as its own step, and the rules run from top to bottom.

For what each step does and accepts, see [Steps reference](../reference/steps.md).

## Presets written by hand

In a preset file you write yourself, steps run in the order they appear in the file, and the same kind of step may appear several times. That gives you full control, for example to filter rows before cleaning text.

!!! warning "Opening a hand-written preset in the editor"
    The editor shows one step of each kind. When a file repeats a kind that holds a single rule set (for example two **Filter rows** steps), the editor shows only the last one, and selecting **Save** writes the steps back in the editor's order above. Keep hand-written presets that rely on their own order out of the editor, or check them after saving.

## ➡️ Next steps

- [Add and reorder steps](../tasks/presets/add-and-reorder-steps.md)
- [Preview a transformation](../tasks/run/preview-a-transformation.md)
- [Preset file format](../reference/preset-file.md)
