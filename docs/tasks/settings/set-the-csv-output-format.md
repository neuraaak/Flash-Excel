# Set the CSV output format

Choose the column separator and the decimal mark of the CSV files Flash-Excel writes, for example to match the program that reads them.

## 🔧 Prerequisites

- None. The setting applies to every CSV file Flash-Excel writes: runs from the **Processing** page, scheduled tasks, launchers and command-line runs.

## 📝 Steps

1. In the sidebar, select **Settings**.
2. Under **CSV output** › **Column separator**, select **Auto**, **Semicolon ;**, **Comma ,** or **Tab**.
3. Under **Decimal mark**, select **Auto**, **Comma 1,5** or **Dot 1.5**.
4. Close the **Settings** window.

## ✅ Result

The next CSV files written use the chosen separator and decimal mark. Files written before are not changed.

**Auto**, the default for both settings, follows your Windows regional settings — the same ones Excel reads, so the file opens in columns on a double-click. Choose a fixed value when another program, or a computer with other regional settings, reads the files.

!!! note "Comma separator and comma decimals"
    With **Comma ,** as the separator, decimal numbers are always written with a dot, even if **Decimal mark** is set to **Comma 1,5**: a comma in the numbers would split them across two columns.

## ➡️ Next steps

- [Run a preset](../run/run-a-preset.md) with **Format** set to **.csv (UTF-8)**.
- [File formats](../../reference/file-formats.md)
