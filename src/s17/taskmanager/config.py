# -*- coding: utf-8 -*-
# File: config.py

from s17.taskmanager.setuphandlers import get_package_dependencies

__author__ = """Simples Consultoria <products@simplesconsultoria.com.br>"""
__docformat__ = 'plaintext'

PROJECTNAME = 's17.taskmanager'

PRODUCTS = get_package_dependencies()
