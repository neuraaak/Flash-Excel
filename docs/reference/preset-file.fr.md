# Fichier de préréglage

Un préréglage est un fichier texte au format [TOML](https://toml.io/fr/), enregistré avec l'extension `.toml` et encodé en UTF-8. La page **Préréglages** écrit ces fichiers pour vous ; cette page décrit leur format, pour les lire, les partager ou en écrire un à la main. Pour ce qu'est un préréglage, consultez [Préréglages](../concepts/presets.md).

Les clés et les noms d'actions du fichier sont en anglais, quelle que soit la langue de l'interface.

## Structure {#structure}

Un fichier de préréglage contient une table `[meta]` suivie d'un nombre quelconque de tables `[[steps]]` :

```toml
[meta]
name = "Mon préréglage"

[[steps]]
action = "drop_columns"
columns = ["tmp"]

[[steps]]
action = "sort_rows"
by = ["date"]
```

Les étapes s'exécutent dans l'ordre où elles apparaissent dans le fichier. Un préréglage sans étape est valide : il recopie les données sans changement dans le format de sortie.

## La table `[meta]` {#the-meta-table}

| Clé                 | Type             | Obligatoire | Par défaut     | Description                                                                                                                                                                           |
| :------------------ | :--------------- | :---------: | :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`              | texte            |     Oui     | —              | Nom affiché dans les listes de préréglages.                                                                                                                                           |
| `description`       | texte            |     Non     | `""`           | Description libre, pour vos propres notes. L'application ne l'affiche pas.                                                                                                            |
| `csv_separator`     | texte            |     Non     | *(absent)*     | Séparateur de colonnes utilisé pour **lire** les fichiers sources CSV, par exemple `";"`, `","`, `"\t"` ou <code>"&#124;"</code>. Absent, Flash-Excel le détecte à partir du fichier. |
| `csv_encoding`      | texte            |     Non     | `"utf8-lossy"` | Encodage utilisé pour **lire** les fichiers sources CSV. Voir ci-dessous.                                                                                                             |
| `csv_decimal_comma` | `true` / `false` |     Non     | `false`        | Lire `1,5` comme le nombre 1,5 dans les fichiers sources CSV. À activer seulement pour les fichiers qui utilisent une virgule décimale.                                               |
| `source_columns`    | liste de texte   |     Non     | `[]`           | Colonnes du fichier modèle. Écrit par l'application.                                                                                                                                  |
| `source_types`      | table            |     Non     | `{}`           | Types des colonnes du fichier modèle. Écrit par l'application.                                                                                                                        |
| `source_file`       | texte            |     Non     | `""`           | Nom du fichier modèle. Écrit par l'application.                                                                                                                                       |

Les trois clés `csv_*` ne concernent que la lecture des fichiers **sources** CSV. Elles n'ont aucun effet sur les fichiers Excel, ni sur l'écriture des fichiers de sortie : le format des CSV produits vient des [Paramètres](settings.md#csv-output).

Les trois clés `source_*` permettent à l'éditeur d'afficher les colonnes sans recharger le fichier modèle. Laissez-les telles que l'application les a écrites, ou omettez-les.

### Valeurs de `csv_encoding` {#csv_encoding-values}

| Valeur         | À utiliser pour                                                                                                                                                                                                     |
| :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `"utf8-lossy"` | Par défaut. Fichiers UTF-8. Les octets qui ne sont pas de l'UTF-8 valide sont remplacés par `�` au lieu d'arrêter l'exécution.                                                                                      |
| `"utf8"`       | Fichiers UTF-8, avec échec *invalid utf-8 sequence* au moindre octet invalide.                                                                                                                                      |
| `"cp1252"`     | Fichiers enregistrés par Excel en *CSV (séparateur : point-virgule)* ou *CSV (délimité par des virgules)* sur un Windows d'Europe occidentale : les lettres accentuées sont alors lues correctement au lieu de `�`. |
| `"latin-1"`    | Fichiers encodés en ISO-8859-1.                                                                                                                                                                                     |

D'autres noms d'encodage standard, comme `"utf-16"`, sont aussi acceptés.

!!! note "Préréglages enregistrés avant la version 1.4.0"
    Les préréglages enregistrés par les versions antérieures à 1.4.0 contiennent `csv_separator = ";"`, qui impose le point-virgule. Supprimez cette ligne pour laisser Flash-Excel détecter le séparateur.

!!! warning "Enregistrer depuis la page Préréglages"
    Sélectionner **Enregistrer** sur la page **Préréglages** réécrit `[meta]` avec uniquement le nom et les informations du modèle : `description` et les trois clés `csv_*` reviennent à leurs valeurs par défaut. Ajoutez-les de nouveau à la main après l'enregistrement, ou tenez ces préréglages à l'écart de l'éditeur.

## Les tables `[[steps]]` {#the-steps-tables}

Chaque table `[[steps]]` est une étape. Sa clé `action` indique de quel type d'étape il s'agit ; les autres clés sont les options de cette étape.

| `action`              | Options                        |
| :-------------------- | :----------------------------- |
| `rename_columns`      | `mapping`                      |
| `select_columns`      | `columns`                      |
| `drop_columns`        | `columns`                      |
| `cast_types`          | `casts`                        |
| `replace_values`      | `column`, `mapping`            |
| `clean_text`          | `columns`, `ops`, `case`       |
| `fill_nulls`          | `columns`, `strategy`, `value` |
| `add_computed_column` | `target`, `expression`         |
| `filter_rows`         | `combine`, `conditions`        |
| `deduplicate_rows`    | `subset`, `keep`               |
| `sort_rows`           | `by`, `descending`             |
| `reorder_columns`     | `columns`                      |

Chaque option, ses valeurs autorisées et sa valeur par défaut sont listées dans [Étapes](steps.md).

Les conditions de `filter_rows` s'écrivent sous forme de tables `[[steps.conditions]]` juste après leur étape, ou sous forme de liste en ligne :

```toml
[[steps]]
action = "filter_rows"
combine = "OR"
conditions = [
  { column = "pays", operator = "eq", value = "France" },
  { column = "pays", operator = "eq", value = "Belgique" },
]
```

### Écrire les valeurs {#writing-values}

- Les noms de colonnes qui contiennent des espaces ou des symboles doivent être entre guillemets en tant que clés : `{ "Nom de famille" = "nom" }`.
- Les valeurs texte utilisent des guillemets doubles. Pour une expression qui contient elle-même des guillemets doubles, entourez-la de guillemets simples, que TOML lit littéralement : `expression = 'CONCATENER(prenom, " ", nom)'`.
- Les nombres et les booléens n'ont pas de guillemets : `value = 30000`, `descending = true`. Un nombre entre guillemets est du texte, et le séparateur décimal est toujours le point (`1.5`).
- TOML n'a pas de valeur vide (null). Un préréglage ne peut pas remplacer une valeur par une cellule vide.

## Exemple complet {#complete-example}

Ce préréglage lit un export RH, le nettoie et garde les salariés actifs gagnant au moins 30 000. Il est valide tel quel : il se charge sans erreur et s'exécute sur un fichier correspondant.

```toml
[meta]
name = "Rapport RH mensuel"
description = "Nettoyer l'export RH mensuel"
csv_encoding = "utf8-lossy"
csv_decimal_comma = false

[[steps]]
action = "rename_columns"
mapping = { "Nom" = "nom", "Prénom" = "prenom" }

[[steps]]
action = "drop_columns"
columns = ["ID interne"]

[[steps]]
action = "cast_types"
casts = { salaire = "float", date_embauche = "date" }

[[steps]]
action = "replace_values"
column = "statut"
mapping = { "A" = "Actif", "I" = "Inactif" }

[[steps]]
action = "clean_text"
columns = ["nom", "prenom"]
ops = ["trim", "collapse"]
case = "title"

[[steps]]
action = "fill_nulls"
columns = ["service"]
strategy = "value"
value = "Inconnu"

[[steps]]
action = "add_computed_column"
target = "nom_complet"
expression = 'CONCATENER(prenom, " ", MAJUSCULE(nom))'

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

[[steps]]
action = "deduplicate_rows"
subset = ["nom_complet"]
keep = "first"

[[steps]]
action = "sort_rows"
by = ["service", "salaire"]
descending = [false, true]

[[steps]]
action = "select_columns"
columns = ["nom_complet", "service", "salaire", "date_embauche"]

[[steps]]
action = "reorder_columns"
columns = ["service", "nom_complet"]
```

## Erreurs de validation {#validation-errors}

Flash-Excel vérifie un fichier de préréglage quand il le liste ou l'exécute. Un fichier qui ne respecte pas ce format n'est pas exécuté :

- Dans l'application, il apparaît dans la liste des préréglages marqué **illisible** ; survolez la mention pour lire la raison.
- En ligne de commande, l'exécution s'arrête avant de traiter le moindre fichier, avec le code de sortie `1`.

| Message (en anglais)                                              | Signification                                                                                                                                                                                          |
| :---------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *The preset file '…' contains invalid TOML syntax.*               | Le fichier n'est pas du TOML valide : guillemet ou crochet manquant, clé en double. Le détail indique la ligne.                                                                                        |
| *The preset '…' contains configuration errors:* suivi d'une liste | Le TOML est valide, mais une valeur manque ou n'est pas autorisée. Chaque ligne nomme l'emplacement, par exemple `steps > 0 > cast_types > casts > amount` ; les étapes sont numérotées à partir de 0. |
| *Preset file not found: '…'.*                                     | Le chemin indiqué ne mène à aucun fichier.                                                                                                                                                             |

Consultez [Dépannage](../troubleshooting.md#a-preset-is-marked-unreadable).
