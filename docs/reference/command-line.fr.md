# Ligne de commande

Flash-Excel peut appliquer un préréglage sans ouvrir sa fenêtre. C'est ce qu'utilisent les lanceurs et les tâches planifiées, et vous pouvez l'appeler vous-même depuis une invite de commandes, un fichier batch ou un autre outil. Pour un guide pas à pas, consultez [Lancer en ligne de commande](../tasks/automate/run-from-the-command-line.md).

## Syntaxe {#syntax}

```bat
Flash-Excel.exe --preset <preset.toml> --input <fichier> [<fichier> …] [--output <dossier>] [--format keep|xlsx|csv|parquet] [--pattern <modèle>] [--debug]
```

`Flash-Excel.exe` est le programme du dossier d'installation de Flash-Excel. Le chemin exact sur votre PC est affiché dans la fenêtre **Planifier ou créer un lanceur**, après *Utilise l'application installée :*. Utilisez le chemin complet, entre guillemets, quand vous l'appelez depuis un autre dossier.

Il n'y a qu'un seul programme : avec `--preset`, il s'exécute sans fenêtre ; sans `--preset`, il ouvre la fenêtre comme d'habitude.

## Options {#options}

| Option               | Obligatoire | Par défaut                     | Description                                                                                                                                                             |
| :------------------- | :---------: | :----------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--preset <chemin>`  |     Oui     | —                              | Le fichier de préréglage `.toml` à appliquer. N'importe quel fichier de préréglage convient : local, partagé ou ailleurs.                                               |
| `--input <chemin> …` |     Oui     | —                              | Un ou plusieurs fichiers sources, séparés par des espaces. Chaque fichier est traité séparément.                                                                        |
| `--output <dossier>` |     Non     | `Documents\flash-excel\output` | Dossier de destination, créé si besoin. Un dossier relatif est placé dans `Documents\flash-excel\output`.                                                               |
| `--format <format>`  |     Non     | `keep`                         | Format de sortie : `keep` (même que le fichier source), `xlsx`, `csv` ou `parquet`.                                                                                     |
| `--pattern <texte>`  |     Non     | `{name}_clean`                 | Nom de chaque fichier de sortie, sans extension. `{name}` est remplacé par le nom du fichier source sans son extension.                                                 |
| `--debug`            |     Non     | désactivé                      | Écrit des messages détaillés dans le fichier journal.                                                                                                                   |
| `-h`, `--help`       |     Non     | —                              | Affiche la liste des options (en anglais). Doit être combiné avec `--preset` pour atteindre le mode ligne de commande, par exemple `Flash-Excel.exe --preset x --help`. |

Les chemins qui contiennent des espaces doivent être entre guillemets doubles.

### Noms des fichiers de sortie {#output-file-names}

Avec les valeurs par défaut, `C:\Data\ventes.xlsx` donne `Documents\flash-excel\output\ventes_clean.xlsx`. Un fichier existant de même nom est remplacé.

`keep` reprend l'extension du fichier source. Cela fonctionne pour les sources `.xlsx` et `.csv`. Pour les sources `.xls` et `.xlsm`, Flash-Excel ne sait pas écrire ce format et le fichier échoue avec *Unsupported format: 'xls'* : passez `--format xlsx`. Consultez [Formats de fichier](file-formats.md).

### Paramètres repris de l'application {#settings-used-from-the-app}

Une exécution en ligne de commande utilise les paramètres enregistrés dans l'application :

- les réglages **Sortie CSV** (**Séparateur de colonnes** et **Séparateur décimal**) pour les fichiers CSV produits ;
- la **Langue**, pour les libellés vrai/faux des fichiers Excel produits (`True`/`False` en anglais, `VRAI`/`FAUX` en français).

Les options `[meta]` du préréglage lui-même décident de la lecture des fichiers sources CSV. Consultez [Paramètres](settings.md) et [Fichier de préréglage](preset-file.md).

## Comportement {#behaviour}

- Les fichiers sont traités l'un après l'autre, dans l'ordre indiqué.
- Un fichier qui échoue — illisible, verrouillé par Excel, erreur d'étape, sortie impossible à écrire — n'a pas de fichier de sortie. **Les fichiers suivants sont quand même traités.** Il n'y a pas d'équivalent au choix **En cas d'erreur** de la fenêtre.
- Si le préréglage lui-même ne peut pas être chargé, rien n'est traité.

### Messages {#messages}

Pour chaque fichier, une ligne (en anglais) est affichée et écrite dans le [fichier journal](data-locations.md#logs) :

```text
ventes.xlsx -> C:\Users\moi\Documents\flash-excel\output\ventes_clean.xlsx (1250 rows)
mars.csv FAILED: No such file or directory (os error 2): ...
```

Les fichiers réussis sont signalés sur la sortie standard, les fichiers en échec sur la sortie d'erreur.

### Console {#console}

Flash-Excel est un programme fenêtré. Quand vous le lancez depuis une invite de commandes ou PowerShell, il écrit ses messages dans cette console. Quand rien ne l'a lancé depuis une console — une tâche planifiée, un double-clic — il n'y a pas de console et les messages vont seulement dans le fichier journal. Le code de sortie est défini dans tous les cas.

!!! tip "Attendre la fin de l'exécution"
    Un fichier batch (`.cmd` ou `.bat`) attend chaque programme qu'il lance, et peut donc lire le code de sortie dans `%ERRORLEVEL%`. C'est ainsi que fonctionnent les lanceurs créés par Flash-Excel. Dans une invite interactive, Windows peut rendre la main avant la fin d'un programme fenêtré : lancez la commande depuis un fichier batch quand vous avez besoin du code de sortie.

## Codes de sortie {#exit-codes}

| Code  | Signification                                                                                                            |
| :---: | :----------------------------------------------------------------------------------------------------------------------- |
|  `0`  | Chaque fichier source a été traité et écrit.                                                                             |
|  `1`  | Au moins un fichier source a échoué, ou le préréglage n'a pas pu être chargé (fichier introuvable, préréglage invalide). |
|  `2`  | Ligne de commande invalide : option obligatoire manquante, option inconnue, ou `--format` avec une autre valeur.         |

## Exemples {#examples}

Appliquer un préréglage à un fichier, avec le dossier et le format de sortie par défaut :

```bat
Flash-Excel.exe --preset "%USERPROFILE%\Documents\flash-excel\presets\rapport_rh_mensuel.toml" --input "C:\Exports\rh.xlsx"
```

Traiter trois fichiers en CSV dans un dossier choisi :

```bat
Flash-Excel.exe --preset nettoyage.toml --input jan.xlsx fev.xlsx mars.xlsx --output "D:\Rapports\T1" --format csv
```

Nommer les sorties d'après le mois et convertir des sources `.xls` en `.xlsx` :

```bat
Flash-Excel.exe --preset nettoyage.toml --input "C:\Exports\rapport.xls" --format xlsx --pattern "{name}_2026-10"
```

Utiliser le code de sortie dans un fichier batch :

```bat
@echo off
"C:\chemin\vers\Flash-Excel.exe" --preset nettoyage.toml --input a.xlsx b.xlsx
if errorlevel 1 echo Au moins un fichier a echoue. Consultez le fichier journal.
```

## Voir aussi {#related}

- [Lancer en ligne de commande](../tasks/automate/run-from-the-command-line.md)
- [Planifier un préréglage](../tasks/automate/schedule-a-preset.md) et [Créer un lanceur](../tasks/automate/create-a-launcher.md) — tous deux appellent cette ligne de commande pour vous.
