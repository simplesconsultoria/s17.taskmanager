#!/bin/bash
# ensure that when something is wrong, nothing is broken more than it should...
set -e

# first, create some pot containing anything
i18ndude rebuild-pot --pot s17.taskmanager-plone.pot --create plone --merge plone-manual.pot ../*

# finally, update the po files
i18ndude sync --pot s17.taskmanager-plone.pot `find . -iregex '.*plone-.*\.po$'`