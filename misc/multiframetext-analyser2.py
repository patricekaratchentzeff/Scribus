#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 (C)2023 Patrice Karatchentzeff
 
 This version 2023.02.18
 
 This program is free software; you can redistribute it and/or modify
 it under the terms of the  GPL, v3 (GNU General Public License as published by
 the Free Software Foundation, version 3 of the License), or any later version.
 See the Scribus Copyright page in the Help Browser for further informaton 
 about GPL, v3.
 
 SYNOPSIS

 This script aims to valid the concept of running on every textframe in a Scribus document.
 User does not need first to select an frametext: the script will search for him.
 This point is optional, then the script will run perfetly without selected object.
 Scribus document testcase is frametext-test-Document.sla in the same directory.
 
 REQUIREMENTS
 
 You must run from Scribus and must have a file open.
 
 USAGE
 
 Start the script in console into Scribus. Debug informations are written in it.
 Each frame is first read and after written again, by analysing current frame text 
 character by character

 DEVELOPMENT

 All the code are commented if you need to adapt this script for your
 own usage

 >>>>>>  test on: python 3.10.6 and Scribus 1.5.8
 
"""

import sys
import re

try:
    import scribus
except ImportError:
    print("This Python script is written for the Scribus scripting interface.")
    print("It can only be run from within Scribus.")
    sys.exit(1)

# variables definition
#
char = ''             # current character
nextchar = ''         # next character
prevchar = ''         # previous character
c = 0                 # indice (cursor) (in normal case, c=char)
page = 1              # initial page
contents = []         # whole text
textlen = 0           # number of characters in text
textlenshift = 0      # shift for having real characters by frame
totalpagemove = 0     # number of cursor movements in a page after insert/remove characters/spaces
workflow = "page"     # page (default) or frametext : working area for the script


# Indicator function
#
def info(message):
    # Show in bar text on the left scribus main interface
    # Including var is not easy to generalise
    # see an example at the end with .format function
    scribus.messagebarText(message)

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
#    * Selected object is requiere for finding linked frametext
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
            textframe = re.match(r"Text\d+", obj) # Text + at least a digit
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
    global page, c, char, nextchar, prevchar, textlen, textlenshift, totalpagemove
    # select the firt textframe object
    #   it is optional!
    # uncomment next line and comment the next one if you need
    select_firstframetext()
    #pagenum = scribus.pageCount()  # page number
    if workflow == "page":
        scribus.progressTotal(pagenum) # max progression bar
        scribus.messagebarText("Working on document...")
        # get the first and next linked frametext if exists
        scribus.gotoPage(page)
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
                        # next character
                        c += 1
                    rebuild_text(current_text)
            # nextpage
            page += 1

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
