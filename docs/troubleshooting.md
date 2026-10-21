# Troubleshooting

Each entry starts from what you see. Error messages appear in the **Console** of the **Processing** page, in a message at the bottom of the window, or on the command line.

!!! tip "Where to find more detail"
    Every run, error and update check is recorded in the log file `%LOCALAPPDATA%\flash-excel\logs\flash-excel.log`. Paste that path into the address bar of File Explorer to open it. See [Data locations](reference/data-locations.md#logs).

## Unsupported format: 'xls' {#unsupported-format-xls}

**Symptom** — A run on an `.xls` or `.xlsm` file fails with *Unsupported format: 'xls'. Expected 'xlsx', 'csv', or 'parquet'.* (or `'xlsm'`), after the steps have run.

**Cause** — **Format** is set to **Same as source**. Flash-Excel reads `.xls` and `.xlsm` files but cannot write them.

**Fix**

1. On the **Processing** page, under **Output**, set **Format** to **.xlsx (Excel)**.
2. Select **Run preset** again.

On the command line, add `--format xlsx`. See [File formats](reference/file-formats.md).

## Unsupported file format. Allowed: .xlsx, .xls, .xlsm, .csv {#unsupported-file-format}

**Symptom** — Loading a file shows *File error:* followed by this message, or a dropped file is not added to the queue.

**Cause** — The file has another extension, for example `.txt`, `.ods` or `.xlsb`.

**Fix** — Open the file in Excel and save it as `.xlsx` or `.csv`, then load that copy.

## Excel file contains no readable sheets {#excel-file-contains-no-readable-sheets}

**Symptom** — A run or a preview fails with *Excel file contains no readable sheets.*

**Cause** — The workbook has no sheet Flash-Excel can read, or the file is damaged.

**Fix** — Open the workbook in Excel, check that its **first** sheet holds the data, and save it again as `.xlsx`. Flash-Excel reads the first sheet only.

## A CSV source loads as a single column {#csv-source-single-column}

**Symptom** — The template shows one column whose name contains the whole header line, such as `name,age,city`. Runs then fail with *"…" not found* or *unable to find column*.

**Cause** — The CSV is read with the wrong separator. Either the preset forces one with `csv_separator` — presets saved before version 1.4.0 contain `csv_separator = ";"` — or the separator could not be detected and `;` was used.

**Fix**

1. Open the preset file (`Documents\flash-excel\presets\<name>.toml`) in a text editor such as Notepad.
2. In `[meta]`, delete the `csv_separator` line to let Flash-Excel detect the separator, or set it to the file's separator, for example `csv_separator = ","`.
3. Save the file and run again.

See [Preset file format](reference/preset-file.md#the-meta-table).

## Accented letters appear as � in a CSV source {#accented-letters-in-csv-source}

**Symptom** — After loading or processing a CSV file, letters such as `é` or `ç` show as `�`.

**Cause** — The file is not encoded in UTF-8. Excel's *CSV (separator: semicolon)* and *CSV (comma delimited)* formats save in the Windows encoding (Windows-1252 on Western-European systems), while Flash-Excel reads UTF-8 by default.

**Fix** — In the preset file, add `csv_encoding = "cp1252"` to `[meta]`, then run again. Alternatively, save the file from Excel as *CSV UTF-8 (comma delimited)*. See [Preset file format](reference/preset-file.md#csv_encoding-values).

## Decimal numbers stay text in a CSV source {#decimal-numbers-stay-text}

**Symptom** — A column of numbers such as `1,5` is treated as text: sorting is alphabetical, and **Cast types** to **Decimal number** fails with *conversion from `str` to `f64` failed*.

**Cause** — The file uses a comma as decimal mark. Flash-Excel reads a dot as decimal mark unless told otherwise.

**Fix** — In the preset file, add `csv_decimal_comma = true` to `[meta]`. See [Preset file format](reference/preset-file.md#the-meta-table).

## An output CSV opens in a single column in Excel {#output-csv-single-column}

**Symptom** — Double-clicking an output `.csv` file opens Excel with all values in column A.

**Cause** — The file's separator or decimal mark does not match the regional settings of the PC that opens it. This happens when **CSV output** is forced to a value, or when the file is opened on a PC with other regional settings than the one that wrote it.

**Fix**

1. Select **Settings** in the sidebar.
2. Under **CSV output**, set **Column separator** and **Decimal mark** to **Auto** to match this PC, or to the values the receiving PC expects.
3. Run the preset again.

To open an existing file without re-running, use Excel's **Data** › **From Text/CSV** and choose the separator. See [Set the CSV output format](tasks/settings/set-the-csv-output-format.md).

## Accented letters look wrong in an output CSV opened in Excel {#accented-letters-in-output-csv}

**Symptom** — An output `.csv` opened by double-click in Excel shows `Ã©` instead of `é`.

**Cause** — Output CSV files are written in UTF-8. On a double-click, Excel may read them with the Windows encoding instead.

**Fix** — Choose **.xlsx (Excel)** as output **Format** when the file is meant for Excel. To open the CSV as it is, use **Data** › **From Text/CSV** in Excel and choose *65001: Unicode (UTF-8)* as file origin.

## Permission denied, or the file is being used by another process {#file-in-use}

**Symptom** — A file fails with a message such as *Permission denied* or *being used by another process*. Its status becomes **Error**.

**Cause** — The output file (or, less often, the source file) is open in Excel or another program, which locks it.

**Fix** — Close the file in Excel, then run again. With **Skip file**, the other files of the run are processed anyway; only the locked one needs a new run.

## A step cannot find a column {#column-not-found}

**Symptom** — A step fails with *"Amount" not found* or *unable to find column "Amount"; valid columns: [...]*.

**Cause** — The step names a column that does not exist at that point: the source file has different column names than the template, the name differs by case or spaces, or an earlier step renamed or removed the column.

**Fix**

1. Compare the column names of the source file with those in the message's list of valid columns.
2. On the **Presets** page, load the current file under **Load the Excel template**. If the **Column layout changed** dialog opens, select **Load & clean up references** to remove the missing columns from the steps, then fix the steps that need them.
3. Select **Save**, then run again.

See [Steps and their order](concepts/steps-and-order.md).

## A computed column says a name is not available {#is-not-available-use-column-names-or-catalog-functions}

**Symptom** — The **Add computed column** step fails with *Expression not allowed: '…' is not available. Use column names or catalog functions.*

**Cause** — The expression contains a name that is neither a column at this step nor a function. Common reasons: a typo, a function written in lower case (`si` instead of `SI`), or a column renamed or removed by an earlier step.

**Fix** — Write function names in upper case, wrap column names that contain spaces or symbols in brackets (`[Unit price]`), and use the column's name as it is at this step. Selecting the column under **Columns** in the editor inserts the right form. See [Computed column functions](reference/computed-functions.md).

## Invalid syntax in a computed column {#invalid-syntax}

**Symptom** — The **Add computed column** step fails with *Invalid syntax:* followed by details.

**Cause** — A parenthesis or a quote is not closed, a comma is missing between arguments, `=` is used instead of `==`, or a bracketed name such as `[Unit price]` matches no column.

**Fix** — Check the punctuation of the expression and the exact spelling of bracketed column names. See [Computed column functions](reference/computed-functions.md#operators).

## The truth value of an Expr is ambiguous {#truth-value-ambiguous}

**Symptom** — The **Add computed column** step fails with *Evaluation error: the truth value of an Expr is ambiguous*.

**Cause** — The expression combines conditions with `and`, `or`, `not` or `in`.

**Fix** — Use `&` for *and*, `|` for *or* and `~` for *not*, with each comparison in parentheses: `SI((age >= 18) & (age < 65), "working age", "other")`.

## '…' is not a number, but the column holds numbers {#not-a-number}

**Symptom** — **Filter rows** fails with *'18 years' is not a number, but the column holds numbers (Int64). Enter a numeric value.*

**Cause** — A condition on a numeric column has a value that is not a number.

**Fix** — On the **Presets** page, open **Filter rows** and type only the number in **Value**, with a dot as decimal mark (`18`, `1.5`). Then select **Save**.

## Conversion from str to … failed {#conversion-failed}

**Symptom** — **Cast types** fails with *conversion from `str` to `i64` failed in column 'amount' for 3 out of 1250 values: [...]*. The type may also read `f64`, `date` or `datetime[μs]`.

**Cause** — Some values cannot be converted: text in a number column, a comma as decimal mark, a decimal number cast to **Whole number**, or a date that is not in `YYYY-MM-DD` form. The message lists the values that failed.

**Fix** — Clean those values in the steps before **Cast types**, for example with **Replace values** or **Clean text**, or cast to another type. See [Steps › Cast types](reference/steps.md#cast-types).

## Expected String in Clean text or a text function {#expected-string}

**Symptom** — **Clean text**, or a text function such as `MAJUSCULE`, fails with *invalid series dtype: expected `String`, got `i64`*.

**Cause** — The column holds numbers or dates, not text.

**Fix** — Add the column to **Cast types** with type **Text**. Cast types runs before Clean text and computed columns.

## The output has fewer rows than expected {#fewer-rows}

**Symptom** — The output, or the preview, has fewer rows than expected, or none at all.

**Cause** — **Filter rows** removes rows whose cells are empty in a filtered column, and text comparisons are case-sensitive (`Active` does not match `active`). **Deduplicate rows** also removes rows. The preview works on the first 100 rows only, so it may show *No rows remain in this sample after transformation* while the full file still has matching rows.

**Fix** — Check the filter values' case and spelling; clean the text first with **Clean text** if needed. Run the preset on the whole file to see the real result.

## A preset is marked unreadable {#a-preset-is-marked-unreadable}

**Symptom** — A preset appears in the list with the marker **unreadable**, and cannot be opened or run.

**Cause** — Its file is not a valid preset: invalid TOML syntax, or a missing or wrong value. This usually follows a hand edit. Hover over the marker to read the exact reason, such as *contains invalid TOML syntax* or *contains configuration errors*.

**Fix**

1. Open the file in `Documents\flash-excel\presets` with a text editor.
2. Fix the line named in the reason. Steps are numbered from 0 in the message.
3. Save the file. The preset becomes readable the next time the list is loaded.

See [Preset file format](reference/preset-file.md#validation-errors).

## Preset saved, but these steps were refused {#steps-refused}

**Symptom** — **Save** shows *Preset saved, but these steps were refused and are not in the file:* followed by step names.

**Cause** — Those steps were incomplete or had values a preset does not accept, for example a step with no column selected. The preset was saved without them.

**Fix** — Open each named step, complete it or clear it, then select **Save** again.

## A preset already uses the file {#preset-file-name-taken}

**Symptom** — **Save** fails with *A preset already uses the file '…'. Choose another name.*

**Cause** — Two preset names that differ only by punctuation or case give the same file name (`Sales report!` and `sales report` both give `sales_report.toml`).

**Fix** — Give the preset a name that differs by at least one letter or digit.

## The preset holds a value that cannot be saved to TOML {#value-cannot-be-saved}

**Symptom** — **Save** fails with *The preset '…' holds a value that cannot be saved to TOML (a null inside a step).*

**Cause** — A step contains an empty value that a preset file cannot store, typically a **Replace values** rule whose **Replace with** is empty.

**Fix** — Give the rule a replacement value, or remove it, then select **Save** again.

## Changes to a preset are not used by the run {#changes-not-used}

**Symptom** — **Preview** or **Run preset** behaves as if your latest changes to the steps were not there.

**Cause** — Runs and previews use the preset as saved on disk.

**Fix** — On the **Presets** page, select **Save**, then go back to **Processing** and select the preset again.

## Shared presets are missing, or cannot be saved or exported {#shared-presets}

**Symptom** — Presets from a shared folder do not appear in the list; or, for a shared preset, **Save** and **Delete** are disabled and **Export** fails with *Preset file is outside the presets directory*.

**Cause** — A shared folder that cannot be reached (network drive disconnected, folder moved) is skipped; the log records *preset source unavailable*. Shared presets are read-only by design and cannot be exported from Flash-Excel.

**Fix** — Check that the folder opens in File Explorer, and correct its **Folder path** under **Settings** › **Read-only preset sources** if needed. To get your own editable copy of a shared preset, copy its `.toml` file into `Documents\flash-excel\presets` with File Explorer. See [Use shared preset folders](tasks/presets/use-shared-preset-folders.md).

## A run is already in progress {#run-in-progress}

**Symptom** — Starting a run shows *A run is already in progress*.

**Cause** — A previous run has not finished yet.

**Fix** — Wait for it to end, or stop it with the square button next to **Run preset**. See [Stop a run](tasks/run/stop-a-run.md).

## The scheduled task did not run {#scheduled-task-did-not-run}

**Symptom** — No output file was written at the scheduled time.

**Cause** — Possible causes:

- Tasks created by Flash-Excel run only while your Windows session is open. They do not run when you are signed out or the PC is off, and a missed time is not caught up later.
- A preset or input file was moved, renamed or deleted after the task was created: the task uses the exact paths it was created with.
- A file failed: the run went on with the other files, and the task ended with result `0x1`.

**Fix**

1. Open **Task Scheduler**, then **Task Scheduler Library** › **Flash-Excel**, and select the task. Check **Last Run Time** and **Last Run Result**.
2. Open the log file and look for lines ending in *FAILED* at that time.
3. If paths changed, create the task again from **Configure execution** on the **Processing** page.

See [Schedule a preset](tasks/automate/schedule-a-preset.md).

## The scheduling command is too long {#command-too-long}

**Symptom** — **Advanced: copy the scheduling command** warns that *Windows cannot create this task with a pasted /tr command because it exceeds 261 characters*.

**Cause** — With many or long file paths, the command exceeds the length Windows accepts for a pasted `schtasks` command.

**Fix** — Select **Add to Task Scheduler** instead: Flash-Excel then registers the full configuration itself, without that limit.

## Scheduling commands cannot contain %, !, quotes or newlines {#scheduling-forbidden-characters}

**Symptom** — **Add to Task Scheduler** or **Create a .cmd launcher** fails with this message.

**Cause** — A path, the output folder or the naming pattern contains `%`, `!` or `"`. These characters change meaning in Windows commands.

**Fix** — Rename the files or folders concerned, or choose another output folder or naming pattern, then try again.

## Enter a name of 1–200 characters without reserved filename characters {#execution-name-invalid}

**Symptom** — Creating a scheduled task or a launcher fails with this message.

**Cause** — **Execution name** is empty, too long, ends with a dot or a space, or contains one of `\ / : * ? " < > | % !`.

**Fix** — Enter a plain name, for example `Monthly HR report`.

## Start time must use HH:mm {#start-time-invalid}

**Symptom** — **Add to Task Scheduler** fails with *Start time must use HH:mm (00:00–23:59)*.

**Fix** — Enter the **Daily time (scheduled task)** as two-digit hours and minutes, for example `07:30`.

## No output in the Command Prompt {#no-console-output}

**Symptom** — A command-line run prints nothing, or the prompt comes back before the run ends.

**Cause** — Flash-Excel is a windowed program: it writes to a console only when started from one, and an interactive prompt may not wait for it.

**Fix** — Run the command from a `.cmd` batch file, which waits for it and can read `%ERRORLEVEL%`, and check the log file for the result of each file. See [Command line](reference/command-line.md#console).

## The update link never appears, or the update fails {#the-update-link-never-appears-or-the-update-fails}

**Symptom** — No **Update to v…** link appears although a newer version exists, or selecting it shows **Updating…** and then nothing changes.

**Cause** — The update server could not be reached (no internet connection, proxy or firewall), or the downloaded update did not pass the signature check. The log records *update check FAILED* or *update apply FAILED* with the reason.

**Fix**

1. Check your internet connection and restart Flash-Excel: the check runs at each start.
2. If it still fails, download the latest `Flash-Excel-<version>-setup.exe` from the [GitHub releases page](https://github.com/neuraaak/Flash-Excel/releases) and run it. Your presets and settings are kept.

See [Automatic updates](concepts/automatic-updates.md) and [Update Flash-Excel](tasks/update/update-flash-excel.md).

## Still stuck?

Open an issue on [GitHub](https://github.com/neuraaak/Flash-Excel/issues) with the error message, what you were doing, and the matching lines of the log file. Remove any confidential data from them first.
