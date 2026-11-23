# Gestion des erreurs

Une exécution peut échouer pour un fichier — le fichier est ouvert dans Excel, une étape fait référence à une colonne absente, une valeur ne peut pas être convertie. Le choix **En cas d'erreur** de la page **Traitement** décide de ce que fait ensuite Flash-Excel. Il compte surtout quand vous traitez plusieurs fichiers en une exécution.

## Les trois choix

| Choix (tel qu'affiché dans l'application)                | Quand une étape échoue                                                                                                                        | Suite de l'exécution                                                                 |
| :------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------- |
| **Passer le fichier** — *continuer la file* (par défaut) | Le traitement de ce fichier s'arrête. Aucun fichier de sortie n'est écrit pour lui. Son statut devient **Ignoré**.                            | Les fichiers suivants sont traités.                                                  |
| **Tout arrêter** — *stopper à la première erreur*        | Le traitement de ce fichier s'arrête. Aucun fichier de sortie n'est écrit pour lui. Son statut devient **Erreur**.                            | Toute l'exécution s'arrête. Les fichiers non encore traités sont marqués **Ignoré**. |
| **Ignorer** — *écrire partiellement*                     | L'étape en échec est écartée : les données la traversent sans changement. Les étapes suivantes s'exécutent et le fichier de sortie est écrit. | Les fichiers suivants sont traités.                                                  |

Avec **Ignorer**, la sortie est *partielle* : il lui manque l'effet de chaque étape en échec. Vérifiez la **Console** avant d'utiliser un tel fichier.

## Erreurs hors des étapes

Certaines erreurs surviennent avant la première étape ou après la dernière : le fichier source ne peut pas être lu (absent, verrouillé par Excel, format illisible), ou le fichier de sortie ne peut pas être écrit. Aucune sortie ne peut alors être produite, quel que soit le choix :

- le statut du fichier devient **Erreur** ;
- avec **Passer le fichier** et **Ignorer**, les fichiers suivants sont quand même traités ;
- avec **Tout arrêter**, toute l'exécution s'arrête.

## Où apparaissent les erreurs

- La **Console** en bas de la page **Traitement** affiche chaque message d'erreur, et **Erreurs** les compte. **Avertissements** compte des messages comme *Fichier ignoré suite à une erreur dans « … »*.
- Chaque fichier de la file affiche son propre statut : **En attente**, **En cours**, **Terminé**, **Erreur** ou **Ignoré**.
- Le journal de l'application garde une trace de chaque exécution. Consultez [Emplacements des données](../reference/data-locations.md#logs).

## Arrêter soi-même une exécution

Le bouton d'arrêt (le carré à côté de **Lancer le preset**) demande l'arrêt de l'exécution. Flash-Excel termine l'étape en cours, puis s'arrête : le fichier courant n'est pas écrit, et les fichiers suivants ne sont pas traités. La **Console** affiche *Exécution arrêtée par l'utilisateur.* Consultez [Arrêter une exécution](../tasks/run/stop-a-run.md).

## Exécutions hors de la fenêtre

Les lanceurs, les tâches planifiées et la ligne de commande n'ont pas de choix **En cas d'erreur**. Ils se comportent toujours comme **Passer le fichier** : un fichier qui échoue à n'importe quel moment n'a pas de sortie, et les fichiers suivants sont quand même traités. L'exécution se termine alors avec le code de sortie `1` au lieu de `0`. Consultez [Ligne de commande](../reference/command-line.md#exit-codes).

## ➡️ Étapes suivantes

- [Lancer un préréglage](../tasks/run/run-a-preset.md)
- [Dépannage](../troubleshooting.md)
