# Lancer un préréglage

Appliquez un préréglage à un ou plusieurs fichiers sources et écrivez les fichiers transformés. Vous choisissez le format de sortie, le dossier de destination, les noms de fichiers et ce qui se passe quand un fichier échoue.

## 🔧 Prérequis

- Au moins un fichier source chargé sur la page **Traitement**. Consultez [Charger des fichiers sources](../files/load-source-files.md).
- Un préréglage enregistré.

## 📝 Étapes

1. Dans la barre latérale, sélectionnez **Traitement**.
2. Sous **Preset**, sélectionnez le préréglage. Chaque entrée affiche le nom du préréglage, sa source (**Local** ou le libellé d'un dossier partagé) et son nombre d'actions. Le cadre en dessous liste les actions du préréglage sélectionné.
3. Sous **Sortie**, réglez la sortie :

    | Champ                      | Ce qu'il faut saisir                                                                                             | Par défaut                     |
    | :------------------------- | :--------------------------------------------------------------------------------------------------------------- | :----------------------------- |
    | **Format**                 | **Même que la source**, **.xlsx (Excel)**, **.csv (UTF-8)** ou **.parquet**.                                     | **Même que la source**         |
    | **Dossier de destination** | Le dossier où les fichiers sont écrits. Saisissez un chemin, ou sélectionnez l'icône dossier pour en choisir un. | `Documents\flash-excel\output` |
    | **Modèle de nom**          | Le nom du fichier de sortie, sans extension. `{name}` représente le nom du fichier source.                       | `{name}_clean`                 |

4. Sous **En cas d'erreur**, choisissez ce qui se passe quand un fichier échoue :
    - **Passer le fichier** (continuer la file) : le fichier en échec n'est pas écrit et l'exécution continue avec le fichier suivant ;
    - **Tout arrêter** (stopper à la première erreur) : l'exécution s'arrête au premier fichier en échec ;
    - **Ignorer** (écrire partiellement) : l'étape en échec est sautée, les autres étapes s'appliquent quand même et le fichier est écrit.
5. Sélectionnez **Lancer le preset**.

## ✅ Résultat

Les fichiers sont traités l'un après l'autre. Chaque ligne affiche sa progression et son statut : **En attente**, **En cours**, **Terminé**, **Erreur** ou **Ignoré**. En bas du panneau, **Progression** couvre tout le lot, avec les compteurs **Lignes sorties**, **Erreurs**, **Avertissements** et **Durée**.

La **Console** journalise chaque étape avec ses nombres de lignes, puis une ligne du type `Terminé en 0.42s → <chemin de sortie>` pour chaque fichier écrit. Utilisez les filtres **All**, **Info**, **Step**, **Warn** et **Err** pour restreindre le journal.

Avec les réglages par défaut, `C:\Data\ventes.xlsx` donne `Documents\flash-excel\output\ventes_clean.xlsx`.

!!! warning "Les fichiers existants sont remplacés"
    Un fichier de même nom dans le dossier de destination est écrasé. Changez le **Modèle de nom** ou le **Dossier de destination** pour conserver les résultats précédents.

!!! note "Même que la source avec des fichiers .xls et .xlsm"
    **Même que la source** n'écrit que des fichiers `.xlsx` et `.csv`. Pour une source `.xls` ou `.xlsm`, choisissez **.xlsx (Excel)** comme **Format**, sinon le fichier échoue avec [Unsupported format: 'xls'](../../troubleshooting.md#unsupported-format-xls).

!!! tip "Dossier relatif"
    Un **Dossier de destination** relatif, comme `mensuel`, est créé dans `Documents\flash-excel\output`.

Si un fichier se termine par **Erreur**, lisez son message dans la **Console** et cherchez-le dans [Dépannage](../../troubleshooting.md) : une colonne manquante est traitée dans [Une étape ne trouve pas une colonne](../../troubleshooting.md#column-not-found), un fichier verrouillé dans [Permission denied](../../troubleshooting.md#file-in-use).

## ➡️ Étapes suivantes

- [Arrêter une exécution](stop-a-run.md)
- [Planifier un préréglage](../automate/schedule-a-preset.md) pour répéter cette exécution chaque jour.
- [Gestion des erreurs](../../concepts/error-handling.md) — les trois modes d'erreur en détail.
- [Régler le format de sortie CSV](../settings/set-the-csv-output-format.md)
