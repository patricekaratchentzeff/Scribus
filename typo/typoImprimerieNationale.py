#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 (C)2023 Patrice Karatchentzeff
 
 This version 2023.02.15
 
 This program is free software; you can redistribute it and/or modify
 it under the terms of the  GPL, v3 (GNU General Public License as published by
 the Free Software Foundation, version 3 of the License), or any later version.
 See the Scribus Copyright page in the Help Browser for further informaton 
 about GPL, v3.
 
 SYNOPSIS

 This script aims to format the punctuation signs in order to respect
the directives of the French Imprimerie nationale (France)
 
 REQUIREMENTS
 
 You must run from Scribus and must have a file open.
 
 USAGE
 
 Start the script. A file dialog appears for choosing the target
(simple frame or all the page)

 DEVELOPMENT

All the code are commented if you need to adapt this script for your
own usage, for instance to adapt for other language than French.
 
"""

import sys

try:
    import scribus
except ImportError:
    print("This Python script is written for the Scribus scripting interface.")
    print("It can only be run from within Scribus.")
    sys.exit(1)

from datetime import datetime, timedelta
    
# variables definition
#
char = ''             # current character
nextchar = ''         # next character
prevchar = ''         # previous character
c = 0                 # indice (cursor) (in normal case, c=char)
page = 1              # initial page
content = []          # whole text
textlen = 0           # number of characters in text
textlenshift = 0      # shift for having characters by page
totalpagemove = 0     # number of cursor movements in a page after insert/remove characters/spaces
spaceindic = 0        # remove space character indicator 
singleindic = 0       # change single sign character indicator 
doubleindic = 0       # change double sign character indicator
double_thinindic = 0  # change double_thin sign character indicator
dashindic = 0         # change dash sign character indicator
langleindic = 0       # change left angle sign character indicator
rangleindic = 0       # change right angle sign character indicator
lparentindic = 0      # change left parenthesis sign character indicator
rparentindic = 0      # change reight parenthesis sign character indicator
workflow = "page"     # page (default) or frametext : working area for the script
runtime = 0           # script runtime

# Space character definition
#   s    (normal space)
#   nbs  (non breaking space)
#   nbts (non breaking thin space)
#   ts   (thin space)
#   n    (nothing, i.e all except space)
non_breaking_space = u"\u00a0"      
non_breaking_thin_space = u"\u202f"
thin_space = u"\u2009"
space = ' '
spacelist = [space, thin_space, non_breaking_space, non_breaking_thin_space]

# Other specific characters
#
lparent = u"\u0028"   # left parenthesis  (
rparent = u"\u0029"   # right parenthesis )
lsbracket = u"\u005b" # left square bracket  [
rsbracket = u"\u005d" # right square bracket ]

# Indicator function
#
def info(message):
    # Show in bar text on the left scribus main interface
    # Including var is not easy to generalise
    # see an example at the end with .format function
    scribus.messagebarText(message)

# basic functions for manipulating/testing characters
#

# define char, prevchar and char
#        cur: current position in text
def define_char(cur, textlen, text):
    global char, prevchar, nextchar
    # Possible blank or almost-blank page!
    if textlen <= 1:
        prevchar = ''
        char = ''
        nextchar = ''
    else:    
        # 1st character
        if (cur == 0):
            prevchar = ''
            scribus.selectText(cur + 1, 1, text)
            nextchar = scribus.getText(text)
        # last character    
        if (cur == textlen - 1):
            nextchar = ''
            scribus.selectText(cur - 1, 1, text)
            prevchar = scribus.getText(text)
        # other characters
        if (cur > 0 and cur < textlen-1):
            scribus.selectText(cur - 1, 1, text)
            prevchar = scribus.getText(text)
            scribus.selectText(cur + 1, 1, text) 
            nextchar = scribus.getText(text)
        if (cur > textlen-1):
            print("ERROR: current text character pointer overflow!")
            sys.exit(1)
        scribus.selectText(cur, 1, text)
        char = scribus.getText(text)

# Space character tests
#
def match_space(char):
    if char in spacelist:
        return True
    else:
        return False

def not_match_space(char):
    if char in spacelist:
        return False
    else:
        return True

# Inserting, deleting and replacing characters
#  - run only for ONE character, no need more in French -
#
def insert_char(char, position, text):
    global c, totalpagemove
    scribus.insertText(char, position, text)
    c += 1 # current cursor has increased by 1
    totalpagemove += 1

def remove_char(position, text):
    global c, totalpagemove
    scribus.selectText(position, 1, text) # set 1 in variable if needs to replace more
    scribus.deleteText(text)
    c -= 1 # current cursor has decreased by 1
    totalpagemove -= 1

def replace_char(char, position, text):
    scribus.selectText(position, 1, text)
    scribus.deleteText(text)
    scribus.insertText(char, position, text)
    
# Official French typo by Imprimerie nationale française
#
# signs    before/after      associated test function   associated correction function
# char   prevchar/nextchar
#
# ss...    s                 FR_is_a_space              FR_remove_duplicated_spaces
# .,       n/s               FR_is_a_single             FR_typo_for_single
# ;!?      nbts/s            FR_is_a_double_thin        FR_typo_for_double_thin
# :        nbs/s             FR_is_a_double             FR_typo_for_double
# —        s/s               FR_is_a_dash               FR_typo_for_dash
# «        s/nbs             FR_is_a_langle             FR_typo_for_rangle
# »        nbs/s             FR_is_a_rangle             FR_typo_for_langle
# ([       s/n               FR_is_a_lparent            FR_typo_for_oparent
# )]       n/s               FR_is_a_rparent            FR_typo_for_cparent
#
# NOTE1 : … is n/s at the end and then begining of a sentence
#           is also n/n between bracket for indicating a cut
#         --> automation is not possible, because depends of the context.
# NOTE2 : french single and double quotes (guillemet APL ', guillemet dactyloographique ",
#         apostrophe culbuté ‘, apostrophe ’, virgule double „, guillemet simple gauche ‹
#         et guillemet simple droite ›) follows obvious rules (s/n for right and n/s for left).
#         but are not fully automated because they depend of the context. People who use it
#         know normaly what they do!
#         !!! English quotes “ ” should not normaly use
#
# All the following process is based on the fact that there is not more than
# ONE space to analyse, then it is important to remove first the following space
# characters. In French typo, in any case, it is not possible to have many
# following space characters
# If ever you adapt the script for other languages, pay attention at this point

# Clean following (duplicated) spaces
#
# all cases of space caracters
def FR_is_a_space(char):
    return (char == space) \
        or (char == non_breaking_space) \
        or (char == non_breaking_thin_space) \
        or (char == thin_space)

def FR_remove_duplicated_spaces(cur, text, prevchar, nextchar):
    global spaceindic
    # remove current space after a space
    # (because this function is included in a loop, the next step(s) will purchase/achieve the job)
    if (match_space(prevchar)):
        remove_char(cur, text)
        spaceindic += 1

# Now it is time to produce all the functions of the French typo rules
#        
# .,       n/s      FR_is_a_single    FR_typo_for_single
#
def FR_is_a_single(char):
    return (char == '.') or (char == ',')

def FR_typo_for_single(cur, text, prevchar, nextchar):
    global singleindic
    # n/n  --> n/s
    if (not_match_space(prevchar) and not_match_space(nextchar)):  
        insert_char(space, cur + 1, text)
        singleindic += 1
    # n/s  --> n/s (swap 'general' s in 'good' s if ever)  
    if (not_match_space(prevchar) and match_space(nextchar)):  
        replace_char(space, cur + 1, text)
        singleindic += 1
    # s/n  --> n/s 
    if (match_space(prevchar) and not_match_space(nextchar)):  
        remove_char(cur - 1, text)
        insert_char(space, cur, text) # shif of -1 because of previous delete
        singleindic += 1
    # s/s  --> n/s (swap 'general' s in 'good' s if ever)  
    if (match_space(prevchar) and match_space(nextchar)):  
        remove_char(cur - 1, text)
        replace_char(space, cur, text) # shif of -1 because of previous delete
        singleindic += 1

# ;!?      nbts/s         FR_is_a_double_thin       FR_typo_for_double_thin
#
def FR_is_a_double_thin(char):
    return (char == ';') or (char == '!') or (char == '?')

def FR_typo_for_double_thin(cur, text, prevchar, nextchar):
    global double_thinindic
    # s/s  --> nbts/s (swap if ever needs)
    if (match_space(prevchar) and match_space(nextchar)):  
        replace_char(non_breaking_thin_space, cur - 1, text)
        replace_char(space, cur + 1, text)
        double_thinindic += 1
    # s/n  --> nbts/s 
    if (match_space(prevchar) and not_match_space(nextchar)):  
        replace_char(non_breaking_thin_space, cur - 1, text)
        insert_char(space, cur + 1, text)
        double_thinindic += 1
    # n/n  --> nbts/s 
    if (not_match_space(prevchar) and not_match_space(nextchar)):  
        insert_char(non_breaking_thin_space, cur, text)
        insert_char(space, cur + 2, text)
        double_thinindic += 1
    # n/s  --> nbts/s
    if (not_match_space(prevchar) and match_space(nextchar)):  
        insert_char(non_breaking_thin_space, cur, text)
        replace_char(space, cur + 2, text)
        double_thinindic += 1

# :        nbs/s             FR_is_a_double             FR_typo_for_double
#
def FR_is_a_double(char):
    return char == ':'

def FR_typo_for_double(cur, text, prevchar, nextchar):
    global doubleindic
    # s/s  --> nbs/s (swap if ever needs)
    if (match_space(prevchar) and match_space(nextchar)):  
        replace_char(non_breaking_space, cur - 1, text)
        replace_char(space, cur + 1, text)
        doubleindic += 1
    # s/n  --> nbs/s 
    if (match_space(prevchar) and not_match_space(nextchar)):  
        replace_char(non_breaking_space, cur - 1, text)
        insert_char(space, cur + 1, text)
        doubleindic += 1
    # n/n  --> nbs/s 
    if (not_match_space(prevchar) and not_match_space(nextchar)):  
        insert_char(non_breaking_space, cur, text)
        insert_char(space, cur + 2, text)
        doubleindic += 1
    # n/s  --> nbs/s
    if (not_match_space(prevchar) and match_space(nextchar)):  
        insert_char(non_breaking_space, cur, text)
        replace_char(space, cur + 2, text)
        doubleindic += 1

# —        s/s               FR_is_a_dash               FR_typo_for_dash
#
def FR_is_a_dash(char):
    return char == '—'

def FR_typo_for_dash(cur, text, prevchar, nextchar):
    global dashindic
    # s/s  --> s/s (swap if ever needs)
    if (match_space(prevchar) and match_space(nextchar)):  
        replace_char(space, cur - 1, text)
        replace_char(space, cur + 1, text)
        dashindic += 1
    # s/n  --> s/s 
    if (match_space(prevchar) and not_match_space(nextchar)):  
        replace_char(space, cur - 1, text)
        insert_char(space, cur + 1, text)
        dashindic += 1
    # n/n  --> s/s 
    if (not_match_space(prevchar) and not_match_space(nextchar)):  
        insert_char(space, cur, text)
        insert_char(space, cur + 2, text)
        dashindic += 1
    # n/s  --> s/s
    if (not_match_space(prevchar) and match_space(nextchar)):  
        insert_char(space, cur, text)
        replace_char(space, cur + 2, text)
        dashindic += 1

# «        s/nbs             FR_is_a_rangle             FR_typo_for_rangle
#
def FR_is_a_langle(char):
    return char == '«'

def FR_typo_for_langle(cur, text, prevchar, nextchar):
    global langleindic
    # s/s  --> s/nbs (swap if ever needs)
    if (match_space(prevchar) and match_space(nextchar)):  
        replace_char(space, cur - 1, text)
        replace_char(non_breaking_space, cur + 1, text)
        langleindic += 1
    # s/n  --> s/nbs 
    if (match_space(prevchar) and not_match_space(nextchar)):  
        replace_char(space, cur - 1, text)
        insert_char(non_breaking_space, cur + 1, text)
        langleindic += 1
    # n/n  --> s/nbs 
    if (not_match_space(prevchar) and not_match_space(nextchar)):  
        insert_char(space, cur, text)
        insert_char(non_breaking_space, cur + 2, text)
        langleindic += 1
    # n/s  --> s/nbs
    if (not_match_space(prevchar) and match_space(nextchar)):  
        insert_char(space, cur, text)
        replace_char(non_breaking_space, cur + 2, text)
        langleindic += 1

# »        nbs/s             FR_is_a_langle             FR_typo_for_langle
#
def FR_is_a_rangle(char):
    return char == '»'

def FR_typo_for_rangle(cur, text, prevchar, nextchar):
    global rangleindic
    # s/s  --> nbs/s (swap if ever needs)
    if (match_space(prevchar) and match_space(nextchar)):  
        replace_char(non_breaking_space, cur - 1, text)
        replace_char(space, cur + 1, text)
        rangleindic += 1
    # s/n  --> nbs/s 
    if (match_space(prevchar) and not_match_space(nextchar)):  
        replace_char(non_breaking_space, cur - 1, text)
        insert_char(space, cur + 1, text)
        rangleindic += 1
    # n/n  --> nbs/s 
    if (not_match_space(prevchar) and not_match_space(nextchar)):  
        insert_char(non_breaking_space, cur, text)
        insert_char(space, cur + 2, text)
        rangleindic += 1
    # n/s  --> nbs/s
    if (not_match_space(prevchar) and match_space(nextchar)):  
        insert_char(non_breaking_space, cur, text)
        replace_char(space, cur + 2, text)
        rangleindic += 1

# ([       s/n               FR_is_a_lparent            FR_typo_for_lparent
#
def FR_is_a_lparent(char):
    return (char == lparent) or (char == lsbracket)

def FR_typo_for_lparent(cur, text, prevchar, nextchar):
    global lparentindic
    # s/s  --> s/n 
    if (match_space(prevchar) and match_space(nextchar)):  
        replace_char(space, cur - 1, text)
        remove_char(cur + 1, text)
        lparentindic += 1
    # s/n  --> s/n 
    if (match_space(prevchar) and not_match_space(nextchar)):  
        replace_char(space, cur - 1, text)
        lparentindic += 1
    # n/n  --> s/n 
    if (not_match_space(prevchar) and not_match_space(nextchar)):  
        insert_char(space, cur, text)
        lparentindic += 1
    # n/s  --> s/n
    if (not_match_space(prevchar) and match_space(nextchar)):  
        insert_char(space, cur, text)
        remove_char(cur + 2, text)
        lparentindic += 1

# )]       n/s               FR_is_a_rparent            FR_typo_for_rparent
#
def FR_is_a_rparent(char):
    return (char == ')') or (char == ']')

def FR_typo_for_rparent(cur, text, prevchar, nextchar):
    global rparentindic
    # s/s  --> n/s 
    if (match_space(prevchar) and match_space(nextchar)):  
        remove_char(cur - 1, text)
        replace_char(space, cur, text)
        rparentindic += 1
    # s/n  --> n/s 
    if (match_space(prevchar) and not_match_space(nextchar)):
        remove_char(cur - 1, text)
        insert_char(space, cur, text)
        rparentindic += 1
    # n/n  --> n/s 
    if (not_match_space(prevchar) and not_match_space(nextchar)):  
        insert_char(space, cur + 1, text)
        rparentindic += 1
    # n/s  --> n/s
    if (not_match_space(prevchar) and match_space(nextchar)):  
        replace_char(space, cur + 1, text)
        rparentindic += 1

# List of tuple functions for general purpose at the final loop
# --> inconvenience: all the function should have the same arguments
#
FR_typo_todo = ((FR_is_a_space, FR_remove_duplicated_spaces), \
                (FR_is_a_single, FR_typo_for_single), \
                (FR_is_a_double_thin, FR_typo_for_double_thin), \
                (FR_is_a_double, FR_typo_for_double), \
                (FR_is_a_dash, FR_typo_for_dash), \
                (FR_is_a_rangle, FR_typo_for_rangle), \
                (FR_is_a_langle, FR_typo_for_langle), \
                (FR_is_a_lparent, FR_typo_for_lparent), \
                (FR_is_a_rparent, FR_typo_for_rparent) \
                )

# That's all for the typo.
# now general setup for the user

# Welcome banner for explicit the goal of the script.
# escape is possible for error
#
def welcome_banner():
    #
    message_init = """<center>Ce script a pour but de forcer la tyographie du texte
    en respectant les normes recommandées par l'<b>Imprimerie nationale de France</b>.
    Il ne gère donc que les <font color=red>espacements</font>.
    <br><br> Si vous voulez transformer vos caractères en respectant les usages de France,
    comme les guillemets « ou », utilisez un autre script.
    <br><br>Pour poursuivre, cliquer sur OK</center>"""
    info("Message d'information")
    result = scribus.messageBox("Information",
                                message_init,
                                icon=ICON_INFORMATION,
                                button1=BUTTON_OK,
                                button2=BUTTON_ABORT|BUTTON_DEFAULT)
    if ( result == BUTTON_ABORT):
        sys.exit(1)

# Setup the script: for frametext or for all the page?
#       exit if no selection or bad selection object
def setup_script():
    global workflow
    info("Configuration du script")
    while True:
        message_setup = """<center>Appliquer la typographie</center>
        <ul> 1 : sur une zone de texte (à sélectionner à la souris auparavant)</ul>
        <ul> 2: sur tout le document (choix par défaut)</ul>
        <ul> 0 : pour quitter le processus</ul>"""
        flow = scribus.valueDialog("Domaine d'application", message_setup, "2")
        if flow == "2":
            workflow = "page"
            break
        if flow == "1":
            workflow = "frametext"
            break
        if flow == "0":
            sys.exit(1)
        else:
            message_warn = """<center>Vous devez répondre par 1 (zone de texte) <br>
            ou 2 (tout le document)</center>"""
            scribus.messageBox("Information",
                               message_warn,
                               icon=ICON_WARNING,
                               button1=BUTTON_OK)
    # check if a frametext has been selected
    if workflow == "frametext":
         # no selection
        if scribus.selectionCount() == 0:
            message_warn = """Aucun objet n'est sélectionné.\n
            Sélectionnez un cadre de texte et recommencez. """
            scribus.messageBox('Scribus - Erreur',
                               message_warn,
                               scribus.ICON_WARNING, scribus.BUTTON_OK)
            sys.exit(2)
        # multi-selection
        elif scribus.selectionCount() > 1:
            message_warn = """<center>Ce script ne peut pas fonctionner 
            lorsque plusieurs objets sont sélectionnés.<br>
            Veuillez ne sélectionner qu'un seul cadre de texte, <br>
            puis recommencez.</center> """
            scribus.messageBox('Scribus - Erreur',
                               message_warn,
                               scribus.ICON_WARNING, scribus.BUTTON_OK)
            sys.exit(2)
        # check if selection is a real frametext
        else:
            list_item = scribus.getPageItems() # [('Text1', 4, 0), ('Image1', 2, 1), ...]
            for item in list_item:
                if (item[1] != 4):
                    message_warn = """ L'objet sélectionné n'est pas un cadre de texte.\n
                    Veuillez sélectionner un cadre de texte, puis recommencez. """
                    scribus.messageBox('Scribus - Erreur',
                                       message_warn,
                                       scribus.ICON_WARNING, scribus.BUTTON_OK)
                    sys.exit(2)

# Final stats
#
def final_stats():
    # (other solution is to use import Template)
    # Limitation of presentation is Rich Text limitations
    message_stats = """
    <table>
    <tr>
      <th>Règles typographiques</th>
      <th>Modifications</th>
    </tr>
    <tr style="background-color:{color2}">
      <td>Modification d'espaces surnuméraire</td>
      <td style="text-align:center">{space}</td>
    </tr>
    <tr style="background-color:{color1}">
      <td>Ponctuation simple ('.' et ',')</td>
      <td style="text-align:center">{single}</td>
    </tr>
    <tr style="background-color:{color2}">
      <td>Ponctuation double (';', '!' et '?')</td>
      <td style="text-align:center">{double_thin}</td>
    </tr>
    <tr style="background-color:{color1}">
      <td>Ponctuation double (':')</td>
      <td style="text-align:center">{double}</td>
    </tr>
    <tr style="background-color:{color2}">
      <td>Tiret ('—')</td>
      <td style="text-align:center">{dash}</td>
    </tr>
    <tr style="background-color:{color1}">
      <td>Guillemet ouvrant ('«')</td>
      <td style="text-align:center">{langle}</td>
    </tr>
    <tr style="background-color:{color2}">
      <td>Guillemet fermant ('»')</td>
      <td style="text-align:center">{rangle}</td>
    </tr>
    <tr style="background-color:{color1}">
      <td>Parenthèses ouvrantes ('(' et '[')</td>
      <td style="text-align:center">{lparent}</td>
    </tr>
    <tr style="background-color:{color2}">
      <td>Parenthèses fermantes (')' et ']')</td>
      <td style="text-align:center">{rparent}</td>
    </tr>
    </table>
    <br>
    <center>Temps de traitement : {rtime}</center>
    """.format(single=singleindic, space=spaceindic, double_thin=double_thinindic,
               double=doubleindic, dash=dashindic, langle=langleindic,
               rangle=rangleindic, lparent=lparentindic, rparent=rparentindic,
               rtime=runtime, color1="#FFFFF0", color2="#FFFBCD")
    scribus.messageBox('Statistiques du traitement',
                       message_stats,
                       scribus.ICON_INFORMATION, scribus.BUTTON_OK)

# Computes the process time and returns human lisible time
#    
def process_time(final_time, init_time):
    global runtime
    rtime = final_time - init_time
    min = rtime.seconds // 60
    sec = rtime.seconds - 60*min
    runtime = """{minute} min {second} s""".format(minute=min, second=sec)
    return runtime

# print debug info
#
def print_debug(c, page, pagenum, list_item, text, textlen,
                textlen2, textlenshift, totalpagemove, contents):
    debug = """
