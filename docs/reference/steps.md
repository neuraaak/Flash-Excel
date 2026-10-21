# Steps

Flash-Excel offers 12 kinds of step. Each section below gives the step's name in the app, its **action name** in a preset file, its options, and how it behaves. For how steps chain together, see [Steps and their order](../concepts/steps-and-order.md). For the file syntax, see [Preset file format](../reference/preset-file.md).

Column names are case-sensitive everywhere. A step that names a column absent at that point of the chain fails, and the file is handled according to the **On error** choice (see [Error handling](../concepts/error-handling.md)).

## Summary

| Step (in the app)        | Action name           | Main options                          |
| :----------------------- | :-------------------- | :------------------------------------ |
| **Rename columns**       | `rename_columns`      | `mapping`                             |
| **Select columns**       | `select_columns`      | `columns`                             |
| **Drop columns**         | `drop_columns`        | `columns`                             |
| **Cast types**           | `cast_types`          | `casts`                               |
| **Replace values**       | `replace_values`      | `column`, `mapping`                   |
| **Clean text**           | `clean_text`          | `columns`, `ops`, `case`              |
| **Fill empty cells**     | `fill_nulls`          | `columns`, `strategy`, `value`        |
| **Add computed column**  | `add_computed_column` | `target`, `expression`                |
| **Filter rows**          | `filter_rows`         | `combine`, `conditions`               |
| **Deduplicate rows**     | `deduplicate_rows`    | `subset`, `keep`                      |
| **Sort rows**            | `sort_rows`           | `by`, `descending`                    |
| **Reorder columns**      | `reorder_columns`     | `columns`                             |

In the tables below, *list* means a TOML array such as `["a", "b"]`, and *table* means a TOML table of `key = value` pairs such as `{ "old" = "new" }`.

## Rename columns

`rename_columns` — gives one or more columns a new name. In the app: **Column mapping**, one rule per column with **Source column** and **New name**.

| Option    | Type                    | Required | Allowed values                         | Default |
| :-------- | :---------------------- | :------: | :------------------------------------- | :------ |
| `mapping` | table (text → text)     | Yes      | At least one pair `"current name" = "new name"` | —       |

Every current name must exist. Later steps see the new names.

```toml
[[steps]]
action = "rename_columns"
mapping = { "Last Name" = "last_name", "First Name" = "first_name" }
```

## Select columns

`select_columns` — keeps only the listed columns, in the listed order, and removes all the others. In the app: **Columns to keep**; columns toggled off are dropped from the output.

| Option    | Type         | Required | Allowed values                 | Default |
| :-------- | :----------- | :------: | :----------------------------- | :------ |
| `columns` | list of text | Yes      | At least one existing column   | —       |

```toml
[[steps]]
action = "select_columns"
columns = ["id", "name", "amount"]
```

## Drop columns

`drop_columns` — removes the listed columns and keeps all the others. In the app: **Columns to remove**. Prefer it to **Select columns** when you only discard a few columns.

| Option    | Type         | Required | Allowed values                 | Default |
| :-------- | :----------- | :------: | :----------------------------- | :------ |
| `columns` | list of text | Yes      | At least one existing column   | —       |

```toml
[[steps]]
action = "drop_columns"
columns = ["Internal ID", "tmp"]
```

## Cast types

`cast_types` — converts columns to another data type. In the app: **Type casting**, one rule per column with **Column** and **Type**.

| Option  | Type                 | Required | Allowed values                                              | Default |
| :------ | :------------------- | :------: | :---------------------------------------------------------- | :------ |
| `casts` | table (column → type)| Yes      | At least one pair; type is one of the values below          | —       |

| Type value | Name in the app          | Notes                                                                                      |
| :--------- | :----------------------- | :----------------------------------------------------------------------------------------- |
| `string`   | **Text**                 | Any value can become text.                                                                 |
| `int`      | **Whole number**         | Text must be a whole number (`12`, not `1.5` or `12 kg`). Decimal numbers are truncated.   |
| `float`    | **Decimal number**       | Text must use a dot as decimal mark (`1.5`, not `1,5`).                                    |
| `bool`     | **Boolean (True/False)** | Works from numbers (`0` is false, other values true). Text cannot be cast to a boolean.    |
| `date`     | **Date**                 | Text must be in `YYYY-MM-DD` form, for example `2024-03-05`.                              |
| `datetime` | **Date & time**          | Text must be in `YYYY-MM-DDTHH:MM:SS` form, for example `2024-03-05T10:00:00`.             |

A single value that cannot be converted makes the step fail, with a message such as `conversion from str to i64 failed in column 'amount' for 1 out of 1 values: ["abc"]`. Clean or replace such values in earlier steps.

```toml
[[steps]]
action = "cast_types"
casts = { salary = "float", hired_on = "date" }
```

## Replace values

