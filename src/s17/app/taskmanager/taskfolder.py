# -*- coding: utf-8 -*-

from Acquisition import aq_inner

from five import grok

from plone.directives import form, dexterity

from zope import schema

from Products.CMFPlone.utils import getToolByName

from s17.app.taskmanager import MessageFactory as _


grok.templatedir("templates")



