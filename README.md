# For developers
 
 My scripts for French typo in Scribus.
 
 The misc directory is just for script tests, for understand Scribus API with Python.
 
 The final script is in typo directory: typoImprimerieNationale.py
 
 * run it in a Scribus document
 * tested with Python 3.10.6 and Scribus 1.5.8
 
 The target is to respect the **French typography** in Scribus as proposed in the *Imprimerie nationale* from France:
 
 __Notation convention__
 
| Notation | Space character definition |
|----------| ------------------|
|   s   | (normal space)|
|   nbs | (non breaking space)|
|   nbts| (non breaking thin space)|
|   ts  | (thin space)|
|   n   | (nothing, i.e all except space)|
 
 
 __Official French typo by Imprimerie nationale française__

 |Signs char|Before/after (prevchar/nextchar) | associated test function|  associated correction function|
 | -----|-------------------|-------------------------|--------------------------------|
 |ss... |  s                |FR_is_a_space            | FR_remove_duplicated_spaces    |
 |.,    |  n/s              |FR_is_a_single           | FR_typo_for_single             |
 |;!?   |  nbts/s           |FR_is_a_double_thin      | FR_typo_for_double_thin        |
 |:     |  nbs/s            |FR_is_a_double           | FR_typo_for_double             |
 |—     |  s/s              |FR_is_a_dash             | FR_typo_for_dash               |
 |«     |  s/nbs            |FR_is_a_langle           | FR_typo_for_rangle             |
 |»     |  nbs/s            |FR_is_a_rangle           | FR_typo_for_langle             |
 |([    |  s/n              |FR_is_a_lparent          | FR_typo_for_oparent            |
 |)]    |  n/s              |FR_is_a_rparent          | FR_typo_for_cparent            |

* NOTE1: 
   - … is n/s at the end and then begining of a sentence
   - is also n/n between bracket for indicating a cut
   -  --> automation is not possible, because depends of the context.

* NOTE2: 
   - french single and double quotes (guillemet APL ', guillemet dactyloographique ",
   - apostrophe culbuté ‘, apostrophe ’, virgule double „, guillemet simple gauche ‹
   - et guillemet simple droite ›) follows obvious rules (s/n for right and n/s for left).
   - but are not fully automated because they depend of the context. People who use it
   - know normaly what they do!
   -  !!! English quotes “ ” should not normaly use
 
 The script is full documented inside and is surely a good basement for general typo script for other languages. The part of French spec is isolated and it is easy to propose other rules for other languages.
 
 I add a test Scribus document for validating/testing this script. The debug mode in console shows the different parts/steps of the script. You can use the misc scripts for playing with a minimal set of rules, because the main script is a bit long. The document is test-typo.sla.

# Pour les utilisateurs francophones

Ce répertoire contient des scripts pour la mise en forme typographique respectant les recommandations de l'Imprimerie nationale de France. Vous trouverez ces recommendations dans le livre *Lexique des règles typographiques en usage à l'Imprimerie nationale* (Édition Massin, ISBN 978-2-74336-0482-9 pour la dernière édition en cours, celle de 2002). 

Le seul script utile est celui contenu dans le répertoire typo appelé typoImprimerieNationale.py.

Vous devez le charger dans Scribus une fois votre document ouvert. Plus d'informations dans le répertoire ad hoc.

Ce scipt a été testé avec Python 3.10.6 et Scribus 1.5.8.

La documentation interne du script est en anglais.