`replace_values` — replaces exact cell values in one column. Values that are not listed stay unchanged. In the app: **Replacements**, one rule per value with **Column**, **Find** and **Replace with**; rules on the same column are grouped into one step per column.

| Option    | Type                    | Required | Allowed values                                     | Default |
| :-------- | :---------------------- | :------: | :------------------------------------------------- | :------ |
| `column`  | text                    | Yes      | An existing column                                 | —       |
| `mapping` | table (value → value)   | Yes      | At least one pair `"find" = replacement`           | —       |

- Matching is on the **whole cell**, and case-sensitive: `"YES"` does not match `"yes"` or `"YES please"`.
- Replacements can be text, numbers or `true` / `false`. The replacement must suit the column's type: replacing a number with text in a numeric column fails. Cast the column to **Text** first.
- A replacement cannot be empty (null): a preset file has no way to store it, and saving such a preset fails with *holds a value that cannot be saved to TOML*.

```toml
[[steps]]
action = "replace_values"
column = "status"
mapping = { "A" = "Active", "I" = "Inactive" }
```

## Clean text

`clean_text` — tidies text in one or more columns. In the app: **Add clean action**, then pick **Target columns**, **Operations** and **Case conversion**. Each clean action is saved as its own step.

| Option    | Type         | Required | Allowed values                                  | Default  |
| :-------- | :----------- | :------: | :---------------------------------------------- | :------- |
| `columns` | list of text | Yes      | At least one existing **text** column           | —        |
| `ops`     | list of text | No       | Any of `trim`, `collapse`, `accents`, `special` | `[]`     |
| `case`    | text         | No       | `none`, `lower`, `upper`, `title`               | `none`   |

| Value      | Name in the app               | Effect                                                                              |
| :--------- | :---------------------------- | :---------------------------------------------------------------------------------- |
| `trim`     | **Trim whitespace**           | Removes spaces at the start and end.                                                |
| `collapse` | **Collapse spaces**           | Replaces each run of spaces, tabs or line breaks with a single space.               |
| `accents`  | **Remove accents**            | `é` becomes `e`, `ç` becomes `c`. Characters with no plain-letter equivalent are removed. |
| `special`  | **Remove special characters** | Keeps only letters, digits, underscores and whitespace; removes punctuation and symbols. |
| `lower`    | **lower**                     | Lower case.                                                                         |
| `upper`    | **UPPER**                     | Upper case.                                                                         |
| `title`    | **Title**                     | First letter of each word in upper case.                                            |

The operations always apply in this order, whatever the order of the list: trim, collapse, accents, special, then case. Removing special characters can therefore leave double spaces behind. The columns must hold text: cast a numeric column to **Text** first, or the step fails with `expected String`.

```toml
[[steps]]
action = "clean_text"
columns = ["last_name", "first_name"]
ops = ["trim", "collapse"]
case = "title"
```

## Fill empty cells

`fill_nulls` — fills empty cells in one or more columns. In the app: **Columns to process**, then **Fill empty cells with** and, for a value, **Replacement value**.

| Option     | Type                         | Required                       | Allowed values                     | Default |
| :--------- | :--------------------------- | :----------------------------: | :--------------------------------- | :------ |
| `columns`  | list of text                 | Yes                            | At least one existing column       | —       |
| `strategy` | text                         | No                             | `value`, `forward`, `backward`     | `value` |
| `value`    | text, number or `true`/`false` | When `strategy = "value"`    | Any value                          | —       |

| Strategy   | Name in the app | Effect                                                    |
| :--------- | :-------------- | :-------------------------------------------------------- |
| `value`    | **A value**     | Puts `value` in every empty cell.                         |
| `forward`  | **Value above** | Copies the nearest non-empty value above the cell.        |
| `backward` | **Value below** | Copies the nearest non-empty value below the cell.        |

A cell counts as empty when it holds no value at all. A cell containing spaces or an empty text is not empty. With `forward`, empty cells at the very top stay empty; with `backward`, those at the very bottom do.

The replacement value typed in the app is text. Filling a numeric column with it turns the whole column into text; in a preset file, write a number without quotes (`value = 0`) to keep the column numeric.

```toml
[[steps]]
action = "fill_nulls"
columns = ["department"]
strategy = "value"
value = "Unknown"
```

## Add computed column

`add_computed_column` — creates a column, or overwrites an existing one, from a formula. In the app: **Add computed column**, with **New column name** and an expression built from **Columns**, **Functions** and **Separators**. Each computed column is saved as its own step, and later ones can use earlier ones.

| Option       | Type | Required | Allowed values                                                    | Default |
| :----------- | :--- | :------: | :---------------------------------------------------------------- | :------ |
| `target`     | text | Yes      | Name of the column to create. An existing name is overwritten.     | —       |
| `expression` | text | Yes      | A formula, see [Computed column functions](computed-functions.md) | —       |

