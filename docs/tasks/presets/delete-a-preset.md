# Delete a preset

Remove a preset you no longer need. Deleting a preset removes its file from your presets folder.

## 🔧 Prerequisites

- A preset of your own, listed with the label **Local**. Presets from a shared folder cannot be deleted from Flash-Excel.

## 📝 Steps

1. In the sidebar, select **Presets**.
2. Select the preset in the list on the left.
3. In the toolbar, select **Delete**.
4. In the **Delete preset** dialog, check the name after **Are you sure you want to delete**, then select **Delete**.

## ✅ Result

The message **Preset deleted** appears and the preset leaves the list. Its `.toml` file is deleted from `Documents\flash-excel\presets`.

!!! warning "This action cannot be undone"
    Flash-Excel keeps no copy of a deleted preset. [Export the preset](export-a-preset.md) first if you may need it again.

!!! note "Scheduled tasks and launchers"
    A scheduled task or a launcher that uses the deleted preset fails on its next run. Remove it too: see [Schedule a preset](../automate/schedule-a-preset.md).

## ➡️ Next steps

- [Create a preset](create-a-preset.md)
