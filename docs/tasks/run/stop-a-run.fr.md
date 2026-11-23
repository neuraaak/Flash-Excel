# Arrêter une exécution

Interrompez une exécution en cours, par exemple quand vous remarquez que le préréglage ou les fichiers ne sont pas les bons.

## 🔧 Prérequis

- Une exécution en cours sur la page **Traitement**. Consultez [Lancer un préréglage](run-a-preset.md).

## 📝 Étapes

1. Sur la page **Traitement**, sélectionnez le bouton d'arrêt carré à droite de **Lancer le preset**. Il n'est disponible que pendant une exécution.

## ✅ Résultat

Flash-Excel laisse l'étape en cours se terminer, puis s'arrête avant l'étape ou le fichier suivant. La **Console** affiche **Exécution arrêtée par l'utilisateur.**

- Les fichiers déjà marqués **Terminé** sont écrits et restent dans le dossier de destination.
- Le fichier en cours de traitement n'est pas écrit s'il lui restait des étapes à appliquer, et il est marqué **Ignoré**.
- Les fichiers pas encore atteints sont marqués **Ignoré**.

Pour traiter les fichiers restants, sélectionnez **Charger un fichier**, choisissez uniquement ces fichiers, puis sélectionnez **Lancer le preset**. Consultez [Charger des fichiers sources](../files/load-source-files.md).

## ➡️ Étapes suivantes

- [Lancer un préréglage](run-a-preset.md)
- [Gestion des erreurs](../../concepts/error-handling.md)
