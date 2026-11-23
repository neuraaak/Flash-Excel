# Supprimer un préréglage

Retirez un préréglage dont vous n'avez plus besoin. Supprimer un préréglage efface son fichier de votre dossier de préréglages.

## 🔧 Prérequis

- Un préréglage qui vous appartient, listé avec le libellé **Local**. Les préréglages d'un dossier partagé ne peuvent pas être supprimés depuis Flash-Excel.

## 📝 Étapes

1. Dans la barre latérale, sélectionnez **Préréglages**.
2. Sélectionnez le préréglage dans la liste à gauche.
3. Dans la barre d'outils, sélectionnez **Supprimer**.
4. Dans la fenêtre **Supprimer le preset**, vérifiez le nom après **Voulez-vous vraiment supprimer**, puis sélectionnez **Supprimer**.

## ✅ Résultat

Le message **Préréglage supprimé** apparaît et le préréglage quitte la liste. Son fichier `.toml` est supprimé de `Documents\flash-excel\presets`.

!!! warning "Cette action est irréversible"
    Flash-Excel ne garde aucune copie d'un préréglage supprimé. [Exportez le préréglage](export-a-preset.md) d'abord si vous risquez d'en avoir encore besoin.

!!! note "Tâches planifiées et lanceurs"
    Une tâche planifiée ou un lanceur qui utilise le préréglage supprimé échoue à sa prochaine exécution. Retirez-le aussi : consultez [Planifier un préréglage](../automate/schedule-a-preset.md).

## ➡️ Étapes suivantes

- [Créer un préréglage](create-a-preset.md)
