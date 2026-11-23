# Créer un préréglage

Créez un préréglage quand vous avez un nouveau type de fichier à transformer. Un préréglage contient les étapes à appliquer et mémorise les colonnes d'un fichier modèle, ce qui permet de le modifier plus tard sans ce fichier.

## 🔧 Prérequis

- Un fichier modèle : un fichier Excel ou CSV ayant les mêmes colonnes que les fichiers que vous traiterez (`.xlsx`, `.xls`, `.xlsm` ou `.csv`).

## 📝 Étapes

1. Dans la barre latérale, sélectionnez **Préréglages**.
2. À côté de **Préréglages**, sélectionnez le bouton **+** (**Nouveau préréglage**). Un nouveau préréglage nommé `Preset 1` (ou le numéro libre suivant) s'ouvre dans l'éditeur.
3. Dans le champ de nom de la barre d'outils, remplacez le nom par défaut par le vôtre.
4. Sous **Charger le modèle Excel**, sélectionnez **Charger un fichier** et choisissez votre fichier modèle.
5. Sous **Configuration des actions**, ajoutez au moins une étape. Consultez [Ajouter des étapes à un préréglage](add-steps-to-a-preset.md).
6. Sélectionnez **Enregistrer**.

## ✅ Résultat

Le message **Préréglage enregistré** apparaît, et le préréglage figure dans la liste à gauche avec le libellé **Local** et son nombre d'étapes. Il est aussi proposé dans la liste **Preset** de la page **Traitement**.

Le préréglage est enregistré sous forme de fichier `.toml` dans `Documents\flash-excel\presets`. Le nom du fichier vient du nom du préréglage : `Monthly report` devient `monthly_report.toml`.

!!! warning "Un nouveau préréglage n'est enregistré qu'avec Enregistrer"
    Jusque-là, il n'existe que dans l'éditeur et n'apparaît pas dans la liste.

!!! note "Renommer un préréglage"
    Pour renommer un préréglage, sélectionnez-le, changez son nom et sélectionnez **Enregistrer** : son fichier est renommé lui aussi. Si un autre préréglage utilise déjà le même nom de fichier, Flash-Excel refuse l'enregistrement et vous demande de choisir un autre nom.

## ➡️ Étapes suivantes

- [Ajouter des étapes à un préréglage](add-steps-to-a-preset.md)
- [Prévisualiser une transformation](../run/preview-a-transformation.md)
- [Préréglages](../../concepts/presets.md) — ce que contient un préréglage.
- [Fichier de préréglage](../../reference/preset-file.md) — le format du fichier `.toml`.
