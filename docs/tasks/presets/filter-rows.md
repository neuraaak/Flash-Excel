# Filter rows

Keep only the rows that match your conditions, for example the active customers or the orders above an amount. The other rows are left out of the output file.

## 🔧 Prerequisites

- A preset open on the **Presets** page, with a template file loaded. See [Create a preset](create-a-preset.md).

## 📝 Steps

1. Under **Action configuration**, select **Filter rows**.
2. Next to **Keep rows matching**, choose how the conditions combine:
    - **All conditions**: a row is kept when it matches every condition;
    - **Any condition**: a row is kept when it matches at least one condition.
3. Select **Add a rule**. A condition row appears.
4. In the condition row:
    1. pick the column;
    2. pick the operator: `=`, `≠`, `>`, `≥`, `<`, `≤`, **contains**, **starts with** or **ends with**;
    3. type the value to compare with in **Value**.
5. Repeat steps 3 and 4 for each condition. Select **×** at the end of a row to remove it.
6. Select **Save**.

## ✅ Result

The **Filter rows** action shows the number of conditions in the list of actions. When the preset runs, only the matching rows are written.

!!! note "How values are compared"
    - On a numeric column, type a number: a text value on a numeric column makes the run fail with an error.
    - **contains**, **starts with** and **ends with** compare the text exactly as typed, including upper and lower case.
    - A condition with an empty value is ignored. With no condition at all, every row is kept.

!!! tip "Check the filter on a preview"
    The preview reads only the first 100 rows of the file. If no row of that sample matches, the preview says so even though later rows may match. See [Preview a transformation](../run/preview-a-transformation.md).

## ➡️ Next steps

- [Steps](../../reference/steps.md) — the **Filter rows** options in detail.
- [Troubleshooting](../../troubleshooting.md) if a run fails on a filter.
