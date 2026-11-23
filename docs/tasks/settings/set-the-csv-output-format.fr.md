# Régler le format de sortie CSV

Choisissez le séparateur de colonnes et le séparateur décimal des fichiers CSV écrits par Flash-Excel, par exemple pour correspondre au programme qui les lit.

## 🔧 Prérequis

- Aucun. Le réglage s'applique à tous les fichiers CSV écrits par Flash-Excel : exécutions depuis la page **Traitement**, tâches planifiées, lanceurs et exécutions en ligne de commande.

## 📝 Étapes

1. Dans la barre latérale, sélectionnez **Paramètres**.
2. Sous **Sortie CSV** › **Séparateur de colonnes**, sélectionnez **Auto**, **Point-virgule ;**, **Virgule ,** ou **Tabulation**.
3. Sous **Séparateur décimal**, sélectionnez **Auto**, **Virgule 1,5** ou **Point 1.5**.
4. Fermez la fenêtre **Paramètres**.

## ✅ Résultat

Les prochains fichiers CSV écrits utilisent le séparateur et le séparateur décimal choisis. Les fichiers écrits auparavant ne changent pas.

**Auto**, la valeur par défaut des deux réglages, suit les paramètres régionaux Windows — ceux qu'Excel lit aussi, donc le fichier s'ouvre en colonnes au double-clic. Choisissez une valeur fixe quand un autre programme, ou un ordinateur aux paramètres régionaux différents, lit les fichiers.

!!! note "Séparateur virgule et décimales à virgule"
    Avec **Virgule ,** comme séparateur, les nombres décimaux sont toujours écrits avec un point, même si **Séparateur décimal** vaut **Virgule 1,5** : une virgule dans les nombres les couperait sur deux colonnes.

## ➡️ Étapes suivantes

- [Lancer un préréglage](../run/run-a-preset.md) avec **Format** réglé sur **.csv (UTF-8)**.
- [Formats de fichier](../../reference/file-formats.md)
