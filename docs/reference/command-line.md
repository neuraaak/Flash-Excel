# Command line

Flash-Excel can apply a preset without opening its window. This is what launchers and scheduled tasks use, and you can call it yourself from a Command Prompt, a batch file or another tool. For a step-by-step guide, see [Run from the command line](../tasks/automate/run-from-the-command-line.md).

## Syntax

```bat
flash-excel.exe --preset <preset.toml> --input <file> [<file> …] [--output <folder>] [--format keep|xlsx|csv|parquet] [--pattern <pattern>] [--debug]
```

`flash-excel.exe` is the program in the Flash-Excel installation folder. The exact path on your PC is shown in the **Schedule or create a launcher** window, after *Uses the installed application:*. Use the full path, in quotes, when you call it from another folder.

There is only one program: given `--preset`, it runs without a window; without `--preset`, it opens the window as usual.

## Options

| Option              | Required | Default                          | Description                                                                                                                         |
| :------------------ | :------: | :------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| `--preset <path>`   | Yes      | —                                | The `.toml` preset file to apply. Any preset file works: local, shared or elsewhere.                                                |
| `--input <path> …`  | Yes      | —                                | One or more source files, separated by spaces. Each file is processed on its own.                                                   |
| `--output <folder>` | No       | `Documents\flash-excel\output`   | Destination folder, created if needed. A relative folder is placed inside `Documents\flash-excel\output`.                            |
| `--format <format>` | No       | `keep`                           | Output format: `keep` (same as the source file), `xlsx`, `csv` or `parquet`.                                                         |
| `--pattern <text>`  | No       | `{name}_clean`                   | Name of each output file, without extension. `{name}` is replaced by the source file name without its extension.                    |
| `--debug`           | No       | off                              | Writes detailed messages to the log file.                                                                                           |
| `-h`, `--help`      | No       | —                                | Shows the list of options. Must be combined with `--preset` to reach the command-line mode, for example `flash-excel.exe --preset x --help`. |

Paths containing spaces must be in double quotes.

### Output file names

With the defaults, `C:\Data\sales.xlsx` gives `Documents\flash-excel\output\sales_clean.xlsx`. An existing file with the same name is replaced.

`keep` reuses the source file's extension. It works for `.xlsx` and `.csv` sources. For `.xls` and `.xlsm` sources, Flash-Excel cannot write that format and the file fails with *Unsupported format: 'xls'*: pass `--format xlsx`. See [File formats](file-formats.md).

### Settings used from the app

A command-line run uses the settings saved in the app:

- the **CSV output** settings (**Column separator** and **Decimal mark**) for CSV output files;
- the **Language**, for the true/false labels in Excel output files (`True`/`False` in English, `VRAI`/`FAUX` in French).

The preset's own `[meta]` options decide how CSV source files are read. See [Settings](settings.md) and [Preset file format](preset-file.md).

## Behaviour

- Files are processed one after the other, in the order given.
- A file that fails — unreadable, locked by Excel, a step error, an output that cannot be written — gets no output file. **The next files are still processed.** There is no equivalent of the window's **On error** choice.
- If the preset itself cannot be loaded, nothing is processed.

### Messages

For each file, one line is printed and written to the [log file](data-locations.md#logs):

```text
sales.xlsx -> C:\Users\me\Documents\flash-excel\output\sales_clean.xlsx (1250 rows)
march.csv FAILED: No such file or directory (os error 2): ...
```

Successful files are reported on the standard output, failed ones on the standard error.

### Console

Flash-Excel is a windowed program. When you start it from a Command Prompt or PowerShell, it writes its messages into that console. When nothing started it from a console — a scheduled task, a double-click — there is no console and the messages go only to the log file. The exit code is set in every case.

!!! tip "Waiting for the end of the run"
    A batch file (`.cmd` or `.bat`) waits for each program it starts, so it can read the exit code in `%ERRORLEVEL%`. This is how the launchers created by Flash-Excel work. In an interactive prompt, Windows may give the prompt back before a windowed program ends: run the command from a batch file when you need the exit code.

## Exit codes

| Code | Meaning                                                                                                      |
| :--: | :----------------------------------------------------------------------------------------------------------- |
| `0`  | Every input file was processed and written.                                                                  |
| `1`  | At least one input file failed, or the preset could not be loaded (file not found, invalid preset).          |
| `2`  | Invalid command line: a required option is missing, an option is unknown, or `--format` has another value.    |

## Examples

Apply a preset to one file, with the default output folder and format:

```bat
flash-excel.exe --preset "%USERPROFILE%\Documents\flash-excel\presets\monthly_hr_report.toml" --input "C:\Exports\hr.xlsx"
```

Process three files into a CSV in a chosen folder:

```bat
flash-excel.exe --preset clean.toml --input jan.xlsx feb.xlsx mar.xlsx --output "D:\Reports\Q1" --format csv
```

Name the outputs after the month and convert `.xls` sources to `.xlsx`:

```bat
flash-excel.exe --preset clean.toml --input "C:\Exports\report.xls" --format xlsx --pattern "{name}_2026-10"
```

Use the exit code in a batch file:

```bat
@echo off
"C:\path\to\flash-excel.exe" --preset clean.toml --input a.xlsx b.xlsx
if errorlevel 1 echo At least one file failed. See the log file.
```

## Scheduling

Flash-Excel does not schedule runs itself. Windows Task Scheduler does it better: it survives a restart and reports failures. The **Configure execution** button on the **Processing** page creates a scheduled task or a `.cmd` launcher that calls this command line for you. See [Schedule a preset](../tasks/automate/schedule-a-preset.md) and [Create a launcher](../tasks/automate/create-a-launcher.md).
