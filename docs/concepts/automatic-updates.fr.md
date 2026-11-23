# Mises à jour automatiques

Flash-Excel se tient à jour depuis l'application. Vous n'avez pas besoin de télécharger un nouvel installateur pour chaque version.

## Comment une nouvelle version est détectée

À chaque démarrage, Flash-Excel demande au serveur de mise à jour s'il existe une version plus récente. La vérification se fait en arrière-plan et ne ralentit pas votre travail.

Quand une version plus récente est disponible, le coin inférieur droit de la fenêtre affiche **Mettre à jour vers v*X.Y.Z*** à côté du numéro de version actuel. Rien n'est installé tant que vous ne le sélectionnez pas. Quand aucune mise à jour n'est disponible, ou quand la vérification ne peut pas joindre le serveur (par exemple sans connexion internet), seul le numéro de version est affiché.

## Comment une mise à jour est installée

Quand vous sélectionnez **Mettre à jour vers v*X.Y.Z***, le lien devient **Mise à jour…** pendant que Flash-Excel :

1. télécharge la nouvelle version — souvent sous forme d'un petit correctif plutôt que de l'application entière ;
2. vérifie que le téléchargement est authentique ;
3. ferme la fenêtre, pour que ses fichiers puissent être remplacés, et installe la nouvelle version dans son dossier d'installation.

Redémarrez Flash-Excel s'il ne se rouvre pas de lui-même. Aucun droit administrateur n'est nécessaire, car Flash-Excel est installé pour votre seul utilisateur Windows.

## Mises à jour signées

Chaque version est signée par l'éditeur, et les métadonnées de mise à jour le sont aussi (Flash-Excel utilise [The Update Framework](https://theupdateframework.io/), un standard pour des mises à jour logicielles sûres). Avant d'installer quoi que ce soit, Flash-Excel vérifie ces signatures à l'aide des clés de confiance livrées avec l'application. Un téléchargement altéré, ou qui ne vient pas de l'éditeur, est refusé et rien n'est installé.

## Ce qu'une mise à jour conserve

Une mise à jour ne remplace que le dossier d'installation. Vos paramètres, préréglages, fichiers de sortie et journaux sont stockés ailleurs et restent intacts. Consultez [Emplacements des données](../reference/data-locations.md).

## Quand les mises à jour automatiques ne s'appliquent pas

Les mises à jour ne fonctionnent que dans l'application installée. Si une mise à jour échoue, la raison est écrite dans le journal de l'application, et vous pouvez toujours installer la dernière version à la main depuis la [page des versions GitHub](https://github.com/neuraaak/Flash-Excel/releases). Consultez [Dépannage](../troubleshooting.md#the-update-link-never-appears-or-the-update-fails).

## ➡️ Étapes suivantes

- [Mettre à jour Flash-Excel](../tasks/update/update-flash-excel.md)
- [Notes de version](../release-notes.md)
