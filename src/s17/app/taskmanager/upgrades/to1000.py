# -*- coding: utf-8 -*-
import logging

from zope import component

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup import interfaces as gsinterfaces
from Products.GenericSetup.upgrade import listUpgradeSteps
from s17.app.taskmanager.config import PRODUCTS


PROJECT = 's17.app.taskmanager'

def get_package_name(name):
    return name[9:] if name.startswith('Products') else name

def fromZero(context):
    ''' Upgrade from Zero to version 1000
    '''

    setup = getToolByName(context, 'portal_setup')
    migration = getToolByName(context,'portal_migration')
    catalog = getToolByName(context,'portal_catalog')
    portal_properties = getToolByName(context,'portal_properties')
    qi = getToolByName(context,'portal_quickinstaller')

    # Install dependencies for this upgrade
    # List package names
    packages = [
        'collective.upload',
        ]
    # (name,locked,hidden,install,profile,runProfile)
    dependencies = [p for p in PRODUCTS
                    if ((p['package'] in packages) and p['install'])]

    for p in dependencies:
        qi.installProduct(get_package_name(p['package']), locked=p['locked'],
            hidden=p['hidden'], profile=p['profile'])