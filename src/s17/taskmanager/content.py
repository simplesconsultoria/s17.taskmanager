# -*- coding: utf-8 -*-

from plone.directives import form

from zope import schema

from plone.app.textfield import RichText

from s17.taskmanager import MessageFactory as _

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

priorities = SimpleVocabulary(
    [SimpleTerm(value=1, title=_(u'High')),
     SimpleTerm(value=2, title=_(u'Normal')),
     SimpleTerm(value=3, title=_(u'Low'))]
)


class ITaskFolder(form.Schema):

    responsible = schema.Choice(
        title=_(u'Responsible'),
        description=_(''),
        required=False,
        vocabulary='plone.app.vocabularies.Users',
    )

    can_add_tasks = schema.List(
        title=_(u'Who can add tasks?'),
        description=_(''),
        required=False,
        value_type=schema.Choice(vocabulary='plone.app.vocabularies.Groups'),
    )


class ITask(form.Schema):

    title = schema.TextLine(
        title=_(u'Task Name'),
        description=_(''),
        required=True,
    )

    responsible = schema.Choice(
        title=_(u'Responsible'),
        description=_(''),
        required=False,
        vocabulary='plone.app.vocabularies.Users',
    )

    priority = schema.Choice(
        title=_(u'Priority'),
        description=_(''),
        required=True,
        vocabulary=priorities,
        default=2,
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
        title=_(u'Expected date'),
        description=_(''),
        required=False,
    )