********************************************************************
* DEBUG mode
*   Page {page} of {pagenum}
*       Page item: {list_item}
*        Current processing text: ++++ {text} ++++
*         => textlen={textlen} (textlen2={textlen2}) 
*            textlenshift={textlenshift}  totalpagemove={totalpagemove}
*            Initial cursor is {c}
********************************************************************

=== Current text  =======
{contents}
=== End current text ====
    """.format(c=c, page=page, pagenum=pagenum, list_item=list_item,
               text=text, textlen=textlen, textlen2=textlen2,
               textlenshift=textlenshift, totalpagemove=totalpagemove,
               contents=contents)
    print(debug)

# Print rebuild text after the loop
#
def rebuild_text(text):
    rebuilt= """
*** Rebuilt text  ******
{text}
*** End rebuilt text  **
    """.format(text=text)
    print(rebuilt)

# Select first frametext objetc for all the document run
#    * Selected object is requiere to find linked frametext
#    * No frametext is a fail
#    * The script will then run on the first found page
#
def select_firstframetext():
    global page, pagenum
    selectframetext = False        # flag for existence
    deselectAll()                  # unselect all
    pagenum = scribus.pageCount()  # page number
    # test all objets per page searching a frame
    while (page <= pagenum):
        scribus.gotoPage(page)
        lobjects = scribus.getAllObjects()
        for obj in lobjects:
            textframe = re.match('Text', obj) # Text + a digit
            if textframe :
                first_text = obj
                scribus.selectObject(obj)
                selectframetext = True
                break
            else:
                 page += 1
        if selectframetext:
            print("\n>>>> First selected frametext object is:", first_text)
            break
        page += 1
    if ( selectframetext == False ):
        # add a Scribus dialog to inform fail
        print("DEBUG: No frametext object in document!")

def main(argv):
    """
    """
    global page, c, textlenshift, totalpagemove, runtime
    # setup the script
    #
    welcome_banner()
    setup_script()
    # run on frametext only
    #
    start = datetime.now() # get init time start process
    if workflow == "frametext":
        text = scribus.getSelectedObject()
        textlen = scribus.getTextLength(text)
        scribus.progressTotal(textlen - 1) # max progression bar
        scribus.messagebarText("Working on frametext...")
        # analyse of the text char by char
        #
        while c <= (textlen - 1):
            scribus.messagebarText("Working on text...")
            scribus.progressSet(c)   # progression bar step
            # setup prevchar, char and nextchar
            define_char(c, textlen, text)
            #print("DEBUG mode", "  Text=", text, "c=", c, "/", textlen, "  char=", char)
            # adjust typo
            for dotypo in FR_typo_todo:
                if (dotypo[0](char)):
                    dotypo[1](c, text, prevchar, nextchar)
            # next character
            c += 1
    # run on all the pages
    #
    if workflow == "page":
        pagenum = scribus.pageCount()  # page number   
        scribus.progressTotal(pagenum) # max progression bar
        scribus.messagebarText("Working on document...")
        #
        while (page <= pagenum):
            scribus.progressSet(page)  # progression bar step
            message_info = """Working on page {number}""".format(number=page)
            info(message_info)
            scribus.gotoPage(page)
            list_item = scribus.getPageItems() # [('Text1', 4, 0), ('Image1', 2, 1), ...]
            for item in list_item:
                # must work only on the text
                if (item[1] == 4):  # 4 (= Text frame) of ('Text1', 4, 0)
                    text = item[0]  # Text1 of ('Text1', 4, 0)
                    # select all the text in current frame for couting characters
                    # use selectFrameText instead of getTextLength
                    # bug : getTextLength sends all the text from ALL the linked frames
                    #       if an object has not been selected!
                    #       textlen = scribus.getTextLength(text)
                    scribus.selectFrameText(0,-1,text)
                    contents = scribus.getFrameText(text)
                    textlen2 = len(contents)              # real text length to work
                    textlen = scribus.getTextLength(text) # whole text length over all the linked frames
                    c = 0 # init cursor at position 0
                    print_debug(c, page, pagenum, list_item, text,
                                textlen, textlen2, textlenshift, totalpagemove,
                                contents)
                    # analyse of the text char by char
                    current_text = ''
                    while c <= (textlen - 1):
                        # setup prevchar, char and nextchar
                        define_char(c, textlen, text)
                        #print("DEBUG mode", "  Text=", text, "c=", c, "/", textlen, "  char=", char)
                        # here, the job to do on characters...
                        current_text += char
                        # adjust typo
                        for dotypo in FR_typo_todo:
                            if (dotypo[0](char)):
                                dotypo[1](c, text, prevchar, nextchar)
                        # next character
                        c += 1
                    rebuild_text(current_text)
            # nextpage
            page += 1
    # get end time process
    end = datetime.now()
    runtime = process_time(end, start)
    # Final stats information
    #    
    final_stats()       

def main_wrapper(argv):
    """The main_wrapper() function disables redrawing, sets a sensible generic
    status bar message, and optionally sets up the progress bar. It then runs
    the main() function. Once everything finishes it cleans up after the main()
    function, making sure everything is sane before the script terminates."""
    try:
        scribus.statusMessage("Running script...")
        scribus.progressReset()
        main(argv)
    finally:
        # Exit neatly even if the script terminated with an exception,
        # so we leave the progress bar and status bar blank and make sure
        # drawing is enabled.
        if scribus.haveDoc():
            scribus.setRedraw(True)
            scribus.statusMessage("")
            scribus.progressReset()

# This code detects if the script is being run as a script, or imported as a module.
# It only runs main() if being run as a script. This permits you to import your script
# and control it manually for debugging.
if __name__ == '__main__':
    main_wrapper(sys.argv)
