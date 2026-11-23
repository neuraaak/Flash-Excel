# Dépannage

Chaque entrée part de ce que vous voyez. Les messages d'erreur apparaissent dans la **Console** de la page **Traitement**, dans un message en bas de la fenêtre, ou en ligne de commande.

Les messages de l'interface sont traduits ; les messages d'erreur du moteur de transformation, de la ligne de commande et du journal restent en anglais. Chaque entrée les cite tels qu'ils s'affichent.

!!! tip "Où trouver plus de détails"
    Chaque exécution, erreur et vérification de mise à jour est enregistrée dans le fichier journal `%LOCALAPPDATA%\flash-excel\logs\flash-excel.log`. Collez ce chemin dans la barre d'adresse de l'Explorateur de fichiers pour l'ouvrir. Consultez [Emplacements des données](reference/data-locations.md#logs).

## Unsupported format: 'xls' {#unsupported-format-xls}

**Symptôme** — Une exécution sur un fichier `.xls` ou `.xlsm` échoue avec *Unsupported format: 'xls'. Expected 'xlsx', 'csv', or 'parquet'.* (ou `'xlsm'`), une fois les étapes exécutées.

**Cause** — **Format** est réglé sur **Même que la source**. Flash-Excel lit les fichiers `.xls` et `.xlsm` mais ne sait pas les écrire.

**Solution**

1. Sur la page **Traitement**, sous **Sortie**, réglez **Format** sur **.xlsx (Excel)**.
2. Sélectionnez de nouveau **Lancer le preset**.

En ligne de commande, ajoutez `--format xlsx`. Consultez [Formats de fichier](reference/file-formats.md).

## Format de fichier non pris en charge {#unsupported-file-format}

**Symptôme** — Charger un fichier affiche *Erreur de fichier :* suivi de *Unsupported file format. Allowed: .xlsx, .xls, .xlsm, .csv*, ou un fichier déposé n'est pas ajouté à la file.

**Cause** — Le fichier a une autre extension, par exemple `.txt`, `.ods` ou `.xlsb`.

**Solution** — Ouvrez le fichier dans Excel et enregistrez-le en `.xlsx` ou `.csv`, puis chargez cette copie.

## Excel file contains no readable sheets {#excel-file-contains-no-readable-sheets}

**Symptôme** — Une exécution ou un aperçu échoue avec *Excel file contains no readable sheets.*

**Cause** — Le classeur n'a aucune feuille lisible par Flash-Excel, ou le fichier est endommagé.

**Solution** — Ouvrez le classeur dans Excel, vérifiez que sa **première** feuille contient les données, et enregistrez-le de nouveau en `.xlsx`. Flash-Excel ne lit que la première feuille.

## Une source CSV se charge en une seule colonne {#csv-source-single-column}

**Symptôme** — Le modèle affiche une seule colonne dont le nom contient toute la ligne d'en-tête, comme `nom,age,ville`. Les exécutions échouent ensuite avec *"…" not found* ou *unable to find column*.

**Cause** — Le CSV est lu avec le mauvais séparateur. Soit le préréglage en impose un avec `csv_separator` — les préréglages enregistrés avant la version 1.4.0 contiennent `csv_separator = ";"` —, soit le séparateur n'a pas pu être détecté et `;` a été utilisé.

**Solution**

1. Ouvrez le fichier de préréglage (`Documents\flash-excel\presets\<nom>.toml`) dans un éditeur de texte comme le Bloc-notes.
2. Dans `[meta]`, supprimez la ligne `csv_separator` pour laisser Flash-Excel détecter le séparateur, ou réglez-la sur le séparateur du fichier, par exemple `csv_separator = ","`.
3. Enregistrez le fichier et relancez.

