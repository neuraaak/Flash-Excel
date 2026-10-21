# Settings

Open the settings with **Settings** in the sidebar. Theme, language and CSV changes apply and are saved as soon as you select them. A read-only preset source is saved only when you select **Save** in its dialog. Close the window with **×** or **Esc**.

The settings are stored in `app.config.yaml`, in `%APPDATA%\flash-excel`. You can also edit that file by hand: changes are read on the next start. See [Data locations](data-locations.md).

## Appearance

| Setting (in the app) | Values                                   | Default     | `app.config.yaml` key | File values                                |
| :------------------- | :--------------------------------------- | :---------- | :-------------------- | :----------------------------------------- |
| **Color palette**    | **Blue Gray**, **GitHub**, **Warm Dark** | Blue Gray   | `appearance.palette`  | `blue-gray`, `github-dark`, `warm-dark`    |
| **Mode**             | **Dark**, **Light**                      | Dark        | `appearance.mode`     | `dark`, `light`                            |

Each palette has a dark and a light variant. The palette cards preview the colours of the selected mode.

The palettes themselves are defined in `theme.config.yaml`, next to `app.config.yaml`. A new version of Flash-Excel that changes the palettes replaces this file and keeps your previous copy as `theme.config.yaml.bak`. If `app.config.yaml` names a palette that does not exist, Flash-Excel uses Blue Gray.

## Language

| Setting (in the app) | Values                  | Default                          | `app.config.yaml` key | File values  |
| :------------------- | :---------------------- | :------------------------------- | :-------------------- | :----------- |
| **Language**         | **English**, **French** | The language chosen in the installer; English otherwise | `locale` | `en`, `fr` |

The language applies to the whole interface. It also sets the true/false labels written in Excel output files: `True`/`False` in English, `VRAI`/`FAUX` in French.

Function names of computed columns stay in French whatever the language. See [Computed column functions](computed-functions.md).

## CSV output

These settings apply to the CSV files Flash-Excel **writes**, from the window, launchers, scheduled tasks and the command line. They do not change how CSV source files are read: that is set per preset (see [Preset file format](preset-file.md)).

| Setting (in the app)  | Values                                             | Default | `app.config.yaml` key | File values                          |
| :-------------------- | :------------------------------------------------- | :------ | :-------------------- | :----------------------------------- |
| **Column separator**  | **Auto**, **Semicolon ;**, **Comma ,**, **Tab**    | Auto    | `csv.separator`       | `auto`, `semicolon`, `comma`, `tab`  |
| **Decimal mark**      | **Auto**, **Comma 1,5**, **Dot 1.5**               | Auto    | `csv.decimal`         | `auto`, `comma`, `dot`               |

- **Auto** follows your Windows regional settings (the list separator and the decimal symbol) — the same ones Excel reads, so the file opens in columns on a double-click. On a French Windows, that usually means `;` and `1,5`; on an English (US) Windows, `,` and `1.5`.
- A comma cannot be both the separator and the decimal mark. When the separator resolves to a comma, decimals are always written with a dot.
- In `app.config.yaml`, an unknown value is treated as `auto`.

See [Set the CSV output format](../tasks/settings/set-the-csv-output-format.md).

## Read-only preset sources

Shared folders whose presets appear next to your local ones. Flash-Excel only reads them. See [Use shared preset folders](../tasks/presets/use-shared-preset-folders.md).

| Field (in the app) | Description                                                  | `app.config.yaml` key       |
| :----------------- | :----------------------------------------------------------- | :-------------------------- |
| **Label**          | Name shown with the presets from this folder, e.g. `Finance`. | `presets.sources[].label`   |
| **Folder path**    | The folder that contains the `.toml` presets.                | `presets.sources[].path`    |

Both fields are required. Only the `.toml` files directly in the folder are listed, not those in sub-folders. Selecting **Remove source**, then **Delete**, removes the folder from the list; *the folder and its presets will not be deleted*.

## Example `app.config.yaml`

```yaml
appearance:
  palette: "github-dark"
  mode: "light"

locale: "fr"

csv:
  separator: "semicolon"
  decimal: "comma"

presets:
  sources:
  - label: Finance
    path: \\server\share\flash-excel\presets
```

## Settings that are not in this window

The output format, destination folder, naming pattern and error choice are set for each run on the **Processing** page, under **Output** and **On error**. They are not saved between sessions. See [Run a preset](../tasks/run/run-a-preset.md).
