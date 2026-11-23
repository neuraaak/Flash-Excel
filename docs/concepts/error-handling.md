# Error handling

A run can fail for a file — the file is open in Excel, a step refers to a column that is missing, a value cannot be converted. The **On error** choice on the **Processing** page decides what Flash-Excel does next. It matters most when you process several files in one run.

## The three choices

| Choice (as shown in the app)               | When a step fails                                                                                  | Rest of the run                    |
| :----------------------------------------- | :------------------------------------------------------------------------------------------------- | :--------------------------------- |
| **Skip file** — *continue queue* (default) | Processing of this file stops. No output file is written for it. Its status becomes **Skipped**.   | The next files are processed.      |
| **Stop all** — *halt on first error*       | Processing of this file stops. No output file is written for it. Its status becomes **Error**.     | The whole run ends. Files not yet processed are marked **Skipped**. |
| **Ignore** — *write partial*               | The failing step is left out: the data passes through it unchanged. The following steps still run and the output file is written. | The next files are processed.      |

With **Ignore**, the output is *partial*: it lacks the effect of every step that failed. Check the **Console** before you use such a file.

## Errors outside the steps

Some errors happen before the first step or after the last one: the source file cannot be read (missing, locked by Excel, unreadable format), or the output file cannot be written. No output can be produced in that case, whatever the choice:

- the file's status becomes **Error**;
- with **Skip file** and **Ignore**, the next files are still processed;
- with **Stop all**, the whole run ends.

## Where errors appear

- The **Console** at the bottom of the **Processing** page shows each error message, and **Errors** counts them. **Warnings** counts messages such as *Skipping file due to error in '…'*.
- Each file in the queue shows its own status: **Pending**, **Running**, **Done**, **Error** or **Skipped**.
- The application log keeps a trace of each run. See [Data locations](../reference/data-locations.md#logs).

## Stopping a run yourself

The stop button (the square next to **Run preset**) asks the run to stop. Flash-Excel finishes the step in progress, then stops: the current file is not written, and the files after it are not processed. The **Console** shows *Run stopped by user.* See [Stop a run](../tasks/run/stop-a-run.md).

## Runs outside the window

Launchers, scheduled tasks and the command line have no **On error** choice. They always behave like **Skip file**: a file that fails at any point gets no output, and the next files are still processed. The run then ends with exit code `1` instead of `0`. See [Command line](../reference/command-line.md#exit-codes).

## ➡️ Next steps

- [Run a preset](../tasks/run/run-a-preset.md)
- [Troubleshooting](../troubleshooting.md)
