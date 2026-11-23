# Étapes et ordre

Un préréglage est une chaîne d'**étapes**. Chaque étape fait un type de transformation — renommer des colonnes, filtrer des lignes, trier des lignes — et transmet son résultat à la suivante. Le fichier de sortie est ce qui sort de la dernière étape.

## Les étapes s'exécutent l'une après l'autre

Les étapes ne voient jamais directement le fichier source : chacune travaille sur le résultat des étapes précédentes. Cela a trois effets concrets :

- **Les colonnes retirées disparaissent pour les étapes suivantes.** Après **Sélectionner les colonnes** ou **Supprimer des colonnes**, une étape suivante ne peut pas utiliser une colonne écartée.
- **Les colonnes renommées changent de nom pour les étapes suivantes.** Après **Renommer les colonnes**, les étapes suivantes utilisent le nouveau nom.
- **Les colonnes ajoutées n'existent que pour les étapes suivantes.** Une colonne créée par **Ajouter une colonne calculée** peut être filtrée, triée ou réordonnée, car ces étapes viennent après elle.

L'éditeur suit cette chaîne pour vous. Les listes de colonnes proposées par chaque étape montrent les colonnes telles qu'elles sont *à ce stade*, et non telles qu'elles sont dans le fichier source. Quand vous renommez une colonne, les étapes suivantes sont mises à jour avec le nouveau nom. Quand un fichier modèle nouvellement chargé ne contient plus certaines colonnes, la fenêtre **Structure de colonnes modifiée** propose **Charger et nettoyer les références** pour les retirer de vos étapes.

Si une étape fait encore référence à une colonne qui n'existe plus au moment de l'exécution, cette étape échoue et le fichier est traité selon le choix **En cas d'erreur**. Consultez [Gestion des erreurs](error-handling.md).

## L'ordre utilisé par l'éditeur

Sur la page **Préréglages**, la liste **Configuration des actions** présente les 12 types d'étapes dans un ordre fixe. Vous configurez chaque type au plus une fois, et le préréglage exécute ceux qui sont configurés dans cet ordre :

| Ordre | Étape (telle qu'affichée)        | Usage type                                                          |
| :---: | :------------------------------- | :------------------------------------------------------------------ |
|   1   | **Renommer les colonnes**        | Donner aux colonnes sources les noms avec lesquels vous travaillez. |
|   2   | **Sélectionner les colonnes**    | Ne garder que les colonnes utiles.                                  |
|   3   | **Supprimer des colonnes**       | Retirer quelques colonnes.                                          |
|   4   | **Convertir les types**          | Transformer du texte en nombres, dates ou booléens.                 |
|   5   | **Remplacer les valeurs**        | Remplacer des valeurs exactes, comme des codes par des libellés.    |
|   6   | **Nettoyer le texte**            | Supprimer les espaces, les accents, changer la casse.               |
|   7   | **Remplir les cellules vides**   | Remplacer les cellules vides par une valeur ou une voisine.         |
|   8   | **Ajouter une colonne calculée** | Créer une colonne à partir d'une formule.                           |
|   9   | **Filtrer les lignes**           | Ne garder que les lignes qui remplissent des conditions.            |
|  10   | **Dédupliquer les lignes**       | Retirer les lignes en double.                                       |
|  11   | **Trier les lignes**             | Ordonner les lignes.                                                |
|  12   | **Réordonner les colonnes**      | Fixer l'ordre final des colonnes.                                   |

Une étape laissée vide n'est pas enregistrée et ne s'exécute pas ; si elle n'était qu'en partie remplie, **Enregistrer** vous signale qu'elle a été refusée (**Préréglage enregistré, mais ces étapes ont été refusées et sont absentes du fichier**). Les étapes ne peuvent pas être glissées dans un autre ordre dans l'éditeur : l'ordre ci-dessus est conçu pour que chaque étape trouve les colonnes et les types dont elle a besoin.

Trois types d'étapes contiennent plusieurs règles : **Remplacer les valeurs** (une règle par colonne), **Nettoyer le texte** (une action de nettoyage par groupe de colonnes) et **Ajouter une colonne calculée** (une règle par nouvelle colonne). Chaque règle est enregistrée comme une étape à part, et les règles s'exécutent de haut en bas.

Pour ce que fait et accepte chaque étape, consultez la [référence des étapes](../reference/steps.md).

## Préréglages écrits à la main {#presets-written-by-hand}

Dans un fichier de préréglage que vous écrivez vous-même, les étapes s'exécutent dans l'ordre où elles apparaissent dans le fichier, et le même type d'étape peut apparaître plusieurs fois. Cela vous donne un contrôle total, par exemple pour filtrer les lignes avant de nettoyer le texte.

!!! warning "Ouvrir un préréglage écrit à la main dans l'éditeur"
    L'éditeur affiche une étape de chaque type. Quand un fichier répète un type qui ne contient qu'un jeu de règles (par exemple deux étapes **Filtrer les lignes**), l'éditeur n'affiche que la dernière, et sélectionner **Enregistrer** réécrit les étapes dans l'ordre de l'éditeur ci-dessus. Tenez à l'écart de l'éditeur les préréglages écrits à la main qui dépendent de leur propre ordre, ou vérifiez-les après l'enregistrement.

## ➡️ Étapes suivantes

- [Ajouter des étapes à un préréglage](../tasks/presets/add-steps-to-a-preset.md)
- [Prévisualiser une transformation](../tasks/run/preview-a-transformation.md)
- [Fichier de préréglage](../reference/preset-file.md)
