# Paramètres

Ouvrez les paramètres avec **Paramètres** dans la barre latérale. Les changements de thème, de langue et de sortie CSV s'appliquent et sont enregistrés dès que vous les sélectionnez. Une source de préréglages en lecture seule n'est enregistrée qu'après avoir sélectionné **Enregistrer** dans sa fenêtre. Fermez la fenêtre avec **×** ou **Échap**.

Les paramètres sont stockés dans `app.config.yaml`, dans `%APPDATA%\flash-excel`. Vous pouvez aussi modifier ce fichier à la main : les changements sont lus au démarrage suivant. Consultez [Emplacements des données](data-locations.md).

## Apparence {#appearance}

| Paramètre (dans l'application) | Valeurs                                  | Par défaut | Clé `app.config.yaml` | Valeurs du fichier                      |
| :----------------------------- | :--------------------------------------- | :--------- | :-------------------- | :-------------------------------------- |
| **Palette de couleurs**        | **Blue Gray**, **GitHub**, **Warm Dark** | Blue Gray  | `appearance.palette`  | `blue-gray`, `github-dark`, `warm-dark` |
| **Mode**                       | **Sombre**, **Clair**                    | Sombre     | `appearance.mode`     | `dark`, `light`                         |

Chaque palette a une variante sombre et une variante claire. Les cartes de palette prévisualisent les couleurs du mode sélectionné.

Les palettes elles-mêmes sont définies dans `theme.config.yaml`, à côté de `app.config.yaml`. Une nouvelle version de Flash-Excel qui modifie les palettes remplace ce fichier et garde votre copie précédente sous le nom `theme.config.yaml.bak`. Si `app.config.yaml` nomme une palette qui n'existe pas, Flash-Excel utilise Blue Gray.

## Langue {#language}

| Paramètre (dans l'application) | Valeurs                   | Par défaut                                              | Clé `app.config.yaml` | Valeurs du fichier |
| :----------------------------- | :------------------------ | :------------------------------------------------------ | :-------------------- | :----------------- |
| **Langue**                     | **Anglais**, **Français** | La langue choisie dans l'installateur ; sinon l'anglais | `locale`              | `en`, `fr`         |

La langue s'applique à toute l'interface. Elle détermine aussi les libellés vrai/faux écrits dans les fichiers Excel produits : `True`/`False` en anglais, `VRAI`/`FAUX` en français.

Les noms de fonctions des colonnes calculées restent en français quelle que soit la langue. Consultez [Fonctions des colonnes calculées](computed-functions.md).

## Sortie CSV {#csv-output}

Ces réglages s'appliquent aux fichiers CSV que Flash-Excel **écrit**, depuis la fenêtre, les lanceurs, les tâches planifiées et la ligne de commande. Ils ne changent pas la lecture des fichiers sources CSV : celle-ci se règle par préréglage (consultez [Fichier de préréglage](preset-file.md)).

| Paramètre (dans l'application) | Valeurs                                                      | Par défaut | Clé `app.config.yaml` | Valeurs du fichier                  |
| :----------------------------- | :----------------------------------------------------------- | :--------- | :-------------------- | :---------------------------------- |
| **Séparateur de colonnes**     | **Auto**, **Point-virgule ;**, **Virgule ,**, **Tabulation** | Auto       | `csv.separator`       | `auto`, `semicolon`, `comma`, `tab` |
| **Séparateur décimal**         | **Auto**, **Virgule 1,5**, **Point 1.5**                     | Auto       | `csv.decimal`         | `auto`, `comma`, `dot`              |

- **Auto** suit vos paramètres régionaux Windows (le séparateur de liste et le symbole décimal) — ceux qu'Excel lit aussi, donc le fichier s'ouvre en colonnes au double-clic. Sur un Windows français, cela donne en général `;` et `1,5` ; sur un Windows anglais (États-Unis), `,` et `1.5`.
- Une virgule ne peut pas être à la fois le séparateur et le séparateur décimal. Quand le séparateur vaut une virgule, les décimales sont toujours écrites avec un point.
- Dans `app.config.yaml`, une valeur inconnue est traitée comme `auto`.

Consultez [Régler le format de sortie CSV](../tasks/settings/set-the-csv-output-format.md).

## Sources de préréglages en lecture seule {#read-only-preset-sources}

Des dossiers partagés dont les préréglages apparaissent à côté des vôtres. Flash-Excel ne fait que les lire. Consultez [Utiliser des dossiers de préréglages partagés](../tasks/presets/use-shared-preset-folders.md).

| Champ (dans l'application) | Description                                                            | Clé `app.config.yaml`     |
| :------------------------- | :--------------------------------------------------------------------- | :------------------------ |
| **Libellé**                | Nom affiché avec les préréglages de ce dossier, par exemple `Finance`. | `presets.sources[].label` |
| **Chemin du dossier**      | Le dossier qui contient les préréglages `.toml`.                       | `presets.sources[].path`  |

Les deux champs sont obligatoires. Seuls les fichiers `.toml` placés directement dans le dossier sont listés, pas ceux des sous-dossiers. Sélectionner **Supprimer la source**, puis **Supprimer**, retire le dossier de la liste ; *le dossier et ses préréglages ne seront pas supprimés*.

## Exemple de `app.config.yaml` {#example-appconfigyaml}

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
    path: \\serveur\partage\flash-excel\presets
```

## Réglages absents de cette fenêtre {#settings-that-are-not-in-this-window}

Le format de sortie, le dossier de destination, le modèle de nom et le choix en cas d'erreur se règlent à chaque exécution sur la page **Traitement**, sous **Sortie** et **En cas d'erreur**. Ils ne sont pas conservés d'une session à l'autre. Consultez [Lancer un préréglage](../tasks/run/run-a-preset.md).