```toml
[[steps]]
action = "add_computed_column"
target = "full_name"
expression = 'CONCATENER(first_name, " ", MAJUSCULE(last_name))'
```

## Filter rows

`filter_rows` — keeps only the rows that match conditions and removes the others. In the app: **Keep rows matching** **All conditions** or **Any condition**, then one rule per condition with **Column**, **Operator** and **Value**.

| Option       | Type              | Required | Allowed values                 | Default |
| :----------- | :---------------- | :------: | :----------------------------- | :------ |
| `combine`    | text              | No       | `AND` (all conditions), `OR` (any condition) | `AND` |
| `conditions` | list of conditions| Yes      | At least one condition         | —       |

Each condition has three options:

| Option     | Type                            | Required | Allowed values               |
| :--------- | :------------------------------ | :------: | :--------------------------- |
| `column`   | text                            | Yes      | An existing column           |
| `operator` | text                            | Yes      | See the operator table below |
| `value`    | text, number or `true`/`false`  | Yes      | The value to compare with    |

| Operator     | In the app      | Keeps rows where the cell…                        |
| :----------- | :-------------- | :------------------------------------------------ |
| `eq`         | **=**           | equals the value                                  |
| `neq`        | **≠**           | differs from the value                            |
| `gt`         | **>**           | is greater than the value                         |
| `gte`        | **≥**           | is greater than or equal to the value             |
| `lt`         | **<**           | is less than the value                            |
| `lte`        | **≤**           | is less than or equal to the value                |
| `contains`   | **contains**    | contains the value as plain text                  |
| `startswith` | **starts with** | starts with the value                             |
| `endswith`   | **ends with**   | ends with the value                               |

- Text comparisons are case-sensitive. `contains`, `starts with` and `ends with` treat the value as plain text (`C++` matches only `C++`), and work on any column by reading it as text.
- On a numeric column, a value typed as text is converted to a number. A value that is not a number makes the step fail with *'…' is not a number, but the column holds numbers (…). Enter a numeric value.*
- On a true/false column, the values `true`, `1` and `yes` (any case) mean true; any other text means false.
- Empty cells never match a condition, so rows with an empty cell in a filtered column are removed.

```toml
[[steps]]
action = "filter_rows"
combine = "AND"

[[steps.conditions]]
column = "status"
operator = "eq"
value = "Active"

[[steps.conditions]]
column = "salary"
operator = "gte"
value = 30000
```

## Deduplicate rows

`deduplicate_rows` — removes duplicate rows. Two rows are duplicates when all the key columns match. In the app: **Deduplication keys** and **When duplicates are found, keep**.

| Option   | Type         | Required | Allowed values                     | Default                  |
| :------- | :----------- | :------: | :--------------------------------- | :----------------------- |
| `subset` | list of text | No       | Existing columns                   | `[]` (compare all columns) |
| `keep`   | text         | No       | `first`, `last`, `none`            | `first`                  |

| Value   | In the app    | Effect                                                     |
| :------ | :------------ | :--------------------------------------------------------- |
| `first` | **First row** | Keeps the first row of each group of duplicates.           |
| `last`  | **Last row**  | Keeps the last row of each group of duplicates.            |
| `none`  | *(file only)* | Removes every row that has a duplicate, keeping none of them. |

The order of the remaining rows is not guaranteed. Add a **Sort rows** step if the order matters.

```toml
[[steps]]
action = "deduplicate_rows"
subset = ["email"]
keep = "first"
```

## Sort rows

`sort_rows` — orders rows by one or more columns. In the app: **Sort keys**, one rule per column with **Column** and **Direction** (**Asc** or **Desc**). Keys apply top to bottom: the first is the primary sort.

| Option       | Type                                  | Required | Allowed values                                         | Default |
| :----------- | :------------------------------------ | :------: | :----------------------------------------------------- | :------ |
| `by`         | list of text                          | Yes      | At least one existing column                           | —       |
| `descending` | `true`/`false`, or a list of them     | No       | One value for all keys, or one per key in `by` order   | `false` |

When `descending` is a list, it must have exactly as many entries as `by`, or the preset is refused with *sort_rows descending list length must match 'by' length*.

```toml
[[steps]]
action = "sort_rows"
by = ["department", "salary"]
descending = [false, true]
```

## Reorder columns

`reorder_columns` — puts the listed columns first, in the listed order. In the app: **Column order**, where you drag columns into place.

| Option    | Type         | Required | Allowed values                 | Default |
| :-------- | :----------- | :------: | :----------------------------- | :------ |
| `columns` | list of text | Yes      | At least one existing column   | —       |

Columns not in the list are kept and placed after the listed ones, in their current order.

```toml
[[steps]]
action = "reorder_columns"
columns = ["department", "full_name"]
```
