# Lancer en ligne de commande

Lancez un préréglage sur un ou plusieurs fichiers depuis une invite de commandes ou un script, sans ouvrir la fenêtre de Flash-Excel. C'est ce que font en coulisse les tâches planifiées et les lanceurs, et vous pouvez l'utiliser dans vos propres fichiers batch.

## 🔧 Prérequis

- Flash-Excel installé. Consultez la [prise en main](../../get-started.md).
- Le chemin de l'exécutable Flash-Excel. Pour le trouver, ouvrez **Configurer une exécution** sur la page **Traitement** : la fenêtre affiche **Utilise l'application installée :** suivi du chemin.
- Un fichier de préréglage. Vos préréglages se trouvent dans `Documents\flash-excel\presets`, un fichier `.toml` par préréglage.

## 📝 Étapes

1. Ouvrez une invite de commandes ou une fenêtre PowerShell.
2. Lancez l'exécutable Flash-Excel avec `--preset` et `--input`. Remplacez les chemins par les vôtres :

    === "Invite de commandes"

        ```bat
        "<chemin vers>\Flash-Excel.exe" --preset "%USERPROFILE%\Documents\flash-excel\presets\monthly_report.toml" --input "C:\Data\janvier.xlsx" "C:\Data\fevrier.xlsx" --output "C:\Data\clean"
        ```

    === "PowerShell"

        ```powershell
        & "<chemin vers>\Flash-Excel.exe" --preset "$HOME\Documents\flash-excel\presets\monthly_report.toml" --input "C:\Data\janvier.xlsx" "C:\Data\fevrier.xlsx" --output "C:\Data\clean"
        ```

3. Ajoutez des options si besoin :

    | Option               | Effet                                                                            | Par défaut                     |
    | :------------------- | :------------------------------------------------------------------------------- | :----------------------------- |
    | `--output <dossier>` | Dossier de destination. Un dossier relatif est créé dans le dossier par défaut.  | `Documents\flash-excel\output` |
    | `--format <format>`  | `keep` (même que la source), `xlsx`, `csv` ou `parquet`.                         | `keep`                         |
    | `--pattern <texte>`  | Nom du fichier de sortie sans extension ; `{name}` est le nom du fichier source. | `{name}_clean`                 |
    | `--debug`            | Écrit plus de détails dans le fichier journal.                                   | Désactivé                      |

## ✅ Résultat

Chaque fichier est traité séparément, et la fenêtre affiche une ligne par fichier (ces messages sont toujours en anglais) :

```text
janvier.xlsx -> C:\Data\clean\janvier_clean.xlsx (1250 rows)
fevrier.xlsx FAILED: <raison>
```

Un fichier en échec n'arrête pas les autres. À la fin de la commande, son code de sortie indique à un script ce qui s'est passé :

| Code de sortie | Signification                                          |
| :------------: | :----------------------------------------------------- |
|      `0`       | Tous les fichiers ont réussi.                          |
|      `1`       | Au moins un fichier a échoué.                          |
|      `2`       | Les arguments de la ligne de commande sont incorrects. |

Les mêmes lignes sont écrites dans le fichier journal de Flash-Excel. Consultez [Emplacements des données](../../reference/data-locations.md).

!!! warning "Attendre la fin de l'exécution dans une invite interactive"
    Flash-Excel est une application fenêtrée. Saisie directement dans une invite de commandes interactive, la commande peut rendre la main avant la fin de l'exécution, avec les lignes de résultat affichées après coup, et `%ERRORLEVEL%` n'est alors pas le code de sortie de l'exécution. Pour attendre la fin et lire le code de sortie, lancez la commande depuis un fichier batch (`.cmd`), comme le font les lanceurs.

!!! note "Mêmes réglages que l'application"
    Une exécution en ligne de commande utilise les réglages de sortie CSV choisis dans **Paramètres** › **Sortie CSV**. Consultez [Régler le format de sortie CSV](../settings/set-the-csv-output-format.md).

!!! tip "Laisser Flash-Excel écrire la commande"
    [Planifier un préréglage](schedule-a-preset.md) et [Créer un lanceur](create-a-launcher.md) construisent cette commande pour vous depuis la page **Traitement**.

## ➡️ Étapes suivantes

- [Ligne de commande](../../reference/command-line.md) — la référence complète des options.
- [Planifier un préréglage](schedule-a-preset.md)
