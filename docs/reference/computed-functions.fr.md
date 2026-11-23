# Fonctions des colonnes calculées

L'étape **Ajouter une colonne calculée** crée une nouvelle colonne à partir d'une formule, appelée *expression*. L'expression est calculée pour chaque ligne. Cette page liste tout ce qu'une expression peut contenir.

Les noms de fonctions sont en français, d'après la version française d'Excel (`CONCATENER` pour `CONCAT`, `SI` pour `IF`). Saisissez-les exactement comme indiqué, en majuscules.

## Écrire une expression {#writing-an-expression}

Une expression combine des références de colonnes, des valeurs littérales, des opérateurs et des fonctions :

```text
SI([Prix unitaire] * qte > 1000, "gros", "petit")
```

L'éditeur vous aide à la construire : sélectionner une pastille sous **Colonnes**, **Fonctions** ou **Séparateurs** l'ajoute à la fin de l'expression. Vous saisissez vous-même les virgules entre les arguments et les parenthèses fermantes. Survoler une fonction affiche sa description et un **Exemple**.

### Références de colonnes {#column-references}

| Syntaxe                 | Quand l'utiliser                                                                                                  | Exemple           |
| :---------------------- | :---------------------------------------------------------------------------------------------------------------- | :---------------- |
| `nom`                   | Le nom de colonne ne contient que des lettres, des chiffres et des tirets bas, et ne commence pas par un chiffre. | `nom_famille`     |
| `[Nom de colonne]`      | Tout autre nom : espaces, chiffre en tête, symboles comme `°`, `€` ou `-`.                                        | `[Prix unitaire]` |
| `col("Nom de colonne")` | Comme les crochets. Fonctionne aussi quand une colonne porte le même nom qu'une fonction.                         | `col("ABS")`      |

Les pastilles **Colonnes** ajoutent les crochets pour vous quand un nom en a besoin. Un nom entre crochets doit correspondre exactement à une colonne existante ; sinon l'expression est refusée avec *Invalid syntax*.

Une référence de colonne utilise les colonnes telles qu'elles sont à cette étape : les colonnes renommées s'appellent par leur nouveau nom, et une colonne calculée plus tôt peut être utilisée par une suivante.

!!! note "Lettres accentuées dans les noms"
    Une colonne dont le nom contient une lettre accentuée, comme `Prénom`, peut s'écrire sans crochets si le nom ne contient ni espace ni symbole. En cas de doute, utilisez la pastille sous **Colonnes**.

### Valeurs littérales {#literal-values}

| Type    | Comment l'écrire                                     | Exemple             |
| :------ | :--------------------------------------------------- | :------------------ |
| Texte   | Entre guillemets doubles ou simples                  | `"majeur"`, `' - '` |
| Nombre  | Des chiffres, avec un point comme séparateur décimal | `18`, `1.2`         |
| Booléen | `True` ou `False`                                    | `True`              |

Une expression doit utiliser au moins une colonne ou une fonction. Un littéral seul, comme `"N/A"` ou `0`, est refusé avec *The expression must return a Polars Expr*. Pour remplir une colonne avec un texte fixe, écrivez `CONCATENER("N/A")`.

### Opérateurs {#operators}

| Opérateur                   | Signification                                | Exemple                    |
| :-------------------------- | :------------------------------------------- | :------------------------- |
| `+` `-` `*` `/`             | Additionner, soustraire, multiplier, diviser | `[Prix unitaire] * qte`    |
| `//` `%` `**`               | Division entière, reste, puissance           | `qte % 2`                  |
| `-` (devant)                | Valeur négative                              | `-ecart`                   |
| `+` entre textes            | Assemble deux textes                         | `MAJUSCULE(code) + "-FR"`  |
| `==` `!=` `<` `>` `<=` `>=` | Comparaisons ; donnent vrai ou faux          | `age >= 18`                |
| `&` <code>&#124;</code> `~` | Et, ou, non — pour combiner des comparaisons | `(age >= 18) & (age < 65)` |
| `( )`                       | Regroupement                                 | `(a + b) * 2`              |

