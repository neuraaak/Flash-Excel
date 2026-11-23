# Étapes

Flash-Excel propose 12 types d'étapes. Chaque section ci-dessous donne le nom de l'étape dans l'application, son **nom d'action** dans un fichier de préréglage, ses options et son comportement. Pour l'enchaînement des étapes, consultez [Étapes et ordre](../concepts/steps-and-order.md). Pour la syntaxe du fichier, consultez [Fichier de préréglage](../reference/preset-file.md).

Les noms de colonnes sont partout sensibles à la casse. Une étape qui nomme une colonne absente à ce stade de la chaîne échoue, et le fichier est traité selon le choix **En cas d'erreur** (consultez [Gestion des erreurs](../concepts/error-handling.md)).

Les noms d'actions et d'options d'un fichier de préréglage sont en anglais, quelle que soit la langue de l'interface. Les messages d'erreur du moteur de transformation sont eux aussi en anglais.

## Résumé {#summary}

| Étape (dans l'application)       | Nom d'action          | Options principales            |
| :------------------------------- | :-------------------- | :----------------------------- |
| **Renommer les colonnes**        | `rename_columns`      | `mapping`                      |
| **Sélectionner les colonnes**    | `select_columns`      | `columns`                      |
| **Supprimer des colonnes**       | `drop_columns`        | `columns`                      |
| **Convertir les types**          | `cast_types`          | `casts`                        |
| **Remplacer les valeurs**        | `replace_values`      | `column`, `mapping`            |
| **Nettoyer le texte**            | `clean_text`          | `columns`, `ops`, `case`       |
| **Remplir les cellules vides**   | `fill_nulls`          | `columns`, `strategy`, `value` |
| **Ajouter une colonne calculée** | `add_computed_column` | `target`, `expression`         |
| **Filtrer les lignes**           | `filter_rows`         | `combine`, `conditions`        |
| **Dédupliquer les lignes**       | `deduplicate_rows`    | `subset`, `keep`               |
| **Trier les lignes**             | `sort_rows`           | `by`, `descending`             |
| **Réordonner les colonnes**      | `reorder_columns`     | `columns`                      |

Dans les tableaux ci-dessous, *liste* désigne un tableau TOML comme `["a", "b"]`, et *table* une table TOML de paires `clé = valeur` comme `{ "ancien" = "nouveau" }`.

## Renommer les colonnes {#rename-columns}

`rename_columns` — donne un nouveau nom à une ou plusieurs colonnes. Dans l'application : **Mapping des colonnes**, une règle par colonne avec **Colonne source** et **Nouveau nom**.

| Option    | Type                  | Obligatoire | Valeurs autorisées                                | Par défaut |
| :-------- | :-------------------- | :---------: | :------------------------------------------------ | :--------- |
| `mapping` | table (texte → texte) |     Oui     | Au moins une paire `"nom actuel" = "nouveau nom"` | —          |

Chaque nom actuel doit exister. Les étapes suivantes voient les nouveaux noms.

```toml
[[steps]]
action = "rename_columns"
mapping = { "Nom" = "nom", "Prénom" = "prenom" }
```

## Sélectionner les colonnes {#select-columns}

`select_columns` — garde uniquement les colonnes listées, dans l'ordre de la liste, et retire toutes les autres. Dans l'application : **Colonnes à conserver** ; les colonnes désactivées sont exclues du fichier de sortie.

| Option    | Type           | Obligatoire | Valeurs autorisées             | Par défaut |
| :-------- | :------------- | :---------: | :----------------------------- | :--------- |
| `columns` | liste de texte |     Oui     | Au moins une colonne existante | —          |

```toml
[[steps]]
action = "select_columns"
columns = ["id", "nom", "montant"]
```

## Supprimer des colonnes {#drop-columns}

`drop_columns` — retire les colonnes listées et garde toutes les autres. Dans l'application : **Colonnes à supprimer**. À préférer à **Sélectionner les colonnes** quand seules quelques colonnes sont à écarter.

| Option    | Type           | Obligatoire | Valeurs autorisées             | Par défaut |
| :-------- | :------------- | :---------: | :----------------------------- | :--------- |
| `columns` | liste de texte |     Oui     | Au moins une colonne existante | —          |

```toml
[[steps]]
action = "drop_columns"
columns = ["ID interne", "tmp"]
```

## Convertir les types {#cast-types}

`cast_types` — convertit des colonnes vers un autre type de données. Dans l'application : **Conversion de types**, une règle par colonne avec **Colonne** et **Type**.

| Option  | Type                   | Obligatoire | Valeurs autorisées                                            | Par défaut |
| :------ | :--------------------- | :---------: | :------------------------------------------------------------ | :--------- |
| `casts` | table (colonne → type) |     Oui     | Au moins une paire ; le type est l'une des valeurs ci-dessous | —          |

| Valeur de type | Nom dans l'application  | Remarques                                                                                                               |
| :------------- | :---------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| `string`       | **Texte**               | Toute valeur peut devenir du texte.                                                                                     |
| `int`          | **Nombre entier**       | Le texte doit être un nombre entier (`12`, pas `1.5` ni `12 kg`). Les nombres décimaux sont tronqués.                   |
| `float`        | **Nombre décimal**      | Le texte doit utiliser un point comme séparateur décimal (`1.5`, pas `1,5`).                                            |
| `bool`         | **Booléen (Vrai/Faux)** | Fonctionne à partir de nombres (`0` vaut faux, les autres valeurs vrai). Le texte ne peut pas être converti en booléen. |
| `date`         | **Date**                | Le texte doit être de la forme `AAAA-MM-JJ`, par exemple `2024-03-05`.                                                  |
| `datetime`     | **Date et heure**       | Le texte doit être de la forme `AAAA-MM-JJTHH:MM:SS`, par exemple `2024-03-05T10:00:00`.                                |

Une seule valeur non convertible fait échouer l'étape, avec un message du type `conversion from str to i64 failed in column 'amount' for 1 out of 1 values: ["abc"]`. Nettoyez ou remplacez ces valeurs dans des étapes précédentes.

```toml
[[steps]]
action = "cast_types"
casts = { salaire = "float", date_embauche = "date" }
```

## Remplacer les valeurs {#replace-values}

`replace_values` — remplace des valeurs de cellules exactes dans une colonne. Les valeurs non listées restent inchangées. Dans l'application : **Remplacements**, une règle par valeur avec **Colonne**, **Rechercher** et **Remplacer par** ; les règles portant sur la même colonne sont regroupées en une étape par colonne.

| Option    | Type                    | Obligatoire | Valeurs autorisées                              | Par défaut |
| :-------- | :---------------------- | :---------: | :---------------------------------------------- | :--------- |
| `column`  | texte                   |     Oui     | Une colonne existante                           | —          |
| `mapping` | table (valeur → valeur) |     Oui     | Au moins une paire `"recherché" = remplacement` | —          |

- La correspondance porte sur la **cellule entière** et respecte la casse : `"OUI"` ne correspond ni à `"oui"` ni à `"OUI merci"`.
- Les remplacements peuvent être du texte, des nombres ou `true` / `false`. Le remplacement doit convenir au type de la colonne : remplacer un nombre par du texte dans une colonne numérique échoue. Convertissez d'abord la colonne en **Texte**.
- Un remplacement ne peut pas être vide (null) : un fichier de préréglage ne sait pas le stocker, et l'enregistrement d'un tel préréglage échoue avec *holds a value that cannot be saved to TOML*.

```toml
[[steps]]
action = "replace_values"
column = "statut"
mapping = { "A" = "Actif", "I" = "Inactif" }
```

## Nettoyer le texte {#clean-text}

`clean_text` — met en ordre le texte d'une ou plusieurs colonnes. Dans l'application : **Ajouter une action de nettoyage**, puis choisissez **Colonnes cibles**, **Opérations** et **Casse**. Chaque action de nettoyage est enregistrée comme une étape à part.

| Option    | Type           | Obligatoire | Valeurs autorisées                             | Par défaut |
| :-------- | :------------- | :---------: | :--------------------------------------------- | :--------- |
| `columns` | liste de texte |     Oui     | Au moins une colonne **texte** existante       | —          |
| `ops`     | liste de texte |     Non     | Parmi `trim`, `collapse`, `accents`, `special` | `[]`       |
| `case`    | texte          |     Non     | `none`, `lower`, `upper`, `title`              | `none`     |

| Valeur     | Nom dans l'application                | Effet                                                                                              |
| :--------- | :------------------------------------ | :------------------------------------------------------------------------------------------------- |
| `trim`     | **Supprimer les espaces**             | Retire les espaces en début et en fin.                                                             |
| `collapse` | **Réduire les espaces multiples**     | Remplace chaque suite d'espaces, de tabulations ou de sauts de ligne par une seule espace.         |
| `accents`  | **Supprimer les accents**             | `é` devient `e`, `ç` devient `c`. Les caractères sans équivalent en lettre simple sont retirés.    |
| `special`  | **Supprimer les caractères spéciaux** | Ne garde que les lettres, chiffres, tirets bas et espaces ; retire la ponctuation et les symboles. |
| `lower`    | **minuscules**                        | Tout en minuscules.                                                                                |
| `upper`    | **MAJUSCULES**                        | Tout en majuscules.                                                                                |
| `title`    | **Titre**                             | Première lettre de chaque mot en majuscule.                                                        |

Les opérations s'appliquent toujours dans cet ordre, quel que soit l'ordre de la liste : trim, collapse, accents, special, puis la casse. Supprimer les caractères spéciaux peut donc laisser des doubles espaces. Les colonnes doivent contenir du texte : convertissez d'abord une colonne numérique en **Texte**, sinon l'étape échoue avec `expected String`.

```toml
[[steps]]
action = "clean_text"
columns = ["nom", "prenom"]
ops = ["trim", "collapse"]
case = "title"
```

## Remplir les cellules vides {#fill-empty-cells}

`fill_nulls` — remplit les cellules vides d'une ou plusieurs colonnes. Dans l'application : **Colonnes à traiter**, puis **Remplir les cellules vides avec** et, pour une valeur, **Valeur de remplacement**.

| Option     | Type                            |        Obligatoire         | Valeurs autorisées             | Par défaut |
| :--------- | :------------------------------ | :------------------------: | :----------------------------- | :--------- |
| `columns`  | liste de texte                  |            Oui             | Au moins une colonne existante | —          |
| `strategy` | texte                           |            Non             | `value`, `forward`, `backward` | `value`    |
| `value`    | texte, nombre ou `true`/`false` | Quand `strategy = "value"` | N'importe quelle valeur        | —          |

| Stratégie  | Nom dans l'application | Effet                                                            |
| :--------- | :--------------------- | :--------------------------------------------------------------- |
| `value`    | **Une valeur**         | Met `value` dans chaque cellule vide.                            |
| `forward`  | **Valeur au-dessus**   | Recopie la plus proche valeur non vide au-dessus de la cellule.  |
| `backward` | **Valeur en dessous**  | Recopie la plus proche valeur non vide en dessous de la cellule. |

Une cellule est vide quand elle ne contient aucune valeur. Une cellule qui contient des espaces ou un texte vide n'est pas vide. Avec `forward`, les cellules vides tout en haut restent vides ; avec `backward`, celles tout en bas.

La valeur de remplacement saisie dans l'application est du texte. Remplir une colonne numérique avec elle transforme toute la colonne en texte ; dans un fichier de préréglage, écrivez un nombre sans guillemets (`value = 0`) pour garder la colonne numérique.

```toml
[[steps]]
action = "fill_nulls"
columns = ["service"]
strategy = "value"
value = "Inconnu"
```

## Ajouter une colonne calculée {#add-computed-column}

`add_computed_column` — crée une colonne, ou écrase une colonne existante, à partir d'une formule. Dans l'application : **Ajouter une colonne calculée**, avec **Nom de la nouvelle colonne** et une expression construite à partir de **Colonnes**, **Fonctions** et **Séparateurs**. Chaque colonne calculée est enregistrée comme une étape à part, et les suivantes peuvent utiliser les précédentes.

| Option       | Type  | Obligatoire | Valeurs autorisées                                                               | Par défaut |
| :----------- | :---- | :---------: | :------------------------------------------------------------------------------- | :--------- |
| `target`     | texte |     Oui     | Nom de la colonne à créer. Un nom existant est écrasé.                           | —          |
| `expression` | texte |     Oui     | Une formule, consultez [Fonctions des colonnes calculées](computed-functions.md) | —          |

```toml
[[steps]]
action = "add_computed_column"
target = "nom_complet"
expression = 'CONCATENER(prenom, " ", MAJUSCULE(nom))'
```

## Filtrer les lignes {#filter-rows}

`filter_rows` — garde uniquement les lignes qui remplissent des conditions et retire les autres. Dans l'application : **Conserver les lignes correspondant à** **Toutes les conditions** ou **N'importe quelle condition**, puis une règle par condition avec **Colonne**, **Opérateur** et **Valeur**.

| Option       | Type                | Obligatoire | Valeurs autorisées                                       | Par défaut |
| :----------- | :------------------ | :---------: | :------------------------------------------------------- | :--------- |
| `combine`    | texte               |     Non     | `AND` (toutes les conditions), `OR` (n'importe laquelle) | `AND`      |
| `conditions` | liste de conditions |     Oui     | Au moins une condition                                   | —          |

Chaque condition a trois options :

| Option     | Type                            | Obligatoire | Valeurs autorisées                             |
| :--------- | :------------------------------ | :---------: | :--------------------------------------------- |
| `column`   | texte                           |     Oui     | Une colonne existante                          |
| `operator` | texte                           |     Oui     | Consultez le tableau des opérateurs ci-dessous |
| `value`    | texte, nombre ou `true`/`false` |     Oui     | La valeur de comparaison                       |

| Opérateur    | Dans l'application | Garde les lignes dont la cellule…     |
| :----------- | :----------------- | :------------------------------------ |
| `eq`         | **=**              | est égale à la valeur                 |
| `neq`        | **≠**              | diffère de la valeur                  |
| `gt`         | **>**              | est supérieure à la valeur            |
| `gte`        | **≥**              | est supérieure ou égale à la valeur   |
| `lt`         | **<**              | est inférieure à la valeur            |
| `lte`        | **≤**              | est inférieure ou égale à la valeur   |
| `contains`   | **contient**       | contient la valeur comme texte simple |
| `startswith` | **commence par**   | commence par la valeur                |
| `endswith`   | **se termine par** | se termine par la valeur              |

- Les comparaisons de texte respectent la casse. **contient**, **commence par** et **se termine par** traitent la valeur comme du texte simple (`C++` ne correspond qu'à `C++`) et fonctionnent sur n'importe quelle colonne en la lisant comme du texte.
- Sur une colonne numérique, une valeur saisie comme texte est convertie en nombre. Une valeur qui n'est pas un nombre fait échouer l'étape avec *'…' is not a number, but the column holds numbers (…). Enter a numeric value.*
- Sur une colonne vrai/faux, les valeurs `true`, `1` et `yes` (quelle que soit la casse) valent vrai ; tout autre texte vaut faux.
- Les cellules vides ne remplissent jamais une condition : les lignes ayant une cellule vide dans une colonne filtrée sont donc retirées.

```toml
[[steps]]
action = "filter_rows"
combine = "AND"

[[steps.conditions]]
column = "statut"
operator = "eq"
value = "Actif"

[[steps.conditions]]
column = "salaire"
operator = "gte"
value = 30000
```

## Dédupliquer les lignes {#deduplicate-rows}

`deduplicate_rows` — retire les lignes en double. Deux lignes sont des doublons quand toutes les colonnes clés correspondent. Dans l'application : **Clés de déduplication** et **En cas de doublon, conserver**.

| Option   | Type           | Obligatoire | Valeurs autorisées      | Par défaut                          |
| :------- | :------------- | :---------: | :---------------------- | :---------------------------------- |
| `subset` | liste de texte |     Non     | Des colonnes existantes | `[]` (comparer toutes les colonnes) |
| `keep`   | texte          |     Non     | `first`, `last`, `none` | `first`                             |

| Valeur  | Dans l'application     | Effet                                                               |
| :------ | :--------------------- | :------------------------------------------------------------------ |
| `first` | **La première ligne**  | Garde la première ligne de chaque groupe de doublons.               |
| `last`  | **La dernière ligne**  | Garde la dernière ligne de chaque groupe de doublons.               |
| `none`  | *(fichier uniquement)* | Retire toutes les lignes qui ont un doublon, sans en garder aucune. |

L'ordre des lignes restantes n'est pas garanti. Ajoutez une étape **Trier les lignes** si l'ordre compte.

```toml
[[steps]]
action = "deduplicate_rows"
subset = ["email"]
keep = "first"
```

## Trier les lignes {#sort-rows}

`sort_rows` — ordonne les lignes par une ou plusieurs colonnes. Dans l'application : **Clés de tri**, une règle par colonne avec **Colonne** et **Direction** (**Croissant** ou **Décroissant**). Les clés s'appliquent de haut en bas : la première est le tri principal.

| Option       | Type                                    | Obligatoire | Valeurs autorisées                                                   | Par défaut |
| :----------- | :-------------------------------------- | :---------: | :------------------------------------------------------------------- | :--------- |
| `by`         | liste de texte                          |     Oui     | Au moins une colonne existante                                       | —          |
| `descending` | `true`/`false`, ou une liste de ceux-ci |     Non     | Une valeur pour toutes les clés, ou une par clé dans l'ordre de `by` | `false`    |

Quand `descending` est une liste, elle doit avoir exactement autant d'entrées que `by`, sinon le préréglage est refusé avec *sort_rows descending list length must match 'by' length*.

```toml
[[steps]]
action = "sort_rows"
by = ["service", "salaire"]
descending = [false, true]
```

## Réordonner les colonnes {#reorder-columns}

`reorder_columns` — place les colonnes listées en premier, dans l'ordre de la liste. Dans l'application : **Ordre des colonnes**, où vous faites glisser les colonnes à leur place.

| Option    | Type           | Obligatoire | Valeurs autorisées             | Par défaut |
| :-------- | :------------- | :---------: | :----------------------------- | :--------- |
| `columns` | liste de texte |     Oui     | Au moins une colonne existante | —          |

Les colonnes absentes de la liste sont conservées et placées après les colonnes listées, dans leur ordre actuel.

```toml
[[steps]]
action = "reorder_columns"
columns = ["service", "nom_complet"]
```
