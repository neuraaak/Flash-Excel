# Ajouter une colonne calculée

Ajoutez une colonne dont les valeurs sont calculées à partir d'autres colonnes, par exemple un nom complet construit à partir d'un prénom et d'un nom, ou un prix arrondi à deux décimales.

## 🔧 Prérequis

- Un préréglage ouvert sur la page **Préréglages**, avec un fichier modèle chargé. Consultez [Créer un préréglage](create-a-preset.md).

## 📝 Étapes

1. Sous **Configuration des actions**, sélectionnez **Ajouter une colonne calculée**.
2. Dans le panneau, sélectionnez **Ajouter une colonne calculée**. La fenêtre **Nouvelle colonne calculée** s'ouvre.
3. Dans **Nom de la nouvelle colonne**, saisissez le nom de la colonne à créer.
4. Construisez la formule dans **Expression** :
    - sélectionnez une colonne sous **Colonnes** pour l'insérer ;
    - sélectionnez un séparateur sous **Séparateurs** pour l'insérer comme texte, par exemple `" "` ;
    - sous **Fonctions**, choisissez une catégorie (**Texte**, **Math**, **Date** ou **Logique**), puis sélectionnez une fonction pour l'insérer. Survolez une fonction pour voir sa description et un **Exemple**.
5. Vérifiez l'expression, puis sélectionnez **Enregistrer**.
6. Recommencez à l'étape 2 pour chaque colonne à ajouter, puis sélectionnez **Enregistrer** dans la barre d'outils pour enregistrer le préréglage.

Exemples d'expressions :

| Expression                          | Résultat                                               |
| :---------------------------------- | :----------------------------------------------------- |
| `CONCATENER(prenom, " ", nom)`      | Assemble les deux colonnes avec une espace.            |
| `MAJUSCULE(nom)`                    | Le nom en majuscules.                                  |
| `ARRONDI(prix, 2)`                  | Le prix arrondi à deux décimales.                      |
| `ANNEE(date_naissance)`             | L'année d'une colonne date.                            |
| `SI(age >= 18, "majeur", "mineur")` | `majeur` quand la condition est vraie, `mineur` sinon. |

!!! tip "Noms de colonnes avec espaces ou symboles"
    Écrivez entre crochets une colonne dont le nom contient des espaces, commence par un chiffre ou comporte des symboles, par exemple `[Date de commande]`. Sélectionner la colonne sous **Colonnes** l'insère sous la bonne forme.

!!! note "Les noms de fonctions sont en français"
    Les noms de fonctions (`CONCATENER`, `MAJUSCULE`, `SI`…) suivent Excel en français et restent les mêmes quelle que soit la langue de l'interface. Les valeurs texte se mettent entre guillemets droits doubles.

## ✅ Résultat

La colonne calculée est listée dans le panneau avec son expression. Sélectionnez l'icône crayon pour la modifier, ou l'icône corbeille pour la supprimer. Dans les étapes suivantes, comme **Filtrer les lignes** ou **Trier les lignes**, la nouvelle colonne est disponible comme n'importe quelle autre.

## ➡️ Étapes suivantes

- [Fonctions des colonnes calculées](../../reference/computed-functions.md) — chaque fonction, ses arguments et des exemples.
- [Prévisualiser une transformation](../run/preview-a-transformation.md) pour vérifier les valeurs.
