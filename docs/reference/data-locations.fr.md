# Emplacements des données

Flash-Excel garde vos données hors de son dossier d'installation, pour que les mises à jour — qui remplacent ce dossier — n'y touchent jamais.

## Vue d'ensemble {#overview}

| Quoi                            | Emplacement                                                          | Contenu                                                                            |
| :------------------------------ | :------------------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| Préréglages                     | `Documents\flash-excel\presets`                                      | Vos préréglages locaux, un fichier `.toml` chacun.                                 |
| Fichiers de sortie (par défaut) | `Documents\flash-excel\output`                                       | Les fichiers écrits par les exécutions quand aucun autre dossier n'est choisi.     |
| Paramètres                      | `%APPDATA%\flash-excel`                                              | `app.config.yaml`, `theme.config.yaml` et les données de la fenêtre.               |
| Journaux                        | `%LOCALAPPDATA%\flash-excel\logs`                                    | `flash-excel.log` et ses archives.                                                 |
| Préréglages partagés            | Les dossiers listés sous **Sources de préréglages en lecture seule** | Des préréglages maintenus par quelqu'un d'autre. Flash-Excel ne fait que les lire. |
| Programme                       | Le dossier d'installation                                            | L'application elle-même. Remplacée à chaque mise à jour.                           |

Pour ouvrir l'un de ces dossiers, collez son emplacement — par exemple `%APPDATA%\flash-excel` — dans la barre d'adresse de l'Explorateur de fichiers.

## Préréglages et fichiers de sortie {#presets-and-output-files}

`Documents` est votre vrai dossier Documents, y compris quand il est redirigé vers OneDrive (`%USERPROFILE%\OneDrive\Documents`). Les préréglages et les sorties sont des documents ordinaires : ouvrez-les, sauvegardez-les, copiez-les sur un autre PC.

Le dossier de sortie n'est qu'une valeur par défaut. Chaque exécution peut écrire ailleurs : **Dossier de destination** sur la page **Traitement**, ou `--output` en ligne de commande. Un dossier relatif est créé dans `Documents\flash-excel\output`.

## Paramètres {#settings}

`%APPDATA%` est votre dossier de données d'application itinérant, en général `C:\Users\<vous>\AppData\Roaming`. Il contient :

| Fichier ou dossier  | Contenu                                                                                                              |
| :------------------ | :------------------------------------------------------------------------------------------------------------------- |
| `app.config.yaml`   | Palette, mode, langue, sortie CSV et dossiers de préréglages partagés. Consultez [Paramètres](settings.md).          |
| `theme.config.yaml` | Les palettes de couleurs. `theme.config.yaml.bak` est la copie précédente, gardée quand une mise à jour les modifie. |
| `.theme.source`     | Marqueur servant à détecter un fichier de palettes plus récent. Ne pas modifier.                                     |
| `webview\`          | Données de la fenêtre de l'application.                                                                              |
| `installer.ini`     | Écrit par l'installateur avec la langue choisie dans l'assistant, lu une fois au démarrage suivant, puis supprimé.   |

Si vous supprimez `app.config.yaml`, Flash-Excel le recrée avec les paramètres par défaut au démarrage suivant.

## Journaux {#logs}

`%LOCALAPPDATA%` est votre dossier local de données d'application, en général `C:\Users\<vous>\AppData\Local`. Le fichier journal `%LOCALAPPDATA%\flash-excel\logs\flash-excel.log` enregistre les démarrages, les exécutions, les erreurs et les vérifications de mise à jour. Ses messages sont en anglais.

- Un nouveau fichier journal est commencé chaque jour ; le précédent est renommé avec sa date et son heure.
- Les fichiers journaux de plus de 14 jours sont supprimés.
- Pour enregistrer plus de détails, démarrez Flash-Excel avec `--debug`, ou ajoutez `--debug` à une exécution en ligne de commande.

Le journal est le premier endroit à consulter quand quelque chose échoue. Consultez [Dépannage](../troubleshooting.md).

## Programme {#program}

Flash-Excel s'installe pour votre seul utilisateur Windows, par défaut sous `%LOCALAPPDATA%\Programs`, sans droits administrateur. Ne stockez rien dans le dossier d'installation : chaque mise à jour le remplace.

## Désinstaller {#uninstalling}

Désinstallez Flash-Excel depuis **Paramètres** › **Applications** dans Windows (ou **Programmes et fonctionnalités**). La désinstallation ne retire que le dossier d'installation.

| Conservé après désinstallation                                                    | Retiré                    |
| :-------------------------------------------------------------------------------- | :------------------------ |
| Préréglages (`Documents\flash-excel\presets`)                                     | Les fichiers du programme |
| Fichiers de sortie (`Documents\flash-excel\output` et tout autre dossier utilisé) |                           |
| Paramètres (`%APPDATA%\flash-excel`)                                              |                           |
| Journaux (`%LOCALAPPDATA%\flash-excel\logs`)                                      |                           |
| Tâches planifiées et lanceurs `.cmd` créés                                        |                           |

Une réinstallation ultérieure retrouve vos préréglages et vos paramètres. Pour tout retirer, supprimez ces dossiers à la main après la désinstallation, et retirez vos tâches planifiées du dossier **Flash-Excel** du Planificateur de tâches (consultez [Planifier un préréglage](../tasks/automate/schedule-a-preset.md)).

## Préréglages des versions antérieures à 1.3.0 {#presets-from-versions-before-130}

Les versions antérieures à 1.3.0 stockaient les préréglages dans le dossier d'installation. À son premier démarrage, une version plus récente copie tout préréglage encore présent à cet endroit vers `Documents\flash-excel\presets`, sans écraser un préréglage de même nom. Les paramètres de ces versions ne sont pas repris.
