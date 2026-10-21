# Computed column functions

The **Add computed column** step builds a new column from a formula, called an *expression*. The expression is computed for every row. This page lists everything an expression can contain.

Function names are in French, after the French version of Excel (`CONCATENER` for `CONCAT`, `SI` for `IF`). Type them exactly as shown, in upper case.

## Writing an expression

An expression combines column references, literal values, operators and functions:

```text
SI([Unit price] * qty > 1000, "large", "small")
```

The editor helps you build it: selecting a chip under **Columns**, **Functions** or **Separators** appends it to the end of the expression. You still type the commas between arguments and the closing parentheses yourself. Hovering over a function shows its description and an **Example**.

### Column references

| Syntax              | When to use it                                                                                  | Example            |
| :------------------ | :---------------------------------------------------------------------------------------------- | :----------------- |
| `name`              | The column name contains only letters, digits and underscores, and does not start with a digit. | `last_name`        |
| `[Column Name]`     | Any other name: spaces, a leading digit, symbols such as `°`, `€` or `-`.                        | `[Unit price]`     |
| `col("Column Name")`| Same as brackets. Also works when a column has the same name as a function.                      | `col("ABS")`       |

The **Columns** chips add brackets for you when a name needs them. A name in brackets must match an existing column exactly; otherwise the expression is refused with *Invalid syntax*.

A column reference uses the columns as they are at this step: renamed columns go by their new name, and an earlier computed column can be used by a later one.

### Literal values

| Kind    | How to write it                         | Example            |
| :------ | :-------------------------------------- | :----------------- |
| Text    | Between double or single quotes         | `"adult"`, `' - '` |
| Number  | Digits, with a dot as decimal mark      | `18`, `1.2`        |
| Boolean | `True` or `False`                       | `True`             |

An expression must use at least one column or function. A literal on its own, such as `"N/A"` or `0`, is refused with *The expression must return a Polars Expr*. To fill a column with a fixed text, write `CONCATENER("N/A")`.

### Operators

| Operator                         | Meaning                                         | Example                      |
| :------------------------------- | :---------------------------------------------- | :--------------------------- |
| `+` `-` `*` `/`                  | Add, subtract, multiply, divide                 | `[Unit price] * qty`         |
| `//` `%` `**`                    | Whole division, remainder, power                | `qty % 2`                    |
| `-` (in front)                   | Negative value                                  | `-delta`                     |
| `+` between texts                | Joins two texts                                 | `MAJUSCULE(code) + "-FR"`    |
| `==` `!=` `<` `>` `<=` `>=`      | Comparisons; produce true or false              | `age >= 18`                  |
| `&` <code>&#124;</code> `~`                    | And, or, not — to combine comparisons           | `(age >= 18) & (age < 65)`   |
| `( )`                            | Grouping                                        | `(a + b) * 2`                |

- Equality is `==`. A single `=` is refused with *Invalid syntax*.
- Combine conditions with `&` and `|`, and put each comparison in parentheses. The words `and`, `or`, `not` and `in` do not work on columns and fail with *the truth value of an Expr is ambiguous*.
- Dividing by zero gives an infinite value, not an error.

## Functions

| Function       | Category | Signature                                  | Returns                                                                                |
| :------------- | :------- | :----------------------------------------- | :------------------------------------------------------------------------------------- |
| `CONCATENER`   | Text     | `CONCATENER(part1, part2, …, sep="")`      | The parts joined into one text.                                                        |
| `MAJUSCULE`    | Text     | `MAJUSCULE(text)`                          | The text in upper case.                                                                |
| `MINUSCULE`    | Text     | `MINUSCULE(text)`                          | The text in lower case.                                                                |
| `GAUCHE`       | Text     | `GAUCHE(text, n)`                          | The first `n` characters.                                                              |
| `DROITE`       | Text     | `DROITE(text, n)`                          | The last `n` characters.                                                               |
| `NBCAR`        | Text     | `NBCAR(text)`                              | The number of characters.                                                              |
| `SUPPRESPACE`  | Text     | `SUPPRESPACE(text)`                        | The text without leading and trailing whitespace.                                      |
| `ARRONDI`      | Math     | `ARRONDI(number, n=0)`                     | The number rounded to `n` decimal places.                                              |
| `ABS`          | Math     | `ABS(number)`                              | The absolute value.                                                                    |
| `MULTIPLIER`   | Math     | `MULTIPLIER(number, n)`                    | The number multiplied by `n`.                                                          |
| `AJOUTER`      | Math     | `AJOUTER(number1, number2)`                | The sum of the two values.                                                             |
| `ANNEE`        | Date     | `ANNEE(date)`                              | The year.                                                                              |
| `MOIS`         | Date     | `MOIS(date)`                               | The month, from 1 to 12.                                                               |
| `JOUR`         | Date     | `JOUR(date)`                               | The day of the month.                                                                  |
| `AUJOURD_HUI`  | Date     | `AUJOURD_HUI()`                            | Today's date, on the day the preset runs.                                              |
| `SI`           | Logic    | `SI(condition, then, else)`                | `then` where the condition is true, `else` elsewhere.                                  |