- L'égalité s'écrit `==`. Un `=` seul est refusé avec *Invalid syntax*.
- Combinez les conditions avec `&` et `|`, et mettez chaque comparaison entre parenthèses. Les mots `and`, `or`, `not` et `in` ne fonctionnent pas sur des colonnes et échouent avec *the truth value of an Expr is ambiguous*.
- Une division par zéro donne une valeur infinie, pas une erreur.

## Fonctions {#functions}

| Fonction      | Catégorie | Signature                                 | Résultat                                                |
| :------------ | :-------- | :---------------------------------------- | :------------------------------------------------------ |
| `CONCATENER`  | Texte     | `CONCATENER(partie1, partie2, …, sep="")` | Les parties assemblées en un seul texte.                |
| `MAJUSCULE`   | Texte     | `MAJUSCULE(texte)`                        | Le texte en majuscules.                                 |
| `MINUSCULE`   | Texte     | `MINUSCULE(texte)`                        | Le texte en minuscules.                                 |
| `GAUCHE`      | Texte     | `GAUCHE(texte, n)`                        | Les `n` premiers caractères.                            |
| `DROITE`      | Texte     | `DROITE(texte, n)`                        | Les `n` derniers caractères.                            |
| `NBCAR`       | Texte     | `NBCAR(texte)`                            | Le nombre de caractères.                                |
| `SUPPRESPACE` | Texte     | `SUPPRESPACE(texte)`                      | Le texte sans espaces en début ni en fin.               |
| `ARRONDI`     | Math      | `ARRONDI(nombre, n=0)`                    | Le nombre arrondi à `n` décimales.                      |
| `ABS`         | Math      | `ABS(nombre)`                             | La valeur absolue.                                      |
| `MULTIPLIER`  | Math      | `MULTIPLIER(nombre, n)`                   | Le nombre multiplié par `n`.                            |
| `AJOUTER`     | Math      | `AJOUTER(nombre1, nombre2)`               | La somme des deux valeurs.                              |
| `ANNEE`       | Date      | `ANNEE(date)`                             | L'année.                                                |
| `MOIS`        | Date      | `MOIS(date)`                              | Le mois, de 1 à 12.                                     |
| `JOUR`        | Date      | `JOUR(date)`                              | Le jour du mois.                                        |
| `AUJOURD_HUI` | Date      | `AUJOURD_HUI()`                           | La date du jour où le préréglage s'exécute.             |
| `SI`          | Logique   | `SI(condition, alors, sinon)`             | `alors` là où la condition est vraie, `sinon` ailleurs. |

Les arguments notés *texte*, *nombre* ou *date* acceptent une référence de colonne ou un autre appel de fonction. `n` est un nombre que vous saisissez.

### CONCATENER

Assemble des colonnes et des textes en un seul texte. Les colonnes numériques sont converties en texte. Le paramètre facultatif `sep` est inséré entre chaque partie.

```text
CONCATENER(prenom, " ", nom)                → "Anne Martin"
CONCATENER(annee, mois, jour, sep="-")      → "2024-3-5"
```

Si une partie est vide pour une ligne, le résultat est vide pour cette ligne. Remplissez d'abord les cellules vides avec **Remplir les cellules vides**.

### MAJUSCULE

Convertit tous les caractères en majuscules.

```text
MAJUSCULE(nom)                              → "MARTIN"
```

### MINUSCULE

Convertit tous les caractères en minuscules.

```text
MINUSCULE(email)                            → "anne.martin@example.com"
```

### GAUCHE

Retourne les `n` premiers caractères. `GAUCHE(code, 0)` retourne un texte vide.

```text
GAUCHE(code, 3)                             → "FR-" pour "FR-1234"
```

### DROITE

Retourne les `n` derniers caractères. `DROITE(reference, 0)` retourne un texte vide.

```text
DROITE(reference, 4)                        → "1234" pour "FR-1234"
```

### NBCAR

Retourne le nombre de caractères, espaces comprises.

```text
NBCAR(description)                          → 13 pour "Bonjour monde"
```

### SUPPRESPACE

Supprime les espaces en début et en fin de texte. Les espaces à l'intérieur du texte sont conservées ; pour les réduire, utilisez l'étape **Nettoyer le texte**.

```text
SUPPRESPACE(nom)                            → "Martin" pour "  Martin "
```

