# -*- coding: utf-8 -*-

from Acquisition import aq_inner

from datetime import datetime

from five import grok

from plone.directives import form, dexterity

from zope import schema

from Products.CMFPlone.utils import getToolByName

from plone.app.textfield import RichText

from s17.app.taskmanager import MessageFactory as _

grok.templatedir("templates")

class ITask(form.Schema):

    priority = schema.Choice(
        title=_(u'Priority'),
        description=_(''),
        required=True,
        values= [_(u'Low'), _(u'Normal'), _(u'High')],
    )

    text = RichText(
        title=_(u'Body text'),
        description=_(''),
        required=False,
    )

    initial_date = schema.Date(
        title=_(u'Initial date'),
        description=_(''),
        required=False,
    )

    final_date = schema.Date(
        title=_(u'End date'),
        description=_(''),
        required=False,
    )

    provided_date = schema.Date(
        title=_(u'Provided date'),
        description=_(''),
        required=False,
    )

    responsible = schema.Choice(
        title=_(u'Responsible'),
        description=_(''),
        required=False,
        vocabulary='plone.principalsource.Users',
    )

@form.default_value(field=ITask['initial_date'])
def startDefaultValue(data):
    return datetime.today()

#class View(grok.View):
#    grok.context(ITask)
#    grok.name("view")
#    grok.template('task_view')
#    grok.require("zope2.View")