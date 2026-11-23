# Utiliser des dossiers de préréglages partagés

Utilisez les préréglages d'un dossier partagé, par exemple un dossier d'équipe sur un lecteur réseau, à côté de vos propres préréglages. Flash-Excel lit ces préréglages mais ne les modifie jamais.

## 🔧 Prérequis

- Un dossier qui contient des fichiers de préréglage (`.toml`) et que vous pouvez ouvrir depuis votre ordinateur.

## 📝 Étapes

1. Dans la barre latérale, sélectionnez **Paramètres**.
2. Sous **Sources de préréglages en lecture seule**, sélectionnez **Ajouter une source**.
3. Dans **Libellé**, saisissez un nom court qui identifie le dossier, par exemple `Finance`.
4. Dans **Chemin du dossier**, saisissez le chemin du dossier, ou sélectionnez l'icône dossier (**Choisir un dossier**) pour le choisir.
5. Sélectionnez **Enregistrer**.

## ✅ Résultat

Le dossier est listé sous **Sources de préréglages en lecture seule**. Ses préréglages apparaissent avec le libellé saisi au lieu de **Local** : dans la liste **Preset** de la page **Traitement** à la prochaine ouverture de cette page, et sur la page **Préréglages** après un redémarrage de Flash-Excel.

Vous pouvez ouvrir, prévisualiser et lancer un préréglage partagé comme les vôtres. **Enregistrer** et **Supprimer** sont indisponibles pour lui, car les dossiers partagés sont en lecture seule dans Flash-Excel.

Pour modifier une source, sélectionnez **Modifier** à côté d'elle. Pour la retirer de la liste, sélectionnez l'icône **Supprimer la source**, puis **Supprimer** dans la fenêtre **Retirer cette source partagée ?**. Le dossier et ses préréglages ne sont pas supprimés.

!!! note "Dossier indisponible"
    Si un dossier partagé est inaccessible au moment où Flash-Excel liste les préréglages, par exemple quand le lecteur réseau est déconnecté, ses préréglages ne sont tout simplement pas listés. Ils reviennent dès que le dossier est de nouveau accessible.

## ➡️ Étapes suivantes

- [Exporter un préréglage](export-a-preset.md) pour placer l'un de vos préréglages dans un dossier partagé.
- [Paramètres](../../reference/settings.md) — chaque paramètre et l'endroit où il est stocké.
