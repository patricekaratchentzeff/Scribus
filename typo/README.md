# For all users

This script is aimed for French users, so the documentation and interface are for the moment in French. If you have such this need, you surely speak or understand French language.

# Documentation

Ce script vous permet de forcer la typographie de votre texte selon les recommandations de l'Imprimerie nationale, donc celle en usage en France.

Vous trouverez ces recommandations dans l'ouvrage *Lexique des règles typographiques en usage à l'Imprimerie nationale* (Édition Massin, ISBN 978-2-74336-0482-9 pour la dernière édition en cours, celle de 2002).

Ce script s'occupe donc uniquement **d'espacement**. Si vous avez des soucis avec l'usage de caractères non français, comme des guillemets américains, vous devez auparavant remettre au carré votre texte selon les bons usages. Il existe d'autres scripts à cet usage, mais sachez qu'ils ne pourront jamais être exhaustif, étant donné l'impossibilité d'automatiser l'imbrication des guillemets. Un apprentissage *ad hoc* et une passe manuelle est sans doute la seule bonne solution pour obtenir un résultat professionnel.

En revanche, la typographie s'automatise parfaitement, au moins pour les caractères d'usage courant :

.,;:!?«»{}()[]

qui ont chacun leur règle propre et qui est pénible à respecter avec un clavier classique et/ou un logiciel de traitement de texte.

Notez toutefois que pour les caractères guillemet APL ', guillemet dactyloographique ", apostrophe culbuté ‘, apostrophe ’, virgule double „, guillemet simple gauche et guillemet simple droite, la règle est simple et n'est pas testé dans ce script. Elle est triviale à ajouter si la demande s'en faisait sentir.

La typographie des points de suspension dépend du contexte et n'est donc pas automatisable : vous devez donc connaître la règle.

> … n'a pas d'espace avant, et contient une espace typographique à la fin et au début d'une phrase

> …  est entouré de deux espaces typographiques entre parenthèses pour indiquer une coupe

Pour rappel, en typographie, le mot espace est féminin.

Ce script peut s'appliquer sur un cadre de texte unique ou bien sur **tous** les cadres de texte, **à l'exception** des cadres de texte inclut dans les gabarits. Vous devez alors appliquer ce script au niveau des gabarit pour les valider.

ATTENTION, pour les textes longs comme les romans, ce script peut tourner longtemps. Compter environ 6 à 7 min par 100 000 signes sur un microprocesseur de 2015. Il y a une barre de progression dans Scribus en bas à droite qui indique le pourcentage de travail effectué.


# Règle typographique en usage à l'Imprimerie nationale

| Signes | Règles |
| -----|-------------------|
 |espaces consécutives |  Une seule espace               |
 |.,    |  Absence d'espace/espace typographique             | 
 |;!?   |  Espace typograhique fine insécable/espace typographique          | 
 |:     |  Espace typograhique insécable/espace typographique           | 
 |—     |  Espace typographique/espace typographique             | 
 |«     |  Espace typographique/Espace typograhique insécable          | 
 |»     |  Espace typograhique insécable/espace typographique           | 
 |([    |  espace typographique/absence d'espace              |
 |)]    |  Absence d'espace/espace typographique              |

