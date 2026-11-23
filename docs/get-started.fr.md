# Prise en main de Flash-Excel

À la fin de cette page, vous aurez installé Flash-Excel, créé un préréglage avec une étape, vérifié son résultat dans un aperçu et écrit votre premier fichier transformé.

## 🔧 Prérequis

- Un PC Windows. Aucun droit administrateur n'est nécessaire : Flash-Excel s'installe pour votre seul utilisateur Windows.
- Un fichier Excel ou CSV à transformer (`.xlsx`, `.xls`, `.xlsm` ou `.csv`).

## 📝 Étapes

### Installer Flash-Excel

1. Ouvrez la [dernière version publiée](https://github.com/neuraaak/Flash-Excel/releases/latest) et téléchargez `Flash-Excel-<version>-setup.exe`.
2. Lancez l'installateur et choisissez la langue de l'assistant. Flash-Excel démarre dans la langue choisie ici ; vous pourrez la changer plus tard dans **Paramètres**.
3. Suivez l'assistant. Laissez cochée l'option de lancement sur la dernière page pour démarrer Flash-Excel aussitôt.

La fenêtre s'ouvre sur **Traitement**. La barre latérale à gauche donne accès à **Traitement**, **Préréglages** et **Paramètres**.

### Créer un préréglage avec une étape

Un préréglage est la liste des transformations à appliquer. Cet exemple renomme une colonne.

1. Dans la barre latérale, sélectionnez **Préréglages**.
2. À côté de **Préréglages**, sélectionnez le bouton **+** (**Nouveau préréglage**). Un nouveau préréglage nommé `Preset 1` (ou le numéro libre suivant) s'ouvre dans l'éditeur.
3. Dans le champ de nom en haut, saisissez un nom pour le préréglage, par exemple `Mon premier préréglage`.
4. Sous **Charger le modèle Excel**, sélectionnez **Charger un fichier** et choisissez votre fichier source. Flash-Excel lit ses colonnes pour que les étapes puissent les proposer dans leurs listes.
5. Sous **Configuration des actions**, sélectionnez **Renommer les colonnes** dans la liste des actions.
6. Sélectionnez **Ajouter une règle**. Dans **Colonne source**, choisissez la colonne à renommer ; dans **Nouveau nom**, saisissez son nouveau nom.
7. Sélectionnez **Enregistrer**. Le message **Préréglage enregistré** le confirme, et le préréglage apparaît dans la liste à gauche.

### Prévisualiser et lancer le préréglage

1. Dans la barre latérale, sélectionnez **Traitement**.
2. Cliquez sur la zone de dépôt **Déposez vos fichiers Excel/CSV ici — ou cliquez pour parcourir** et choisissez votre fichier source. Vous pouvez aussi faire glisser le fichier sur la fenêtre.
3. Sous **Preset**, ouvrez la liste et sélectionnez votre préréglage.
4. Sélectionnez **Aperçu**. La fenêtre **Aperçu de la transformation** affiche les 100 premières lignes du fichier après transformation, sans rien écrire. Fermez-la avec **×**.
5. Sous **Sortie**, regardez **Dossier de destination** : par défaut, c'est `Documents\flash-excel\output`. Laissez-le tel quel pour ce premier essai. Si votre fichier source est un `.xls` ou un `.xlsm`, réglez **Format** sur **.xlsx (Excel)** : **Même que la source** n'écrit que des fichiers `.xlsx` et `.csv`.
6. Sélectionnez **Lancer le preset**.

## ✅ Résultat

La ligne du fichier affiche le statut **Terminé**, et la **Console** se termine par une ligne du type `Terminé en 0.42s → C:\Users\<vous>\Documents\flash-excel\output\<fichier>_clean.xlsx`. Ouvrez ce dossier : votre fichier transformé s'y trouve, nommé d'après le fichier source suivi de `_clean`, et le fichier source est inchangé.

Si l'exécution se termine par **Erreur**, la **Console** en indique la raison. Consultez [Dépannage](troubleshooting.md).

## ➡️ Étapes suivantes

- [Ajouter des étapes à un préréglage](tasks/presets/add-steps-to-a-preset.md) — filtrer, nettoyer, trier et plus encore.
- [Lancer un préréglage](tasks/run/run-a-preset.md) sur plusieurs fichiers, avec votre propre dossier, format et modèle de nom de sortie.
- [Planifier un préréglage](tasks/automate/schedule-a-preset.md) pour qu'il s'exécute chaque jour sans ouvrir Flash-Excel.
- [Préréglages](concepts/presets.md) — ce que contient un préréglage et où il est stocké.
