# Use shared preset folders

Use presets stored in a shared folder, for example a team folder on a network drive, alongside your own presets. Flash-Excel reads these presets but never changes them.

## 🔧 Prerequisites

- A folder that contains preset files (`.toml`) and that you can open from your computer.

## 📝 Steps

1. In the sidebar, select **Settings**.
2. Under **Read-only preset sources**, select **Add source**.
3. In **Label**, type a short name that identifies the folder, for example `Finance`.
4. In **Folder path**, type the path of the folder, or select the folder icon (**Browse for a folder**) to pick it.
5. Select **Save**.

## ✅ Result

The folder is listed under **Read-only preset sources**. Its presets appear with the label you typed instead of **Local**: in the **Preset** list of the **Processing** page the next time you open that page, and on the **Presets** page after you restart Flash-Excel.

You can open, preview and run a shared preset like your own. **Save** and **Delete** are unavailable for it, because shared folders are read-only in Flash-Excel.

To change a source, select **Edit** next to it. To remove it from the list, select the **Remove source** icon, then **Delete** in the **Remove shared source?** dialog. The folder and its presets are not deleted.

!!! note "Folder not available"
    If a shared folder cannot be reached when Flash-Excel lists the presets, for example when the network drive is disconnected, its presets are simply not listed. They come back once the folder is reachable again.

## ➡️ Next steps

- [Export a preset](export-a-preset.md) to place one of your presets in a shared folder.
- [Settings](../../reference/settings.md) — every setting and where it is stored.
