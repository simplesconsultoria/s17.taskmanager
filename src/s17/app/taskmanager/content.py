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

    title = schema.TextLine(
        title=_(u"Task Name"),
        description=_(''),
        required=True,
    )

    responsible = schema.Choice(
        title=_(u'Responsible'),
        description=_(''),
        required=False,
        vocabulary='plone.principalsource.Users',
    )

    priority = schema.Choice(
        title=_(u'Priority'),
        description=_(''),
        required=True,
        values= [ _(u'Alta'), _(u'Normal'), _(u'Baixa')],
        default=_(u'Normal'),
    )

    text = RichText(
        title=_(u'Task Detail'),
        description=_(''),
        default_mime_type='text/structured',
        output_mime_type='text/html',
        allowed_mime_types=('text/structured', 'text/plain',),
        required=False,
    )

    initial_date = schema.Date(
        title=_(u'Initial date'),
        description=_(''),
        required=False,
        readonly=True,
    )

    end_date = schema.Date(
        title=_(u'End date'),
        description=_(''),
        required=False,
        readonly=True,
    )

    provided_date = schema.Date(
        title=_(u'Provided date'),
        description=_(''),
        required=False,
    )

#@form.default_value(field=ITask['provided_date'])
#def provided_date_default_value(data):
#    return datetime.today()