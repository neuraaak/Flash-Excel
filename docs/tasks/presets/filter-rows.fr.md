# Filtrer des lignes

Ne conservez que les lignes qui répondent à vos conditions, par exemple les clients actifs ou les commandes au-dessus d'un montant. Les autres lignes sont écartées du fichier de sortie.

## 🔧 Prérequis

- Un préréglage ouvert sur la page **Préréglages**, avec un fichier modèle chargé. Consultez [Créer un préréglage](create-a-preset.md).

## 📝 Étapes

1. Sous **Configuration des actions**, sélectionnez **Filtrer les lignes**.
2. À côté de **Conserver les lignes correspondant à**, choisissez comment les conditions se combinent :
    - **Toutes les conditions** : une ligne est conservée si elle remplit chaque condition ;
    - **N'importe quelle condition** : une ligne est conservée si elle remplit au moins une condition.
3. Sélectionnez **Ajouter une règle**. Une ligne de condition apparaît.
4. Dans la ligne de condition :
    1. choisissez la colonne ;
    2. choisissez l'opérateur : `=`, `≠`, `>`, `≥`, `<`, `≤`, **contient**, **commence par** ou **se termine par** ;
    3. saisissez la valeur de comparaison dans **Valeur**.
5. Recommencez les étapes 3 et 4 pour chaque condition. Sélectionnez **×** au bout d'une ligne pour la retirer.
6. Sélectionnez **Enregistrer**.

## ✅ Résultat

L'action **Filtrer les lignes** affiche le nombre de conditions dans la liste des actions. À l'exécution du préréglage, seules les lignes correspondantes sont écrites.

!!! note "Comment les valeurs sont comparées"
    - Sur une colonne numérique, saisissez un nombre : une valeur texte sur une colonne numérique fait échouer l'exécution avec une erreur.
    - **contient**, **commence par** et **se termine par** comparent le texte exactement tel qu'il est saisi, majuscules et minuscules comprises.
    - Une condition dont la valeur est vide est ignorée. Sans aucune condition, toutes les lignes sont conservées.

!!! tip "Vérifier le filtre sur un aperçu"
    L'aperçu ne lit que les 100 premières lignes du fichier. Si aucune ligne de cet échantillon ne correspond, l'aperçu l'indique alors que des lignes plus loin peuvent correspondre. Consultez [Prévisualiser une transformation](../run/preview-a-transformation.md).

## ➡️ Étapes suivantes

- [Étapes](../../reference/steps.md) — les options de **Filtrer les lignes** en détail.
- [Une étape ne trouve pas une colonne](../../troubleshooting.md#column-not-found) si une exécution échoue sur un filtre.
