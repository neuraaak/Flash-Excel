# Préréglages

Un **préréglage** est une liste enregistrée de transformations. Vous le construisez une fois sur la page **Préréglages**, puis vous l'appliquez à autant de fichiers que vous voulez depuis la page **Traitement**, un lanceur, une tâche planifiée ou la ligne de commande. Le fichier source n'est jamais modifié : chaque exécution écrit un nouveau fichier de sortie.

!!! note "Préréglage ou preset"
    L'interface emploie les deux mots : **Préréglages** dans la barre latérale et l'éditeur, **Preset** sur la page **Traitement**. Ils désignent la même chose.

## Ce que contient un préréglage

Un préréglage est un petit fichier texte au format TOML, d'extension `.toml`. Il contient deux parties :

- **Les métadonnées** — le nom du préréglage, une description facultative et les options de lecture des fichiers CSV (séparateur, encodage, séparateur décimal).
- **Les étapes** — la liste ordonnée des transformations : renommer des colonnes, filtrer des lignes, ajouter une colonne calculée, etc. Flash-Excel propose 12 types d'étapes. Consultez [Étapes et ordre](steps-and-order.md).

Le préréglage mémorise aussi les colonnes, et leurs types, du fichier chargé sous **Charger le modèle Excel**. C'est pourquoi vous pouvez rouvrir un préréglage et modifier ses étapes sans recharger le fichier : l'éditeur affiche **Fichier modèle · peut ne plus exister sur cette machine** et continue de proposer les colonnes mémorisées.

Le format complet du fichier est décrit dans [Fichier de préréglage](../reference/preset-file.md).

## Où sont stockés les préréglages

Les préréglages que vous créez sont enregistrés dans votre dossier **Documents**, sous `Documents\flash-excel\presets`. Le nom du fichier vient du nom du préréglage : en minuscules, sans ponctuation, espaces remplacées par des tirets bas. `Rapport RH mensuel` est enregistré sous `rapport_rh_mensuel.toml`.

Comme ils se trouvent dans **Documents**, les préréglages survivent aux mises à jour et à la désinstallation, et vous pouvez les sauvegarder, les copier ou les envoyer comme n'importe quel document. Consultez [Emplacements des données](../reference/data-locations.md).

## Préréglages locaux et partagés

Flash-Excel liste des préréglages venant de deux types d'emplacements :

| Type        | D'où il vient                                                                                        | Ce que vous pouvez faire                                                   |
| :---------- | :--------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------- |
| **Local**   | `Documents\flash-excel\presets`                                                                      | Modifier, enregistrer, supprimer, exporter, lancer.                        |
| **Partagé** | Un dossier ajouté sous **Paramètres** › **Sources de préréglages en lecture seule**, avec un libellé | Lancer et prévisualiser. **Enregistrer** et **Supprimer** sont désactivés. |

Les dossiers partagés permettent à une équipe d'utiliser les mêmes préréglages, par exemple depuis un lecteur réseau. Flash-Excel n'y écrit jamais : *Les dossiers partagés sont en lecture seule dans Flash-Excel.* Pour modifier un préréglage partagé, éditez le fichier dans le dossier partagé lui-même, ou demandez-le à la personne qui le maintient. Si un dossier partagé est inaccessible, ses préréglages ne sont tout simplement pas listés. Consultez [Utiliser des dossiers de préréglages partagés](../tasks/presets/use-shared-preset-folders.md).

## C'est le préréglage enregistré qui s'exécute

**Lancer le preset** et **Aperçu** lisent le fichier de préréglage tel qu'il est enregistré sur le disque. Les modifications faites dans l'éditeur ne s'appliquent qu'après avoir sélectionné **Enregistrer** sur la page **Préréglages**.

Un fichier de préréglage que Flash-Excel ne sait pas lire apparaît quand même dans la liste, marqué **illisible**, pour qu'un fichier endommagé ne ressemble pas à un fichier supprimé. Survolez la mention pour voir la raison. Consultez [Dépannage](../troubleshooting.md#a-preset-is-marked-unreadable).

!!! warning "Modifier un fichier de préréglage à la main"
    Vous pouvez écrire ou modifier un fichier de préréglage dans un éditeur de texte. Gardez à l'esprit que réenregistrer ce préréglage depuis la page **Préréglages** réécrit ses métadonnées : la description et les options de lecture CSV (`csv_separator`, `csv_encoding`, `csv_decimal_comma`) reviennent à leurs valeurs par défaut. L'éditeur ne garde aussi qu'une étape de chaque type, dans son propre ordre fixe. Consultez [Étapes et ordre](steps-and-order.md#presets-written-by-hand).

## ➡️ Étapes suivantes

- [Créer un préréglage](../tasks/presets/create-a-preset.md)
- [Exporter un préréglage](../tasks/presets/export-a-preset.md)
- [Utiliser des dossiers de préréglages partagés](../tasks/presets/use-shared-preset-folders.md)