Consultez [Fichier de préréglage](reference/preset-file.md#the-meta-table).

## Les lettres accentuées s'affichent en � dans une source CSV {#accented-letters-in-csv-source}

**Symptôme** — Après le chargement ou le traitement d'un fichier CSV, des lettres comme `é` ou `ç` s'affichent en `�`.

**Cause** — Le fichier n'est pas encodé en UTF-8. Les formats *CSV (séparateur : point-virgule)* et *CSV (délimité par des virgules)* d'Excel enregistrent dans l'encodage Windows (Windows-1252 sur les systèmes d'Europe occidentale), alors que Flash-Excel lit l'UTF-8 par défaut.

**Solution** — Dans le fichier de préréglage, ajoutez `csv_encoding = "cp1252"` à `[meta]`, puis relancez. Vous pouvez aussi enregistrer le fichier depuis Excel en *CSV UTF-8 (délimité par des virgules)*. Consultez [Fichier de préréglage](reference/preset-file.md#csv_encoding-values).

## Les nombres décimaux restent du texte dans une source CSV {#decimal-numbers-stay-text}

**Symptôme** — Une colonne de nombres comme `1,5` est traitée comme du texte : le tri est alphabétique, et **Convertir les types** vers **Nombre décimal** échoue avec *conversion from `str` to `f64` failed*.

**Cause** — Le fichier utilise une virgule comme séparateur décimal. Flash-Excel lit le point comme séparateur décimal, sauf indication contraire.

**Solution** — Dans le fichier de préréglage, ajoutez `csv_decimal_comma = true` à `[meta]`. Consultez [Fichier de préréglage](reference/preset-file.md#the-meta-table).

## Un CSV produit s'ouvre en une seule colonne dans Excel {#output-csv-single-column}

**Symptôme** — Un double-clic sur un fichier `.csv` produit ouvre Excel avec toutes les valeurs dans la colonne A.

**Cause** — Le séparateur ou le séparateur décimal du fichier ne correspond pas aux paramètres régionaux du PC qui l'ouvre. Cela arrive quand **Sortie CSV** est forcé sur une valeur, ou quand le fichier est ouvert sur un PC aux paramètres régionaux différents de celui qui l'a écrit.

**Solution**

1. Sélectionnez **Paramètres** dans la barre latérale.
2. Sous **Sortie CSV**, réglez **Séparateur de colonnes** et **Séparateur décimal** sur **Auto** pour correspondre à ce PC, ou sur les valeurs attendues par le PC destinataire.
3. Relancez le préréglage.

Pour ouvrir un fichier existant sans relancer, utilisez **Données** › **À partir d'un fichier texte/CSV** dans Excel et choisissez le séparateur. Consultez [Régler le format de sortie CSV](tasks/settings/set-the-csv-output-format.md).

## Les lettres accentuées sont incorrectes dans un CSV produit ouvert dans Excel {#accented-letters-in-output-csv}

**Symptôme** — Un `.csv` produit, ouvert par double-clic dans Excel, affiche `Ã©` au lieu de `é`.

**Cause** — Les fichiers CSV produits sont écrits en UTF-8. Au double-clic, Excel peut les lire avec l'encodage Windows à la place.

**Solution** — Choisissez **.xlsx (Excel)** comme **Format** de sortie quand le fichier est destiné à Excel. Pour ouvrir le CSV tel quel, utilisez **Données** › **À partir d'un fichier texte/CSV** dans Excel et choisissez *65001 : Unicode (UTF-8)* comme origine du fichier.

## Permission denied, ou le fichier est utilisé par un autre processus {#file-in-use}

**Symptôme** — Un fichier échoue avec un message comme *Permission denied* ou *being used by another process*. Son statut devient **Erreur**.

**Cause** — Le fichier de sortie (ou, plus rarement, le fichier source) est ouvert dans Excel ou un autre programme, qui le verrouille.

**Solution** — Fermez le fichier dans Excel, puis relancez. Avec **Passer le fichier**, les autres fichiers de l'exécution sont traités quand même ; seul le fichier verrouillé doit être relancé.

## Une étape ne trouve pas une colonne {#column-not-found}

**Symptôme** — Une étape échoue avec *"Montant" not found* ou *unable to find column "Montant"; valid columns: [...]*.

**Cause** — L'étape nomme une colonne qui n'existe pas à ce stade : le fichier source a d'autres noms de colonnes que le modèle, le nom diffère par la casse ou des espaces, ou une étape précédente a renommé ou retiré la colonne.

**Solution**

1. Comparez les noms de colonnes du fichier source avec la liste des colonnes valides du message.
2. Sur la page **Préréglages**, chargez le fichier actuel sous **Charger le modèle Excel**. Si la fenêtre **Structure de colonnes modifiée** s'ouvre, sélectionnez **Charger et nettoyer les références** pour retirer les colonnes absentes des étapes, puis corrigez les étapes qui en ont besoin.
3. Sélectionnez **Enregistrer**, puis relancez.

Consultez [Étapes et ordre](concepts/steps-and-order.md).

## Une colonne calculée indique qu'un nom n'est pas disponible {#is-not-available-use-column-names-or-catalog-functions}

**Symptôme** — L'étape **Ajouter une colonne calculée** échoue avec *Expression not allowed: '…' is not available. Use column names or catalog functions.*

**Cause** — L'expression contient un nom qui n'est ni une colonne à cette étape ni une fonction. Raisons courantes : une faute de frappe, une fonction écrite en minuscules (`si` au lieu de `SI`), ou une colonne renommée ou retirée par une étape précédente.

**Solution** — Écrivez les noms de fonctions en majuscules, mettez entre crochets les noms de colonnes qui contiennent des espaces ou des symboles (`[Prix unitaire]`), et utilisez le nom de la colonne tel qu'il est à cette étape. Sélectionner la colonne sous **Colonnes** dans l'éditeur insère la bonne forme. Consultez [Fonctions des colonnes calculées](reference/computed-functions.md).

## Syntaxe invalide dans une colonne calculée {#invalid-syntax}

**Symptôme** — L'étape **Ajouter une colonne calculée** échoue avec *Invalid syntax:* suivi de détails.

**Cause** — Une parenthèse ou un guillemet n'est pas fermé, une virgule manque entre les arguments, `=` est utilisé au lieu de `==`, ou un nom entre crochets comme `[Prix unitaire]` ne correspond à aucune colonne.

**Solution** — Vérifiez la ponctuation de l'expression et l'orthographe exacte des noms de colonnes entre crochets. Consultez [Fonctions des colonnes calculées](reference/computed-functions.md#operators).

## The truth value of an Expr is ambiguous {#truth-value-ambiguous}

**Symptôme** — L'étape **Ajouter une colonne calculée** échoue avec *Evaluation error: the truth value of an Expr is ambiguous*.

**Cause** — L'expression combine des conditions avec `and`, `or`, `not` ou `in`.

**Solution** — Utilisez `&` pour *et*, `|` pour *ou* et `~` pour *non*, avec chaque comparaison entre parenthèses : `SI((age >= 18) & (age < 65), "actif", "autre")`.

## '…' is not a number, but the column holds numbers {#not-a-number}

**Symptôme** — **Filtrer les lignes** échoue avec *'18 ans' is not a number, but the column holds numbers (Int64). Enter a numeric value.*

**Cause** — Une condition sur une colonne numérique a une valeur qui n'est pas un nombre.

**Solution** — Sur la page **Préréglages**, ouvrez **Filtrer les lignes** et saisissez uniquement le nombre dans **Valeur**, avec un point comme séparateur décimal (`18`, `1.5`). Sélectionnez ensuite **Enregistrer**.

## Conversion from str to … failed {#conversion-failed}

**Symptôme** — **Convertir les types** échoue avec *conversion from `str` to `i64` failed in column 'montant' for 3 out of 1250 values: [...]*. Le type peut aussi être `f64`, `date` ou `datetime[μs]`.

**Cause** — Certaines valeurs ne peuvent pas être converties : du texte dans une colonne de nombres, une virgule comme séparateur décimal, un nombre décimal converti en **Nombre entier**, ou une date qui n'est pas au format `AAAA-MM-JJ`. Le message liste les valeurs en échec.

**Solution** — Nettoyez ces valeurs dans les étapes avant **Convertir les types**, par exemple avec **Remplacer les valeurs** ou **Nettoyer le texte**, ou convertissez vers un autre type. Consultez [Étapes › Convertir les types](reference/steps.md#cast-types).

## Expected String dans Nettoyer le texte ou une fonction texte {#expected-string}

**Symptôme** — **Nettoyer le texte**, ou une fonction texte comme `MAJUSCULE`, échoue avec *invalid series dtype: expected `String`, got `i64`*.

**Cause** — La colonne contient des nombres ou des dates, pas du texte.

**Solution** — Ajoutez la colonne à **Convertir les types** avec le type **Texte**. Convertir les types s'exécute avant Nettoyer le texte et les colonnes calculées.

## La sortie a moins de lignes que prévu {#fewer-rows}

**Symptôme** — La sortie, ou l'aperçu, a moins de lignes que prévu, voire aucune.

**Cause** — **Filtrer les lignes** retire les lignes dont les cellules sont vides dans une colonne filtrée, et les comparaisons de texte respectent la casse (`Actif` ne correspond pas à `actif`). **Dédupliquer les lignes** retire aussi des lignes. L'aperçu ne travaille que sur les 100 premières lignes : il peut donc afficher *Aucune ligne ne reste dans cet échantillon après transformation* alors que le fichier complet contient des lignes correspondantes.

**Solution** — Vérifiez la casse et l'orthographe des valeurs de filtre ; nettoyez d'abord le texte avec **Nettoyer le texte** si besoin. Lancez le préréglage sur le fichier complet pour voir le résultat réel.

## Un préréglage est marqué illisible {#a-preset-is-marked-unreadable}

**Symptôme** — Un préréglage apparaît dans la liste avec la mention **illisible**, et ne peut être ni ouvert ni lancé.

**Cause** — Son fichier n'est pas un préréglage valide : syntaxe TOML invalide, ou valeur manquante ou incorrecte. Cela suit en général une modification à la main. Survolez la mention pour lire la raison exacte, comme *contains invalid TOML syntax* ou *contains configuration errors*.

**Solution**

1. Ouvrez le fichier dans `Documents\flash-excel\presets` avec un éditeur de texte.
2. Corrigez la ligne nommée dans la raison. Dans le message, les étapes sont numérotées à partir de 0.
3. Enregistrez le fichier. Le préréglage redevient lisible au prochain chargement de la liste.

Consultez [Fichier de préréglage](reference/preset-file.md#validation-errors).

## Préréglage enregistré, mais des étapes ont été refusées {#steps-refused}

**Symptôme** — **Enregistrer** affiche *Préréglage enregistré, mais ces étapes ont été refusées et sont absentes du fichier :* suivi de noms d'étapes.

**Cause** — Ces étapes étaient incomplètes ou avaient des valeurs qu'un préréglage n'accepte pas, par exemple une étape sans colonne sélectionnée. Le préréglage a été enregistré sans elles.

**Solution** — Ouvrez chaque étape nommée, complétez-la ou videz-la, puis sélectionnez de nouveau **Enregistrer**.

## Un préréglage utilise déjà le fichier {#preset-file-name-taken}

**Symptôme** — **Enregistrer** échoue avec *A preset already uses the file '…'. Choose another name.*

**Cause** — Deux noms de préréglage qui ne diffèrent que par la ponctuation ou la casse donnent le même nom de fichier (`Rapport ventes !` et `rapport ventes` donnent tous deux `rapport_ventes.toml`).

**Solution** — Donnez au préréglage un nom qui diffère d'au moins une lettre ou un chiffre.

## Le préréglage contient une valeur qui ne peut pas être enregistrée en TOML {#value-cannot-be-saved}

**Symptôme** — **Enregistrer** échoue avec *The preset '…' holds a value that cannot be saved to TOML (a null inside a step).*

**Cause** — Une étape contient une valeur vide qu'un fichier de préréglage ne sait pas stocker, typiquement une règle **Remplacer les valeurs** dont **Remplacer par** est vide.

**Solution** — Donnez une valeur de remplacement à la règle, ou retirez-la, puis sélectionnez de nouveau **Enregistrer**.

## Les modifications d'un préréglage ne sont pas prises en compte {#changes-not-used}

**Symptôme** — **Aperçu** ou **Lancer le preset** se comporte comme si vos dernières modifications des étapes n'existaient pas.

**Cause** — Les exécutions et les aperçus utilisent le préréglage tel qu'il est enregistré sur le disque.

**Solution** — Sur la page **Préréglages**, sélectionnez **Enregistrer**, puis revenez à **Traitement** et sélectionnez de nouveau le préréglage.

## Des préréglages partagés manquent, ou ne peuvent être ni enregistrés ni exportés {#shared-presets}

**Symptôme** — Les préréglages d'un dossier partagé n'apparaissent pas dans la liste ; ou, pour un préréglage partagé, **Enregistrer** et **Supprimer** sont désactivés et **Exporter** échoue avec *Preset file is outside the presets directory*.

**Cause** — Un dossier partagé inaccessible (lecteur réseau déconnecté, dossier déplacé) est ignoré ; le journal enregistre *preset source unavailable*. Les préréglages partagés sont en lecture seule par conception et ne peuvent pas être exportés depuis Flash-Excel.

**Solution** — Vérifiez que le dossier s'ouvre dans l'Explorateur de fichiers, et corrigez son **Chemin du dossier** sous **Paramètres** › **Sources de préréglages en lecture seule** si besoin. Pour obtenir votre propre copie modifiable d'un préréglage partagé, copiez son fichier `.toml` dans `Documents\flash-excel\presets` avec l'Explorateur de fichiers. Consultez [Utiliser des dossiers de préréglages partagés](tasks/presets/use-shared-preset-folders.md).

## Une exécution est déjà en cours {#run-in-progress}

**Symptôme** — Lancer une exécution affiche *A run is already in progress*.

**Cause** — Une exécution précédente n'est pas encore terminée.

**Solution** — Attendez sa fin, ou arrêtez-la avec le bouton carré à côté de **Lancer le preset**. Consultez [Arrêter une exécution](tasks/run/stop-a-run.md).

## La tâche planifiée ne s'est pas exécutée {#scheduled-task-did-not-run}

**Symptôme** — Aucun fichier de sortie n'a été écrit à l'heure prévue.

**Cause** — Causes possibles :

- Les tâches créées par Flash-Excel ne s'exécutent que lorsque votre session Windows est ouverte. Elles ne s'exécutent pas quand vous êtes déconnecté ou que le PC est éteint, et une heure manquée n'est pas rattrapée.
- Un préréglage ou un fichier source a été déplacé, renommé ou supprimé après la création de la tâche : la tâche utilise les chemins exacts avec lesquels elle a été créée.
- Un fichier a échoué : l'exécution a continué avec les autres fichiers, et la tâche s'est terminée avec le résultat `0x1`.

**Solution**

1. Ouvrez le **Planificateur de tâches**, puis **Bibliothèque du Planificateur de tâches** › **Flash-Excel**, et sélectionnez la tâche. Vérifiez **Heure de la dernière exécution** et **Résultat de la dernière exécution**.
2. Ouvrez le fichier journal et cherchez à cette heure les lignes qui se terminent par *FAILED*.
3. Si des chemins ont changé, recréez la tâche depuis **Configurer une exécution** sur la page **Traitement**.

Consultez [Planifier un préréglage](tasks/automate/schedule-a-preset.md).

## La commande de planification est trop longue {#command-too-long}

**Symptôme** — **Avancé : copier la commande de planification** avertit que *Windows ne peut pas créer cette tâche avec une commande /tr collée car elle dépasse 261 caractères*.

**Cause** — Avec beaucoup de fichiers ou des chemins longs, la commande dépasse la longueur que Windows accepte pour une commande `schtasks` collée.

**Solution** — Sélectionnez plutôt **Ajouter au planificateur** : Flash-Excel enregistre alors lui-même la configuration complète, sans cette limite.

## Scheduling commands cannot contain %, !, quotes or newlines {#scheduling-forbidden-characters}

**Symptôme** — **Ajouter au planificateur** ou **Créer un lanceur .cmd** échoue avec ce message.

**Cause** — Un chemin, le dossier de sortie ou le modèle de nom contient `%`, `!` ou `"`. Ces caractères changent de sens dans les commandes Windows.

**Solution** — Renommez les fichiers ou dossiers concernés, ou choisissez un autre dossier de sortie ou modèle de nom, puis réessayez.

## Enter a name of 1–200 characters without reserved filename characters {#execution-name-invalid}

**Symptôme** — La création d'une tâche planifiée ou d'un lanceur échoue avec ce message.

**Cause** — **Nom de l'exécution** est vide, trop long, se termine par un point ou une espace, ou contient l'un de `\ / : * ? " < > | % !`.

**Solution** — Saisissez un nom simple, par exemple `Rapport RH mensuel`.

## Start time must use HH:mm {#start-time-invalid}

**Symptôme** — **Ajouter au planificateur** échoue avec *Start time must use HH:mm (00:00–23:59)*.

**Solution** — Saisissez l'**Heure quotidienne (tâche planifiée)** en heures et minutes sur deux chiffres, par exemple `07:30`.

## Aucune sortie dans l'invite de commandes {#no-console-output}

**Symptôme** — Une exécution en ligne de commande n'affiche rien, ou l'invite rend la main avant la fin de l'exécution.

**Cause** — Flash-Excel est un programme fenêtré : il n'écrit dans une console que s'il a été lancé depuis l'une d'elles, et une invite interactive peut ne pas l'attendre.

**Solution** — Lancez la commande depuis un fichier batch `.cmd`, qui l'attend et peut lire `%ERRORLEVEL%`, et consultez le fichier journal pour le résultat de chaque fichier. Consultez [Ligne de commande](reference/command-line.md#console).

## Le lien de mise à jour n'apparaît jamais, ou la mise à jour échoue {#the-update-link-never-appears-or-the-update-fails}

**Symptôme** — Aucun lien **Mettre à jour vers v…** n'apparaît alors qu'une version plus récente existe, ou le sélectionner affiche **Mise à jour…** puis rien ne change.

**Cause** — Le serveur de mise à jour n'a pas pu être joint (pas de connexion internet, proxy ou pare-feu), ou la mise à jour téléchargée n'a pas passé la vérification de signature. Le journal enregistre *update check FAILED* ou *update apply FAILED* avec la raison.

**Solution**

1. Vérifiez votre connexion internet et redémarrez Flash-Excel : la vérification a lieu à chaque démarrage.
2. Si l'échec persiste, téléchargez le dernier `Flash-Excel-<version>-setup.exe` depuis la [page des versions GitHub](https://github.com/neuraaak/Flash-Excel/releases) et lancez-le. Vos préréglages et paramètres sont conservés.

Consultez [Mises à jour automatiques](concepts/automatic-updates.md) et [Mettre à jour Flash-Excel](tasks/update/update-flash-excel.md).

## Toujours bloqué ? {#still-stuck}

Ouvrez une issue sur [GitHub](https://github.com/neuraaak/Flash-Excel/issues) avec le message d'erreur, ce que vous faisiez, et les lignes correspondantes du fichier journal. Retirez-en d'abord toute donnée confidentielle.
