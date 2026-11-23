# Formats de fichier

## Fichiers sources (lecture) {#source-files-read}

| Format               | Extensions               | Ce qui est lu                                                                     |
| :------------------- | :----------------------- | :-------------------------------------------------------------------------------- |
| Classeur Excel       | `.xlsx`, `.xlsm`, `.xls` | La **première feuille** uniquement. Sa première ligne donne les noms de colonnes. |
| CSV (texte délimité) | `.csv`                   | Tout le fichier. Sa première ligne donne les noms de colonnes.                    |

Les sélecteurs de fichiers et la zone de dépôt n'acceptent que ces quatre extensions. Un autre fichier est refusé avec *Unsupported file format. Allowed: .xlsx, .xls, .xlsm, .csv*.

### Fichiers Excel {#excel-files}

- Seule la première feuille du classeur est lue ; les autres feuilles sont ignorées. Pour traiter une autre feuille, placez-la en première position dans Excel et enregistrez.
- Les cellules contenant des formules sont lues avec leur dernière valeur calculée.
- La mise en forme (couleurs, polices, largeurs de colonnes, cellules fusionnées) n'est pas lue.
- Le classeur ne doit pas être verrouillé par un autre programme pendant la lecture. Si Excel le garde ouvert, le fichier échoue ; fermez-le dans Excel et relancez.

### Fichiers CSV {#csv-files}

| Aspect             | Comportement                                                                                                                                                                        | Option du préréglage                |
| :----------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------- |
| Séparateur         | Détecté au début du fichier parmi `;`, `,`, tabulation et <code>&#124;</code>. Si la détection n'est pas concluante, `;` est utilisé.                                               | `csv_separator` en impose un.       |
| Encodage           | UTF-8. Les octets qui ne sont pas de l'UTF-8 valide (par exemple des lettres accentuées enregistrées en Windows-1252) deviennent `�`.                                               | `csv_encoding`, par ex. `"cp1252"`. |
| Séparateur décimal | Point : `1.5` est un nombre, `1,5` reste du texte.                                                                                                                                  | `csv_decimal_comma = true`.         |
| Types de colonnes  | Déduits de toutes les lignes du fichier : une colonne n'est numérique que si toutes ses valeurs sont des nombres. Les dates restent du texte tant que vous ne les convertissez pas. | —                                   |
| Champs vides       | Lus comme des cellules vides, que **Remplir les cellules vides** peut remplir.                                                                                                      | —                                   |

Les options du préréglage sont décrites dans [Fichier de préréglage](preset-file.md#the-meta-table). En ligne de commande, un fichier source dont l'extension n'est pas une extension Excel est lu comme un CSV.

!!! tip "Fichiers CSV enregistrés par un Excel français"
    Un CSV enregistré par Excel en français utilise en général `;` comme séparateur, la virgule décimale et l'encodage Windows-1252. Le séparateur est détecté automatiquement ; pour le reste, ajoutez `csv_decimal_comma = true` et `csv_encoding = "cp1252"` au préréglage.

!!! note "Types de colonnes dans l'éditeur"
    Pour que l'éditeur reste rapide, les types de colonnes qu'il affiche pour un modèle CSV sont déduits des 300 premières lignes. Une exécution lit toutes les lignes : une colonne qui passe de nombres à du texte plus bas est donc du texte à l'exécution, même si l'éditeur l'affichait comme un nombre.

## Fichiers de sortie (écriture) {#output-files-write}

Sur la page **Traitement**, **Format** propose quatre choix ; en ligne de commande, `--format` prend la valeur correspondante.

| Format (dans l'application) | `--format` | Extension écrite        | Remarques                                                                                                                                                                                       |
| :-------------------------- | :--------- | :---------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Même que la source**      | `keep`     | Celle du fichier source | Ne fonctionne que pour les sources `.xlsx` et `.csv`. Voir l'avertissement ci-dessous.                                                                                                          |
| **.xlsx (Excel)**           | `xlsx`     | `.xlsx`                 | Une feuille. Dates au format `JJ/MM/AAAA`, dates et heures au format `JJ/MM/AAAA HH:MM:SS`. Valeurs vrai/faux écrites en texte dans la langue de l'interface : `True`/`False` ou `VRAI`/`FAUX`. |
| **.csv (UTF-8)**            | `csv`      | `.csv`                  | Texte UTF-8 avec une ligne d'en-tête. Séparateur et séparateur décimal tirés de **Paramètres** › **Sortie CSV**.                                                                                |
| **.parquet**                | `parquet`  | `.parquet`              | Fichier de données en colonnes pour les outils de données (Power BI, Python, bases de données). Conserve exactement les types de colonnes.                                                      |

!!! warning "**Même que la source** avec des fichiers `.xls` et `.xlsm`"
    Flash-Excel ne sait pas écrire l'ancien format `.xls`, ni les classeurs `.xlsm` avec macros. Avec **Même que la source**, un tel fichier source échoue avec *Unsupported format: 'xls'* (ou `'xlsm'`) une fois toutes les étapes exécutées. Choisissez **.xlsx (Excel)** pour ces fichiers.

### Nom et emplacement {#name-and-location}

- La sortie est écrite dans le **Dossier de destination** (par défaut `Documents\flash-excel\output`). Un dossier relatif est placé dans ce dossier par défaut.
- Son nom suit le **Modèle de nom** (par défaut `{name}_clean`), où `{name}` est le nom du fichier source sans son extension : `ventes.xlsx` donne `ventes_clean.xlsx`.
- Un fichier existant de même nom est remplacé sans avertissement. Choisissez un modèle différent de `{name}` si la sortie va dans le dossier source, pour ne pas écraser le fichier source.
- Le fichier source lui-même n'est jamais modifié par ailleurs.

La mise en forme, les formules, les autres feuilles et les macros de la source ne sont pas reprises dans la sortie : la sortie ne contient que des valeurs.

Consultez aussi [Emplacements des données](data-locations.md) et [Régler le format de sortie CSV](../tasks/settings/set-the-csv-output-format.md).
