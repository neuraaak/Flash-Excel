# Prévisualiser une transformation

Vérifiez ce qu'un préréglage fait à vos données avant d'écrire le moindre fichier. L'aperçu applique le préréglage aux 100 premières lignes d'un fichier source et affiche le résultat dans un tableau.

## 🔧 Prérequis

- Au moins un fichier source chargé sur la page **Traitement**. Consultez [Charger des fichiers sources](../files/load-source-files.md).
- Un préréglage enregistré. Les modifications faites sur la page **Préréglages** ne sont prévisualisées qu'après avoir sélectionné **Enregistrer** sur cette page.

## 📝 Étapes

1. Dans la barre latérale, sélectionnez **Traitement**.
2. Sous **Preset**, sélectionnez le préréglage à vérifier.
3. Sélectionnez **Aperçu**.

## ✅ Résultat

La fenêtre **Aperçu de la transformation** s'ouvre. Elle affiche les colonnes et les lignes après transformation, ainsi que le nombre de lignes restantes, par exemple **87 lignes après transformation**. Les cellules vides affichent `null`. Aucun fichier de sortie n'est écrit.

Fermez la fenêtre avec **×**, ++esc++ ou en cliquant à l'extérieur.

!!! note "Ce que couvre l'aperçu"
    - Seul le premier fichier de la liste est prévisualisé, même quand plusieurs fichiers sont chargés.
    - Seules les 100 premières lignes de ce fichier sont lues. **Filtrer les lignes**, **Dédupliquer les lignes** et **Trier les lignes** n'agissent donc que sur cet échantillon : une ligne au-delà des 100 premières peut quand même correspondre à vos filtres lors d'une vraie exécution.
    - S'il ne reste aucune ligne de l'échantillon, la fenêtre indique **Aucune ligne ne reste dans cet échantillon après transformation.**

Si l'aperçu échoue, la fenêtre affiche **Échec de l'aperçu :** suivi de la raison. Cherchez cette raison dans [Dépannage](../../troubleshooting.md). Si l'aperçu ignore vos dernières modifications, consultez [Les modifications d'un préréglage ne sont pas prises en compte](../../troubleshooting.md#changes-not-used).

## ➡️ Étapes suivantes

- [Lancer un préréglage](run-a-preset.md)
- [Ajouter des étapes à un préréglage](../presets/add-steps-to-a-preset.md) pour ajuster le préréglage.
