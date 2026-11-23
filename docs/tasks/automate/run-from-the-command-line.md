# Run from the command line

Run a preset on one or more files from a command prompt or a script, without opening the Flash-Excel window. This is what scheduled tasks and launchers do behind the scenes, and you can use it in your own batch files.

## 🔧 Prerequisites

- Flash-Excel installed. See [Get started](../../get-started.md).
- The path of the Flash-Excel executable. To find it, open **Configure execution** on the **Processing** page: the window shows **Uses the installed application:** followed by the path.
- A preset file. Your presets are in `Documents\flash-excel\presets`, one `.toml` file per preset.

## 📝 Steps

1. Open a Command Prompt or a PowerShell window.
2. Run the Flash-Excel executable with `--preset` and `--input`. Replace the paths with yours:

    === "Command Prompt"

        ```bat
        "<path to>\Flash-Excel.exe" --preset "%USERPROFILE%\Documents\flash-excel\presets\monthly_report.toml" --input "C:\Data\january.xlsx" "C:\Data\february.xlsx" --output "C:\Data\clean"
        ```

    === "PowerShell"

        ```powershell
        & "<path to>\Flash-Excel.exe" --preset "$HOME\Documents\flash-excel\presets\monthly_report.toml" --input "C:\Data\january.xlsx" "C:\Data\february.xlsx" --output "C:\Data\clean"
        ```

3. Add options if needed:

    | Option              | Effect                                                                 | Default                        |
    | :------------------ | :--------------------------------------------------------------------- | :----------------------------- |
    | `--output <folder>` | Destination folder. A relative folder is created inside the default one. | `Documents\flash-excel\output` |
    | `--format <format>` | `keep` (same as source), `xlsx`, `csv` or `parquet`.                   | `keep`                         |
    | `--pattern <text>`  | Output file name without extension; `{name}` is the source file name.  | `{name}_clean`                 |
    | `--debug`           | Writes more detail to the log file.                                    | Off                            |

## ✅ Result

Each file is processed on its own, and the window prints one line per file:

```text
january.xlsx -> C:\Data\clean\january_clean.xlsx (1250 rows)
february.xlsx FAILED: <reason>
```

A failing file does not stop the others. When the command ends, its exit code tells a script what happened:

| Exit code | Meaning                              |
| :-------: | :----------------------------------- |
| `0`       | Every file succeeded.                |
| `1`       | At least one file failed.            |
| `2`       | The command-line arguments are wrong. |

The same lines are written to the Flash-Excel log file. See [Data locations](../../reference/data-locations.md).

!!! warning "Wait for the run in an interactive prompt"
    Flash-Excel is a windowed application. Typed directly at an interactive Command Prompt, the prompt can come back before the run ends, with the result lines printed after it, and `%ERRORLEVEL%` is then not the run's exit code. To wait for the end and read the exit code, run the command from a batch file (`.cmd`), as launchers do.

!!! note "Same settings as the app"
    A command-line run uses the CSV output settings chosen in **Settings** › **CSV output**. See [Set the CSV output format](../settings/set-the-csv-output-format.md).

!!! tip "Let Flash-Excel write the command"
    [Schedule a preset](schedule-a-preset.md) and [Create a launcher](create-a-launcher.md) build this command for you from the **Processing** page.

## ➡️ Next steps

- [Command line](../../reference/command-line.md) — the full option reference.
- [Schedule a preset](schedule-a-preset.md)
