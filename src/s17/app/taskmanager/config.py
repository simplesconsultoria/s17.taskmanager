# -*- coding: utf-8 -*-
# File: config.py

from s17.app.taskmanager.setuphandlers import get_package_dependencies

__author__ = """Simples Consultoria <products@simplesconsultoria.com.br>"""
__docformat__ = 'plaintext'

PROJECTNAME = 's17.app.taskmanager'

# PRODUCTS format
# (name,locked,hidden,install,profile,runProfile)

#PRODUCTS=[
#         ('collective.upload',0,1,1,'collective.upload:default',1),
#         ]

PRODUCTS = get_package_dependencies()