### ARRONDI

Arrondit à `n` décimales. Sans `n`, arrondit à un nombre entier.

```text
ARRONDI(prix, 2)                            → 1.23 pour 1.234
ARRONDI(prix)                               → 1.0 pour 1.234
```

### ABS

Retourne la valeur absolue, toujours positive ou nulle.

```text
ABS(ecart)                                  → 5 pour -5
```

### MULTIPLIER

Multiplie chaque valeur par `n`. Équivaut à `prix * 1.2`.

```text
MULTIPLIER(prix, 1.2)                       → 120 pour 100
```

### AJOUTER

Additionne deux valeurs : deux colonnes numériques, ou une colonne et un nombre. Équivaut à `base + bonus`.

```text
AJOUTER(base, bonus)                        → 1200 pour 1000 et 200
```

### ANNEE

Extrait l'année. La colonne doit contenir des dates ou des dates et heures ; convertissez d'abord une colonne texte avec **Convertir les types**.

```text
ANNEE(date_naissance)                       → 1990
```

### MOIS

Extrait le mois, de 1 à 12.

```text
MOIS(date_commande)                         → 3 pour 2024-03-05
```

### JOUR

Extrait le jour du mois.

```text
JOUR(date_livraison)                        → 5 pour 2024-03-05
```

### AUJOURD_HUI

Retourne la date du jour où le préréglage s'exécute. Elle ne prend aucun argument mais garde ses parenthèses. La pastille de l'éditeur l'affiche sous la forme `AUJOURD'HUI` ; dans l'expression, écrivez `AUJOURD_HUI()` avec un tiret bas.

```text
AUJOURD_HUI()                               → 2026-10-21
```

### SI

Retourne `alors` là où la condition est vraie et `sinon` partout ailleurs. `alors` et `sinon` peuvent être des colonnes, des textes ou des nombres. La condition utilise les opérateurs de comparaison `==`, `!=`, `<`, `>`, `<=`, `>=`, combinés si besoin avec `&`, `|` et `~`.

```text
SI(age >= 18, "majeur", "mineur")
SI((qte > 1) & (qte < 10), "lot", "unité")
SI(statut == "Actif", salaire, 0)
```

## Erreurs {#errors}

Quand une expression ne peut pas être calculée, l'étape échoue. La **Console** affiche l'un de ces messages (toujours en anglais) :

| Message                                                                                | Cause                                                                                                                                                 | Solution                                                                                   |
| :------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------- |
| `Invalid syntax:`                                                                      | Parenthèses ou guillemets non appariés, virgule manquante, `=` au lieu de `==`, ou `[Nom]` qui ne correspond à aucune colonne.                        | Vérifiez la ponctuation ; vérifiez le nom de colonne entre crochets.                       |
| `Expression not allowed: '…' is not available. Use column names or catalog functions.` | Un nom qui n'est ni une colonne à cette étape ni une fonction : faute de frappe, mauvaise casse, ou colonne renommée ou retirée plus tôt.             | Corrigez le nom, ou utilisez `[Nom de colonne]`. Les noms de fonctions sont en majuscules. |
| `Expression not allowed:` (autre texte)                                                | L'expression utilise une construction non autorisée.                                                                                                  | N'utilisez que les fonctions et opérateurs de cette page.                                  |
| `Evaluation error:`                                                                    | Il manque un argument à une fonction (*missing 1 required positional argument*), ou `and`/`or`/`in` a été utilisé au lieu de `&`/<code>&#124;</code>. | Vérifiez la signature de la fonction sur cette page.                                       |
| `invalid series dtype: expected String`, `… operation not supported for dtype …`       | Une fonction a reçu une colonne du mauvais type : `MAJUSCULE` sur un nombre, `ANNEE` sur du texte, `ABS` sur du texte.                                | Convertissez d'abord la colonne avec **Convertir les types**.                              |
| `The expression must return a Polars Expr`                                             | L'expression est une simple valeur, sans colonne ni fonction.                                                                                         | Enveloppez la valeur, par exemple `CONCATENER("N/A")`.                                     |

Consultez aussi [Dépannage](../troubleshooting.md#is-not-available-use-column-names-or-catalog-functions).
