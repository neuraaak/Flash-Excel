# File formats

## Source files (read)

| Format                       | Extensions               | What is read                                         |
| :--------------------------- | :----------------------- | :--------------------------------------------------- |
| Excel workbook               | `.xlsx`, `.xlsm`, `.xls` | The **first sheet** only. Its first row gives the column names. |
| CSV (delimited text)         | `.csv`                   | The whole file. Its first line gives the column names. |

The file pickers and the drop zone accept only these four extensions. Another file is refused with *Unsupported file format. Allowed: .xlsx, .xls, .xlsm, .csv*.

### Excel files

- Only the first sheet of the workbook is read; the other sheets are ignored. To process another sheet, move it to the first position in Excel and save.
- Cells containing formulas are read as their last calculated values.
- Formatting (colours, fonts, column widths, merged cells) is not read.
- The workbook must not be locked by another program while it is read. If Excel holds it open, the file fails; close it in Excel and run again.

### CSV files

| Aspect        | Behaviour                                                                                                                                  | Preset option                    |
| :------------ | :----------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------- |
| Separator     | Detected from the start of the file among `;`, `,`, tab and <code>&#124;</code>. When detection is not conclusive, `;` is used.                            | `csv_separator` forces one.      |
| Encoding      | UTF-8. Bytes that are not valid UTF-8 (for example accented letters saved in Windows-1252) become `�`.                                    | `csv_encoding`, e.g. `"cp1252"`. |
| Decimal mark  | Dot: `1.5` is a number, `1,5` stays text.                                                                                                  | `csv_decimal_comma = true`.      |
| Column types  | Guessed from every row of the file: a column is numeric only if all its values are numbers. Dates stay text until you cast them.         | —                                |
| Empty fields  | Read as empty cells, which **Fill empty cells** can fill.                                                                                  | —                                |

The preset options are described in [Preset file format](preset-file.md#the-meta-table). From the command line, a source file whose extension is not an Excel one is read as CSV.

!!! note "Column types in the editor"
    To keep the editor fast, the column types it shows for a CSV template are guessed from the first 300 rows. A run reads every row, so a column that changes from numbers to text further down is text in the run even if the editor showed it as a number.

## Output files (write)

On the **Processing** page, **Format** offers four choices; on the command line, `--format` takes the matching value.

| Format (in the app)    | `--format` | Extension written       | Notes                                                                                              |
| :--------------------- | :--------- | :---------------------- | :------------------------------------------------------------------------------------------------- |
| **Same as source**     | `keep`     | Same as the source file | Works for `.xlsx` and `.csv` sources only. See the warning below.                                   |
| **.xlsx (Excel)**      | `xlsx`     | `.xlsx`                 | One sheet. Dates as `DD/MM/YYYY`, dates and times as `DD/MM/YYYY HH:MM:SS`. True/false values written as text in the interface language: `True`/`False` or `VRAI`/`FAUX`. |
| **.csv (UTF-8)**       | `csv`      | `.csv`                  | UTF-8 text with a header line. Separator and decimal mark from **Settings** › **CSV output**.        |
| **.parquet**           | `parquet`  | `.parquet`              | Columnar data file for data tools (Power BI, Python, databases). Keeps column types exactly.        |

!!! warning "**Same as source** with `.xls` and `.xlsm` files"
    Flash-Excel cannot write the old `.xls` format, nor macro-enabled `.xlsm` workbooks. With **Same as source**, such a source file fails with *Unsupported format: 'xls'* (or `'xlsm'`) after all steps have run. Choose **.xlsx (Excel)** for these files.

### Name and location

- The output is written to the **Destination folder** (default `Documents\flash-excel\output`). A relative folder is placed inside that default folder.
- Its name follows the **Naming pattern** (default `{name}_clean`), where `{name}` is the source file name without its extension: `sales.xlsx` gives `sales_clean.xlsx`.
- An existing file with the same name is replaced without warning. Choose a pattern that differs from `{name}` if the output goes to the source folder, so the source file is not overwritten.
- The source file itself is never modified otherwise.

Formatting, formulas, other sheets and macros of the source are not carried over to the output: the output holds values only.

See also [Data locations](data-locations.md) and [Set the CSV output format](../tasks/settings/set-the-csv-output-format.md).
