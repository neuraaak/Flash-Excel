# Stop a run

Interrupt a run in progress, for example when you notice the wrong preset or the wrong files.

## 🔧 Prerequisites

- A run in progress on the **Processing** page. See [Run a preset](run-a-preset.md).

## 📝 Steps

1. On the **Processing** page, select the square stop button to the right of **Run preset**. It is available only while a run is in progress.

## ✅ Result

Flash-Excel lets the current step finish, then stops before the next step or the next file. The **Console** shows **Run stopped by user.**

- Files already marked **Done** are written and stay in the destination folder.
- The file being processed is not written if steps were still left to apply, and is marked **Skipped**.
- Files not reached yet are marked **Skipped**.

To process the remaining files, select **Load file**, pick only those files, then select **Run preset**. See [Load source files](../files/load-source-files.md).

## ➡️ Next steps

- [Run a preset](run-a-preset.md)
- [Error handling](../../concepts/error-handling.md)
