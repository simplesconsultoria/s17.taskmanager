# -*- coding: utf-8 -*-
import logging

from zope import component

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup import interfaces as gsinterfaces
from Products.GenericSetup.upgrade import listUpgradeSteps
from s17.app.taskmanager.config import PRODUCTS


PROJECT = 's17.app.taskmanager'


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
    dependencies = [(name,locked,hidden,profile) for name,locked,hidden,install,profile,runProfile in PRODUCTS if ((name in packages) and install)]

    for name,locked,hidden,profile in dependencies:
        qi.installProduct(name, locked=locked, hidden=hidden, profile=profile)