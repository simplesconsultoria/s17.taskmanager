#!/bin/bash
# kudos to Products.Ploneboard for the base for this file
# ensure that when something is wrong, nothing is broken more than it should...
set -e

# first, create some pot containing anything
i18ndude rebuild-pot --pot s17.taskmanager.pot --create s17.taskmanager --merge manual.pot ..

# finally, update the po files
i18ndude sync --pot s17.taskmanager.pot  `find . -iregex '.*\.po$'|grep -v plone`

