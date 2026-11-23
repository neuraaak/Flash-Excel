# Ajouter des étapes à un préréglage

Ajoutez les transformations qu'applique un préréglage : renommer, sélectionner ou supprimer des colonnes, convertir des types, nettoyer du texte, filtrer, trier et plus encore. Chaque action a son propre panneau dans l'éditeur, et Flash-Excel exécute les actions dans un ordre fixe.

## 🔧 Prérequis

- Un préréglage ouvert sur la page **Préréglages**. Consultez [Créer un préréglage](create-a-preset.md).
- Un fichier modèle chargé sous **Charger le modèle Excel**, pour que les étapes puissent lister les colonnes. Sans lui, l'indication **Chargez un fichier pour activer le mapping de colonnes** s'affiche.

## 📝 Étapes

1. Dans la barre latérale, sélectionnez **Préréglages**, puis sélectionnez le préréglage dans la liste à gauche.
2. Sous **Configuration des actions**, sélectionnez une action dans la liste, par exemple **Filtrer les lignes**. Survolez l'icône **i** à côté d'une action pour lire ce qu'elle fait.
3. Configurez l'action dans le panneau de droite. La plupart des actions commencent par **Ajouter une règle** ; l'en-tête du panneau indique combien de règles sont **configuré(s)**.
4. Recommencez pour chaque action nécessaire. Une action qui a au moins une règle affiche son nombre dans la liste.
5. Sélectionnez **Enregistrer**.

Les douze actions, dans l'ordre où Flash-Excel les exécute :

| Ordre | Action                           | Ce qu'elle fait                                               |
| :---: | :------------------------------- | :------------------------------------------------------------ |
|   1   | **Renommer les colonnes**        | Donner un nouveau nom à une ou plusieurs colonnes.            |
|   2   | **Sélectionner les colonnes**    | Conserver uniquement les colonnes choisies.                   |
|   3   | **Supprimer des colonnes**       | Retirer les colonnes choisies.                                |
|   4   | **Convertir les types**          | Convertir des colonnes vers un type de données cible.         |
|   5   | **Remplacer les valeurs**        | Rechercher et remplacer des valeurs dans des colonnes.        |
|   6   | **Nettoyer le texte**            | Rogner, normaliser et supprimer les espaces.                  |
|   7   | **Remplir les cellules vides**   | Remplacer les valeurs nulles selon une stratégie.             |
|   8   | **Ajouter une colonne calculée** | Créer une nouvelle colonne depuis une expression.             |
|   9   | **Filtrer les lignes**           | Conserver uniquement les lignes correspondant aux conditions. |
|  10   | **Dédupliquer les lignes**       | Supprimer les doublons par colonnes clés.                     |
|  11   | **Trier les lignes**             | Ordonner les lignes par une ou plusieurs colonnes.            |
|  12   | **Réordonner les colonnes**      | Changer l'ordre des colonnes.                                 |

Les listes de colonnes de chaque action montrent les colonnes telles qu'elles sont à ce stade de l'exécution, et renommer une colonne met à jour les actions suivantes qui l'utilisent. Consultez [Étapes et ordre](../../concepts/steps-and-order.md).

## ✅ Résultat

Le message **Préréglage enregistré** apparaît et le nombre d'étapes du préréglage est mis à jour dans la liste. Si une étape est incomplète, le message **Préréglage enregistré, mais ces étapes ont été refusées et sont absentes du fichier : …** la nomme : complétez-la et enregistrez de nouveau.

!!! note "Changer l'ordre des étapes"
    Vous ne pouvez pas déplacer une étape dans l'éditeur : la page **Préréglages** enregistre toujours les actions dans l'ordre du tableau ci-dessus. Consultez [Étapes et ordre](../../concepts/steps-and-order.md).

!!! tip "Ordre des colonnes dans le fichier de sortie"
    Pour changer l'ordre des colonnes dans le fichier de sortie, utilisez l'action **Réordonner les colonnes**.

!!! note "Charger un modèle aux colonnes différentes"
    Si vous chargez un fichier modèle dont les colonnes diffèrent de celles enregistrées dans le préréglage, la fenêtre **Structure de colonnes modifiée** liste les **Colonnes absentes du fichier** et les **Nouvelles colonnes dans le fichier**. Sélectionnez **Charger et nettoyer les références** pour retirer les colonnes absentes des étapes, **Ignorer les différences** pour garder les étapes telles quelles, ou **Annuler**.

## ➡️ Étapes suivantes

- [Ajouter une colonne calculée](add-a-computed-column.md)
- [Filtrer des lignes](filter-rows.md)
- [Prévisualiser une transformation](../run/preview-a-transformation.md)
- [Étapes](../../reference/steps.md) — chaque option de chaque action.
