# Add a computed column

Add a column whose values are calculated from other columns, for example a full name built from a first name and a last name, or a price rounded to two decimals.

## 🔧 Prerequisites

- A preset open on the **Presets** page, with a template file loaded. See [Create a preset](create-a-preset.md).

## 📝 Steps

1. Under **Action configuration**, select **Add computed column**.
2. In the panel, select **Add computed column**. The **New computed column** window opens.
3. In **New column name**, type the name of the column to create.
4. Build the formula in **Expression**:
    - select a column under **Columns** to insert it;
    - select a separator under **Separators** to insert it as text, for example `" "`;
    - under **Functions**, pick a category (**Text**, **Math**, **Date** or **Logic**), then select a function to insert it. Hover a function to see its description and an **Example**.
5. Check the expression, then select **Save**.
6. Repeat from step 2 for each column to add, then select **Save** in the toolbar to save the preset.

Examples of expressions:

| Expression                                 | Result                                             |
| :----------------------------------------- | :------------------------------------------------- |
| `CONCATENER(first_name, " ", last_name)`   | Joins the two columns with a space.                |
| `MAJUSCULE(last_name)`                     | The last name in upper case.                       |
| `ARRONDI(price, 2)`                        | The price rounded to two decimal places.           |
| `ANNEE(birth_date)`                        | The year of a date column.                         |
| `SI(age >= 18, "adult", "minor")`          | `adult` when the condition holds, `minor` otherwise. |

!!! tip "Column names with spaces or symbols"
    Write a column whose name contains spaces, starts with a digit or holds symbols between square brackets, for example `[Order date]`. Selecting the column under **Columns** inserts it in the right form.

!!! note "Function names are in French"
    The function names (`CONCATENER`, `MAJUSCULE`, `SI`…) follow French Excel and stay the same whatever the interface language. Text values go between double quotes.

## ✅ Result

The computed column is listed in the panel with its expression. Select the pencil icon to edit it, or the bin icon to delete it. In the following steps, such as **Filter rows** or **Sort rows**, the new column is available like any other.

## ➡️ Next steps

- [Computed-column functions](../../reference/computed-functions.md) — every function, its arguments and examples.
- [Preview a transformation](../run/preview-a-transformation.md) to check the values.