Arguments shown as *text*, *number* or *date* accept a column reference or another function call. `n` is a number you type.

### CONCATENER

Joins columns and texts into one text. Number columns are converted to text. The optional `sep` is inserted between every two parts.

```text
CONCATENER(first_name, " ", last_name)      → "Ann Smith"
CONCATENER(year, month, day, sep="-")       → "2024-3-5"
```

If any part is empty for a row, the result is empty for that row. Fill empty cells first with **Fill empty cells**.

### MAJUSCULE

Converts every character to upper case.

```text
MAJUSCULE(last_name)                        → "SMITH"
```

### MINUSCULE

Converts every character to lower case.

```text
MINUSCULE(email)                            → "ann.smith@example.com"
```

### GAUCHE

Returns the first `n` characters. `GAUCHE(code, 0)` returns an empty text.

```text
GAUCHE(code, 3)                             → "FR-" for "FR-1234"
```

### DROITE

Returns the last `n` characters. `DROITE(reference, 0)` returns an empty text.

```text
DROITE(reference, 4)                        → "1234" for "FR-1234"
```

### NBCAR

Returns the number of characters, spaces included.

```text
NBCAR(description)                          → 11 for "Hello world"
```

### SUPPRESPACE

Removes whitespace at the start and end of the text. Spaces inside the text are kept; to collapse them, use the **Clean text** step.

```text
SUPPRESPACE(last_name)                      → "Smith" for "  Smith "
```

### ARRONDI

Rounds to `n` decimal places. Without `n`, rounds to a whole number.

```text
ARRONDI(price, 2)                           → 1.23 for 1.234
ARRONDI(price)                              → 1.0 for 1.234
```

### ABS

Returns the absolute value, always positive or zero.

```text
ABS(delta)                                  → 5 for -5
```

### MULTIPLIER

Multiplies every value by `n`. Same as `price * 1.2`.

```text
MULTIPLIER(price, 1.2)                      → 120 for 100
```

### AJOUTER

Adds two values: two numeric columns, or a column and a number. Same as `base + bonus`.

```text
AJOUTER(base, bonus)                        → 1200 for 1000 and 200
```

### ANNEE

Extracts the year. The column must hold dates or dates and times; cast a text column first with **Cast types**.

```text
ANNEE(birth_date)                           → 1990
```

### MOIS

Extracts the month, from 1 to 12.

```text
MOIS(order_date)                            → 3 for 2024-03-05
```

### JOUR

Extracts the day of the month.

```text
JOUR(delivery_date)                         → 5 for 2024-03-05
```

### AUJOURD_HUI

Returns the date of the day the preset runs. It takes no argument but still needs its parentheses. The editor's chip shows it as `AUJOURD'HUI`; in the expression, write `AUJOURD_HUI()` with an underscore.

```text
AUJOURD_HUI()                               → 2026-10-21
```

### SI

Returns `then` where the condition is true and `else` everywhere else. `then` and `else` can be columns, texts or numbers. The condition uses the comparison operators `==`, `!=`, `<`, `>`, `<=`, `>=`, combined if needed with `&`, `|` and `~`.

```text
SI(age >= 18, "adult", "minor")
SI((qty > 1) & (qty < 10), "batch", "single")
SI(status == "Active", salary, 0)
```

## Errors

When an expression cannot be computed, the step fails. The **Console** shows one of these messages:

| Message                                     | Cause                                                                                     | Fix                                                                                 |
| :------------------------------------------ | :---------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------- |
| `Invalid syntax:`                           | Unbalanced parentheses or quotes, a missing comma, `=` instead of `==`, or `[Name]` that matches no column. | Check the punctuation; check the bracketed column name.                    |
| `Expression not allowed: '…' is not available. Use column names or catalog functions.` | A name that is neither a column at this step nor a function: a typo, a wrong case, or a column renamed or removed earlier. | Fix the name, or use `[Column Name]`. Function names are upper case.                |
| `Expression not allowed:` (other text)      | The expression uses a construct that is not allowed.                                      | Use only the functions and operators on this page.                                  |
| `Evaluation error:`                         | A function is missing an argument (*missing 1 required positional argument*), or `and`/`or`/`in` was used instead of `&`/<code>&#124;</code>. | Check the function's signature on this page.                       |
| `invalid series dtype: expected String`, `… operation not supported for dtype …` | A function received a column of the wrong type: `MAJUSCULE` on a number, `ANNEE` on text, `ABS` on text. | Convert the column first with **Cast types**.                                       |
| `The expression must return a Polars Expr`  | The expression is a plain value, with no column or function.                              | Wrap the value, for example `CONCATENER("N/A")`.                                    |

See also [Troubleshooting](../troubleshooting.md#is-not-available-use-column-names-or-catalog-functions).
