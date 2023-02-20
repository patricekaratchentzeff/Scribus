#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 (C)2023 Patrice Karatchentzeff

 Select first frametext object 

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
page = 1              # initial page

def main(argv):
    global page
    # select the firt textframe
    selectframetext = False
    deselectAll()
    pagenum = scribus.pageCount()  # page number
    print("pagenum=", pagenum)
    while (page <= pagenum):
        scribus.gotoPage(page)
        print("page=", page)
        lobjects = scribus.getAllObjects()
        print("lobjects=", lobjects)
        for obj in lobjects:
            print("obj=",obj)
            textframe = re.match(r'Text', obj)
            if textframe :
                print("Found textframe:", obj)
                scribus.selectObject(obj)
                selectframetext = True
                break
            else:
                 page += 1
        if selectframetext:
            break
        page += 1
    if ( selectframetext == False ):
        print("No frametext in document!")
        #sys.exit(0)

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
