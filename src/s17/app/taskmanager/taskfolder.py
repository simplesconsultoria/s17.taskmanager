# -*- coding: utf-8 -*-

from Acquisition import aq_inner

from five import grok

from plone.directives import form, dexterity

from zope import schema

from Products.CMFPlone.utils import getToolByName

from s17.app.taskmanager import MessageFactory as _


class ITaskFolder(form.Schema):

    responsible = schema.Choice(
        title=_(u'Responsible'),
        description=_(''),
        required=False,
        vocabulary='plone.principalsource.Users',
    )

    can_add_tasks = schema.List(
        title=_(u'Who can add tasks?'),
        description=_(''),
        required=False,
        value_type = schema.Choice(vocabulary='plone.principalsource.Principals'),
    )

#class View(dexterity.DisplayForm):
#    grok.context(IIdeaFolder)
#    grok.require('zope2.View')