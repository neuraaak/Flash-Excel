# Create a launcher

Save a `.cmd` file that runs a preset on the same files when you double-click it, without opening Flash-Excel. Use it for a run you repeat on demand rather than on a schedule.

## 🔧 Prerequisites

- On the **Processing** page, the files to process are loaded and the preset is selected. See [Load source files](../files/load-source-files.md).
- The preset and the source files stay where they are: the launcher uses their current paths.

## 📝 Steps

1. On the **Processing** page, under **Scheduled and manual execution**, select **Configure execution**. The **Schedule or create a launcher** window opens.
2. Check the **Execution name**, the **Input files** and the output settings: **Destination folder**, **Format** and **Naming pattern**.
3. Select **Create a .cmd launcher**.
4. In the save dialog, choose where to save the launcher. Its name defaults to the **Execution name**, with the `.cmd` extension. Keep that extension.

## ✅ Result

The message **Launcher created. Double-click it to run this configuration.** appears, and the window shows where the launcher was saved.

Double-click the launcher to run it. A console window opens, shows one line per file, either `<file> -> <output path> (<n> rows)` or `<file> FAILED: <reason>`, and stays open until you press a key. If a file fails, the launcher goes on with the next one.

To remove a launcher, delete its `.cmd` file.

!!! note "Names and paths that are refused"
    The **Execution name** must have 1 to 200 characters, without `\ / : * ? " < > | % !`. The paths of the preset, the files and the destination folder cannot contain `%`, `!` or quotes.

## ➡️ Next steps

- [Schedule a preset](schedule-a-preset.md) to run the same configuration every day.
- [Run from the command line](run-from-the-command-line.md)
