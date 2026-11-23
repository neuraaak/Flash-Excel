# Glossary

Action name
:   The technical name of a kind of step in a preset file, such as `filter_rows` for **Filter rows**. See [Steps](steps.md).

Batch
:   Several source files processed in one run with the same preset. Each file is processed and written on its own.

Computed column
:   A column created by the **Add computed column** step from an expression. See [Computed column functions](computed-functions.md).

Console
:   The panel at the bottom of the **Processing** page that shows the messages of a run: files loaded, steps applied, warnings and errors.

Destination folder
:   The folder where a run writes its output files. Default: `Documents\flash-excel\output`.

Error mode
:   What a run does when a file or a step fails, set under **On error**: **Skip file**, **Stop all** or **Ignore**. See [Error handling](../concepts/error-handling.md).

Expression
:   The formula of a computed column, for example `CONCATENER(first_name, " ", last_name)`.

Headless run
:   A run without the window, started from the command line, a launcher or a scheduled task. See [Command line](command-line.md).

Launcher
:   A `.cmd` file created by Flash-Excel that runs a preset on fixed files when you double-click it. See [Create a launcher](../tasks/automate/create-a-launcher.md).

Local preset
:   A preset stored in `Documents\flash-excel\presets`, which you can edit, save, delete and export.

Naming pattern
:   The name given to output files, without extension. `{name}` stands for the source file name. Default: `{name}_clean`.

Output file
:   The file a run writes. The source file is not changed.

Palette
:   A set of interface colours (**Blue Gray**, **GitHub**, **Warm Dark**), each with a dark and a light mode.

Preset
:   A saved list of steps, stored as a `.toml` file, that you apply to source files. See [Presets](../concepts/presets.md).

Preview
:   The result of a preset on the first 100 rows of a file, shown without writing anything. See [Preview a transformation](../tasks/run/preview-a-transformation.md).

Queue
:   The list of source files loaded on the **Processing** page, each with its status: **Pending**, **Running**, **Done**, **Error** or **Skipped**.

Read-only preset source
:   A shared folder added in **Settings** whose presets are listed next to yours but cannot be changed from Flash-Excel. See [Use shared preset folders](../tasks/presets/use-shared-preset-folders.md).

Scheduled task
:   A Windows Task Scheduler task that runs a preset every day at a set time. See [Schedule a preset](../tasks/automate/schedule-a-preset.md).

Source file
:   An Excel or CSV file you apply a preset to.

Step
:   One transformation in a preset, such as **Rename columns** or **Sort rows**. Flash-Excel offers 12 kinds of step. See [Steps and their order](../concepts/steps-and-order.md).

Template file
:   The file loaded under **Load the Excel template** on the **Presets** page. It supplies the column names and types the step editors offer. The preset remembers them, so the file is not needed afterwards.

TOML
:   The plain-text format of preset files. See [Preset file format](preset-file.md).
