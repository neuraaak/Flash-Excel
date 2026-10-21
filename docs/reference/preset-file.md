# Preset file format

A preset is a text file in the [TOML](https://toml.io/) format, saved with the `.toml` extension and encoded in UTF-8. The **Presets** page writes these files for you; this page describes their format, for reading them, sharing them or writing one by hand. For what a preset is, see [Presets](../concepts/presets.md).

## Structure

A preset file has one `[meta]` table followed by any number of `[[steps]]` tables:

```toml
[meta]
name = "My preset"

[[steps]]
action = "drop_columns"
columns = ["tmp"]

[[steps]]
action = "sort_rows"
by = ["date"]
```

Steps run in the order they appear in the file. A preset with no steps is valid: it copies the data unchanged into the output format.

## The `[meta]` table

| Key                 | Type              | Required | Default        | Description                                                                                                                   |
| :------------------ | :---------------- | :------: | :------------- | :---------------------------------------------------------------------------------------------------------------------------- |
| `name`              | text              | Yes      | —              | Name shown in the preset lists.                                                                                               |
| `description`       | text              | No       | `""`           | Free description, for your own notes. The app does not display it.                                                          |
| `csv_separator`     | text              | No       | *(not set)*    | Column separator used to **read** CSV source files, for example `";"`, `","`, `"\t"` or <code>"&#124;"</code>. When not set, Flash-Excel detects it from the file. |
| `csv_encoding`      | text              | No       | `"utf8-lossy"` | Encoding used to **read** CSV source files. See below.                                                                        |
| `csv_decimal_comma` | `true` / `false`  | No       | `false`        | Read `1,5` as the number 1.5 in CSV source files. Turn it on only for files that use a comma as decimal mark.                 |
| `source_columns`    | list of text      | No       | `[]`           | Columns of the template file. Written by the app.                                                                             |
| `source_types`      | table             | No       | `{}`           | Column types of the template file. Written by the app.                                                                        |
| `source_file`       | text              | No       | `""`           | Name of the template file. Written by the app.                                                                                |

The three `csv_*` keys only affect how CSV **source** files are read. They have no effect on Excel files, and no effect on how output files are written: the output CSV format comes from [Settings](settings.md#csv-output).

The three `source_*` keys let the editor show columns without reloading the template file. Leave them as the app wrote them, or leave them out.

### `csv_encoding` values

| Value          | Use it for                                                                                                        |
| :------------- | :---------------------------------------------------------------------------------------------------------------- |
| `"utf8-lossy"` | Default. UTF-8 files. Bytes that are not valid UTF-8 are replaced with `�` instead of stopping the run.           |
| `"utf8"`       | UTF-8 files, failing with *invalid utf-8 sequence* on any invalid byte.                                           |
| `"cp1252"`     | Files saved by Excel as *CSV (separator: semicolon)* or *CSV (comma delimited)* on a Western-European Windows: accented letters then read correctly instead of as `�`. |
| `"latin-1"`    | Files encoded in ISO-8859-1.                                                                                      |

Other standard encoding names, such as `"utf-16"`, are also accepted.

!!! note "Presets saved before version 1.4.0"
    Presets saved by versions before 1.4.0 contain `csv_separator = ";"`, which forces semicolons. Delete that line to let Flash-Excel detect the separator.

!!! warning "Saving from the Presets page"
    Selecting **Save** on the **Presets** page rewrites `[meta]` with the name and the template information only: `description` and the three `csv_*` keys go back to their defaults. Add them again by hand after saving, or keep such presets out of the editor.

## The `[[steps]]` tables

Each `[[steps]]` table is one step. Its `action` key says which kind of step it is; the other keys are that step's options.

| `action`              | Options                                 |
| :-------------------- | :-------------------------------------- |
| `rename_columns`      | `mapping`                               |
| `select_columns`      | `columns`                               |
| `drop_columns`        | `columns`                               |
| `cast_types`          | `casts`                                 |
| `replace_values`      | `column`, `mapping`                     |
| `clean_text`          | `columns`, `ops`, `case`                |
| `fill_nulls`          | `columns`, `strategy`, `value`          |
| `add_computed_column` | `target`, `expression`                  |
| `filter_rows`         | `combine`, `conditions`                 |
| `deduplicate_rows`    | `subset`, `keep`                        |
| `sort_rows`           | `by`, `descending`                      |
| `reorder_columns`     | `columns`                               |

Every option, its allowed values and its default are listed in [Steps](steps.md).

The conditions of `filter_rows` are written as `[[steps.conditions]]` tables right after their step, or as an inline list:

```toml
[[steps]]
action = "filter_rows"
combine = "OR"
conditions = [
  { column = "country", operator = "eq", value = "France" },
  { column = "country", operator = "eq", value = "Belgium" },
]
```

### Writing values

- Column names that contain spaces or symbols must be quoted as keys: `{ "Last Name" = "last_name" }`.
- Text values use double quotes. For an expression that itself contains double quotes, wrap it in single quotes, which TOML reads literally: `expression = 'CONCATENER(first_name, " ", last_name)'`.
- Numbers and booleans have no quotes: `value = 30000`, `descending = true`. A quoted number is text.
- TOML has no empty (null) value. A preset cannot replace a value with an empty cell.

## Complete example

This preset reads an HR export, cleans it and keeps the active employees earning at least 30,000. It is valid as written: it loads without errors and runs on a matching file.

```toml
[meta]
name = "Monthly HR report"
description = "Clean the monthly HR export"
csv_encoding = "utf8-lossy"
csv_decimal_comma = false

[[steps]]
action = "rename_columns"
mapping = { "Last Name" = "last_name", "First Name" = "first_name" }

[[steps]]
action = "drop_columns"
columns = ["Internal ID"]

[[steps]]
action = "cast_types"
casts = { salary = "float", hired_on = "date" }

[[steps]]
action = "replace_values"
column = "status"
mapping = { "A" = "Active", "I" = "Inactive" }

[[steps]]
action = "clean_text"
columns = ["last_name", "first_name"]
ops = ["trim", "collapse"]
case = "title"

[[steps]]
action = "fill_nulls"
columns = ["department"]
strategy = "value"
value = "Unknown"

[[steps]]
action = "add_computed_column"
target = "full_name"
expression = 'CONCATENER(first_name, " ", MAJUSCULE(last_name))'

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

[[steps]]
action = "deduplicate_rows"
subset = ["full_name"]
keep = "first"

[[steps]]
action = "sort_rows"
by = ["department", "salary"]
descending = [false, true]

[[steps]]
action = "select_columns"
columns = ["full_name", "department", "salary", "hired_on"]

[[steps]]
action = "reorder_columns"
columns = ["department", "full_name"]
```

## Validation errors

Flash-Excel checks a preset file when it lists or runs it. A file that does not follow this format is not run:

- In the app, it appears in the preset list marked **unreadable**; hover over the marker to read the reason.
- From the command line, the run stops before any file is processed, with exit code `1`.

| Message                                                                 | Meaning                                                                                       |
| :---------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------- |
| *The preset file '…' contains invalid TOML syntax.*                     | The file is not valid TOML: a missing quote or bracket, a duplicated key. The details give the line. |
| *The preset '…' contains configuration errors:* followed by a list      | The TOML is valid, but a value is missing or not allowed. Each line names the location, for example `steps > 0 > cast_types > casts > amount`; steps are numbered from 0. |
| *Preset file not found: '…'.*                                           | The path given does not lead to a file.                                                       |

See [Troubleshooting](../troubleshooting.md#a-preset-is-marked-unreadable).
