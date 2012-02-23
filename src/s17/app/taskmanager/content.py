# -*- coding: utf-8 -*-

from datetime import datetime

from plone.directives import form, dexterity

from zope import schema

from plone.app.textfield import RichText

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
def initial_date_default_value(data):
    return datetime.today()

@form.default_value(field=ITask['end_date'])
def end_date_default_value(data):
    return datetime.today()

@form.default_value(field=ITask['provided_date'])
def provided_date_default_value(data):
    return datetime.today()