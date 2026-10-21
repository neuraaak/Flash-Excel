# Schedule a preset

Run a preset on the same files every day at a set time, without opening Flash-Excel. Flash-Excel creates the task for you in the Windows Task Scheduler.

## 🔧 Prerequisites

- On the **Processing** page, the files to process are loaded and the preset is selected. See [Load source files](../files/load-source-files.md) and [Run a preset](../run/run-a-preset.md).
- The preset and the source files stay where they are: the task uses their current paths.

## 📝 Steps

1. On the **Processing** page, under **Scheduled and manual execution**, select **Configure execution**. The **Schedule or create a launcher** window opens.
2. Check the settings:
    - **Execution name**: the name of the task. It defaults to `flash-excel` followed by the preset file name.
    - **Daily time (scheduled task)**: the time of the daily run. It defaults to `08:00`.
    - **Preset** and **Input files**: the preset and the files the task will process.
    - **Destination folder**, **Format** and **Naming pattern**: the output of the task. They start with the values of the **Processing** page; select **Choose an output folder** to pick another folder.
3. Select **Add to Task Scheduler**.
4. In the **Confirm scheduled task creation** window, read the summary and the warning, then select **Confirm creation**.

## ✅ Result

The message **Scheduled task “<name>” created.** appears. The task is in the Windows Task Scheduler, under **Task Scheduler Library** › **Flash-Excel**, and runs every day at the time you set.

- The task runs while your Windows session is open. Flash-Excel itself can be closed.
- If a file fails, the task goes on with the next file. The **On error** choice of the **Processing** page does not apply.
- Each run replaces the output files of the previous run when the names are the same.

!!! warning "You are responsible for the task"
    The task repeats every day until you disable or delete it. Check the files, the preset and the destination before you confirm.

## 🗑️ Disable or delete the task

1. Open the Windows Start menu, search for **Task Scheduler** and open it.
2. In the left pane, expand **Task Scheduler Library** and open the **Flash-Excel** folder.
3. Right-click the task, then choose **Disable** to pause future runs, or **Delete** and confirm to remove it.

Removing a task does not delete your files.

!!! note "Names and paths that are refused"
    The **Execution name** must have 1 to 200 characters, without `\ / : * ? " < > | % !`. The paths of the preset, the files and the destination folder cannot contain `%`, `!` or quotes.

!!! tip "Copy the command instead"
    **Advanced: copy the scheduling command** copies a `schtasks` command to the clipboard, to create the task yourself. Windows refuses this command when it is longer than 261 characters; use **Add to Task Scheduler** in that case.

## ➡️ Next steps

- [Create a launcher](create-a-launcher.md) to run the same configuration on demand.
- [Run from the command line](run-from-the-command-line.md) — what the task actually runs.
- [Troubleshooting](../../troubleshooting.md)
