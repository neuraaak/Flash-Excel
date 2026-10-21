# FAQ

## Does Flash-Excel change my source file?

No. Every run writes a new output file, by default `Documents\flash-excel\output\<name>_clean.<extension>`, and leaves the source as it is. The one exception is a naming pattern of `{name}` with the source's own folder and format: the output then replaces the source. See [File formats](reference/file-formats.md#name-and-location).

## Does Flash-Excel run on macOS or Linux?

No. Flash-Excel is a Windows application: its installer, its settings and its scheduling all rely on Windows.

## Do I need administrator rights?

No. Flash-Excel installs for your Windows user only, and updates install the same way. See [Get started](get-started.md).

## Are my files sent anywhere?

No. Files are read, transformed and written on your PC. The only network access is the check for a new version when Flash-Excel starts, and the download of an update when you select it. See [Automatic updates](concepts/automatic-updates.md).

## Which files can Flash-Excel read and write?

It reads `.xlsx`, `.xlsm`, `.xls` and `.csv` files, and writes `.xlsx`, `.csv` and `.parquet` files. See [File formats](reference/file-formats.md).

## Can I process another sheet than the first one?

No. Flash-Excel reads the first sheet of a workbook only. Move the sheet you need to the first position in Excel, save, and run again.

## Can I process several files at once?

Yes. Select or drop several files on the **Processing** page: they are processed one after the other with the same preset, each into its own output file. See [Run a preset](tasks/run/run-a-preset.md).

## Is there a size limit for files?

There is no fixed limit. Each file is read entirely into memory, so very large files need enough free memory on your PC.

## Can I try a preset without writing a file?

Yes. **Preview** on the **Processing** page shows the result on the first 100 rows, without writing anything. See [Preview a transformation](tasks/run/preview-a-transformation.md).

## Can I change the order of the steps?

Not in the editor: it runs the configured steps in a fixed order designed so each step finds the columns it needs. A preset file written by hand runs its steps in the order of the file. See [Steps and their order](concepts/steps-and-order.md).

## Why are the computed column functions in French?

They follow the function names of the French version of Excel (`SI`, `CONCATENER`, `ARRONDI`…). They stay the same in every interface language so that presets work for everyone. See [Computed column functions](reference/computed-functions.md).

## How do I share presets with colleagues?

Send the preset file with **Export**, or put presets in a shared folder that everyone adds under **Settings** › **Read-only preset sources**. See [Export a preset](tasks/presets/export-a-preset.md) and [Use shared preset folders](tasks/presets/use-shared-preset-folders.md).

## Can I keep presets under version control?

Yes. A preset is a plain-text `.toml` file, so it can be stored in Git or any versioned folder and compared line by line. See [Preset file format](reference/preset-file.md).

## Can a preset run automatically every day?

Yes. **Configure execution** on the **Processing** page creates a Windows scheduled task, or a `.cmd` launcher you double-click. Flash-Excel does not need to be open, but your Windows session does. See [Schedule a preset](tasks/automate/schedule-a-preset.md).

## Why doesn't Flash-Excel run the schedule itself?

Windows Task Scheduler does it better: a task survives a restart, runs without Flash-Excel being open and records each run's result. **Configure execution** creates that task for you. See [Schedule a preset](tasks/automate/schedule-a-preset.md).

## Can I run a preset from a script?

Yes, with `Flash-Excel.exe --preset … --input …`. See [Command line](reference/command-line.md).

## What happens to my presets when I update or uninstall?

They stay. Presets, settings, outputs and logs are stored outside the installation folder, which is the only thing updates replace and uninstalling removes. See [Data locations](reference/data-locations.md#uninstalling).

## Which version am I running?

The version number is shown in the bottom-right corner of the window, for example `v1.5.0`. See [Release notes](release-notes.md) for what changed.

## How do I switch the interface to French?

Select **Settings** in the sidebar, then **French** under **Language**. See [Change the language](tasks/settings/change-the-language.md).

## Is Flash-Excel free?

Yes. Flash-Excel is open source, under the MIT license. Its source code is on [GitHub](https://github.com/neuraaak/Flash-Excel).
