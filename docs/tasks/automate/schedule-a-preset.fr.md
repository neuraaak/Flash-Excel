# Planifier un préréglage

Lancez un préréglage sur les mêmes fichiers chaque jour à heure fixe, sans ouvrir Flash-Excel. Flash-Excel crée la tâche pour vous dans le Planificateur de tâches Windows.

## 🔧 Prérequis

- Sur la page **Traitement**, les fichiers à traiter sont chargés et le préréglage est sélectionné. Consultez [Charger des fichiers sources](../files/load-source-files.md) et [Lancer un préréglage](../run/run-a-preset.md).
- Le préréglage et les fichiers sources restent à leur place : la tâche utilise leurs chemins actuels.

## 📝 Étapes

1. Sur la page **Traitement**, sous **Exécution planifiée ou manuelle**, sélectionnez **Configurer une exécution**. La fenêtre **Planifier ou créer un lanceur** s'ouvre.
2. Vérifiez les réglages :
    - **Nom de l'exécution** : le nom de la tâche. Par défaut, `flash-excel` suivi du nom du fichier de préréglage.
    - **Heure quotidienne (tâche planifiée)** : l'heure de l'exécution quotidienne. Par défaut, `08:00`.
    - **Preset** et **Fichiers sources** : le préréglage et les fichiers que la tâche traitera.
    - **Dossier de destination**, **Format** et **Modèle de nom** : la sortie de la tâche. Ils reprennent les valeurs de la page **Traitement** ; sélectionnez **Choisir un dossier de sortie** pour choisir un autre dossier.
3. Sélectionnez **Ajouter au planificateur**.
4. Dans la fenêtre **Confirmer la création de la tâche**, lisez le résumé et l'avertissement, puis sélectionnez **Confirmer la création**.

## ✅ Résultat

Le message **Tâche planifiée « <nom> » créée.** apparaît. La tâche se trouve dans le Planificateur de tâches Windows, sous **Bibliothèque du Planificateur de tâches** › **Flash-Excel**, et s'exécute chaque jour à l'heure choisie.

- La tâche s'exécute lorsque votre session Windows est ouverte. Flash-Excel lui-même peut être fermé.
- Si un fichier échoue, la tâche continue avec le fichier suivant. Le choix **En cas d'erreur** de la page **Traitement** ne s'applique pas.
- Chaque exécution remplace les fichiers de sortie de la précédente quand les noms sont identiques.

!!! warning "Vous êtes responsable de la tâche"
    La tâche se répète chaque jour jusqu'à ce que vous la [désactiviez ou la supprimiez](remove-a-scheduled-task.md). Vérifiez les fichiers, le préréglage et la destination avant de confirmer.

!!! note "Noms et chemins refusés"
    Le **Nom de l'exécution** doit compter de 1 à 200 caractères, sans `\ / : * ? " < > | % !`. Les chemins du préréglage, des fichiers et du dossier de destination ne peuvent pas contenir `%`, `!` ni de guillemets.

!!! tip "Copier la commande à la place"
    **Avancé : copier la commande de planification** copie une commande `schtasks` dans le presse-papiers, pour créer la tâche vous-même. Windows refuse cette commande quand elle dépasse 261 caractères ; utilisez alors **Ajouter au planificateur**.

## ➡️ Étapes suivantes

- [Créer un lanceur](create-a-launcher.md) pour lancer la même configuration à la demande.
- [Lancer en ligne de commande](run-from-the-command-line.md) — ce que la tâche exécute réellement.
- [Désactiver ou supprimer une tâche planifiée](remove-a-scheduled-task.md)
- [La tâche planifiée ne s'est pas exécutée](../../troubleshooting.md#scheduled-task-did-not-run)
