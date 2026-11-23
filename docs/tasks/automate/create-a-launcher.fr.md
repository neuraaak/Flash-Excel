# Créer un lanceur

Enregistrez un fichier `.cmd` qui lance un préréglage sur les mêmes fichiers d'un double-clic, sans ouvrir Flash-Excel. Utilisez-le pour une exécution que vous répétez à la demande plutôt qu'à heure fixe.

## 🔧 Prérequis

- Sur la page **Traitement**, les fichiers à traiter sont chargés et le préréglage est sélectionné. Consultez [Charger des fichiers sources](../files/load-source-files.md).
- Le préréglage et les fichiers sources restent à leur place : le lanceur utilise leurs chemins actuels.

## 📝 Étapes

1. Sur la page **Traitement**, sous **Exécution planifiée ou manuelle**, sélectionnez **Configurer une exécution**. La fenêtre **Planifier ou créer un lanceur** s'ouvre.
2. Vérifiez le **Nom de l'exécution**, les **Fichiers sources** et les réglages de sortie : **Dossier de destination**, **Format** et **Modèle de nom**.
3. Sélectionnez **Créer un lanceur .cmd**.
4. Dans la boîte de dialogue d'enregistrement, choisissez où enregistrer le lanceur. Son nom par défaut est le **Nom de l'exécution**, avec l'extension `.cmd`. Gardez cette extension.

## ✅ Résultat

Le message **Lanceur créé. Double-cliquez dessus pour exécuter cette configuration.** apparaît, et la fenêtre indique où le lanceur a été enregistré.

Double-cliquez sur le lanceur pour l'exécuter. Une fenêtre de console s'ouvre, affiche une ligne par fichier, soit `<fichier> -> <chemin de sortie> (<n> rows)`, soit `<fichier> FAILED: <raison>`, et reste ouverte jusqu'à ce que vous appuyiez sur une touche. Si un fichier échoue, le lanceur continue avec le suivant.

Pour retirer un lanceur, supprimez son fichier `.cmd`.

!!! note "Noms et chemins refusés"
    Le **Nom de l'exécution** doit compter de 1 à 200 caractères, sans `\ / : * ? " < > | % !`. Les chemins du préréglage, des fichiers et du dossier de destination ne peuvent pas contenir `%`, `!` ni de guillemets.

## ➡️ Étapes suivantes

- [Planifier un préréglage](schedule-a-preset.md) pour lancer la même configuration chaque jour.
- [Lancer en ligne de commande](run-from-the-command-line.md)
