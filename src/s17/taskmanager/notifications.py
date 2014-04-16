# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from collective.watcherlist.utils import get_charset
from collective.watcherlist.utils import su
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from five import grok
from Products.CMFCore.utils import getToolByName
from s17.taskmanager import MessageFactory as _
from s17.taskmanager.adapters import IResponseContainer
from s17.taskmanager.content import ITask
from zope.i18n import translate
from zope.site.hooks import getSite

import textwrap

wrapper = textwrap.TextWrapper(initial_indent='    ', subsequent_indent='    ')

grok.templatedir('templates')


class BaseMail(grok.View):
    grok.baseclass()

    @property
    def plain(self):
        """The plain text version of the e-mail.
        """
        return u''

    @property
    def subject(self):
        """The subject of the e-mail.
        """
        return _(u'[No subject]')

    def render(self):
        """Render the e-mail.
        """

        return self.plain

    def prepare_email_message(self):
        plain = self.plain
        if not plain:
            return None

        # We definitely want unicode at this point.
        plain = su(plain)

        # We must choose the body charset manually.  Note that the
        # goal and effect of this loop is to determine the
        # body_charset.
        for body_charset in 'US-ASCII', get_charset(), 'UTF-8':
            try:
                plain.encode(body_charset)
            except UnicodeEncodeError:
                pass
            else:
                break
            # Encoding should work now; let's replace errors just in case.
        plain = plain.encode(body_charset, 'replace')

        text_part = MIMEText(plain, 'plain', body_charset)

        email_msg = MIMEMultipart('alternative')
        email_msg.epilogue = ''
        email_msg.attach(text_part)
        return email_msg


class NewTaskMail(BaseMail):
    grok.context(ITask)
    grok.name('new-task-mail')
    grok.require('zope2.View')

    @property
    def plain(self):
        context = aq_inner(self.context)
        portal = getSite()
        fromName = portal.getProperty('email_from_name', '')
        portal_membership = getToolByName(portal, 'portal_membership')
        taskCreator = context.Creator()
        taskCreatorInfo = portal_membership.getMemberInfo(taskCreator)
        taskAuthor = taskCreator
        if taskCreatorInfo:
            taskAuthor = taskCreatorInfo['fullname'] or taskCreator

        taskText = context.text
        if taskText:
            paras = taskText.raw.splitlines()
            taskDetails = '\n\n'.join([wrapper.fill(p) for p in paras])
        else:
            taskDetails = _('email_null_task_details', u"""No details in the task """)
        mail_text = _(
            'email_new_task_template',
            u"""A new task has been submitted by **${task_author}**.

Task Information
----------------

Task
  ${task_title} (${task_url})


**Task Details**::

${task_details}


* This is an automated email, please do not reply - ${from_name}""",
            mapping=dict(
                task_title=su(context.title),
                task_author=su(taskAuthor),
                task_details=su(taskDetails),
                task_url=su(context.absolute_url()),
                from_name=su(fromName)))
        # Translate the body text
        mail_text = translate(mail_text, 's17.taskmanager', context=self.request)
        return mail_text

    @property
    def subject(self):
        context = aq_inner(self.context)
        subject = _(
            'email_new_task_subject_template',
            u'[New task: ${task_title}]',
            mapping=dict(task_title=su(context.title))
        )
        # Make the subject unicode and translate it too.
        subject = su(subject)
        subject = translate(subject, 's17.taskmanager', context=self.request)
        return subject


class NewResponseMail(BaseMail):
    grok.context(ITask)
    grok.name('new-response-mail')
    grok.require('zope2.View')

    @property
    def plain(self):
        """When a response is created, send a notification email to all
        tracker managers
        """
        response_id = self.request.get('response_id', -1)
        context = aq_inner(self.context)
        folder = IResponseContainer(context)
        response = folder[response_id]

        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        portal_membership = getToolByName(portal, 'portal_membership')
        fromName = su(portal.getProperty('email_from_name', ''))

        creator = response.creator
        creatorInfo = portal_membership.getMemberInfo(creator)
        if creatorInfo and creatorInfo['fullname']:
            responseAuthor = creatorInfo['fullname']
        else:
            responseAuthor = creator
        responseAuthor = su(responseAuthor)

        responseText = su(response.text)
        paras = responseText.splitlines()

        # Indent the response details so they are correctly interpreted as
        # a literal block after the double colon behind the 'Response
        # Details' header.
        wrapper = textwrap.TextWrapper(
            initial_indent=u'    ', subsequent_indent=u'    ')
        responseDetails = u'\n\n'.join([wrapper.fill(p) for p in paras])

        if responseDetails:
            header = _('heading_response_details', u'Response Details')
            header = translate(header, 's17.taskmanager', context=self.request)
            responseDetails = u'**%s**::\n\n\n%s' % (header, responseDetails)

        changes = u''
        for change in response.changes:
            before = su(change.get('before'))
            after = su(change.get('after'))
            name = su(change.get('name'))
            # Some changes are workflow changes, which can be translated.
            # Note that workflow changes are in the plone domain.
            before = translate(before, 's17.taskmanager', context=self.request)
            after = translate(after, 's17.taskmanager', context=self.request)
            name = translate(name, 's17.taskmanager', context=self.request)
            changes += u'- %s: %s -> %s\n' % (name, before, after)

        mail_text = _(
            'email_new_response_template',
            u"""A new response has been given to the task **${task_title}**
by **${response_author}**.

Response Information
--------------------

Task
  ${task_title} (${task_url})

${changes}

${response_details}

* This is an automated email, please do not reply - ${from_name}""",
            mapping=dict(
                task_title=su(context.title),
                response_author=responseAuthor,
                response_details=responseDetails,
                task_url=su(context.absolute_url()),
                changes=changes,
                from_name=fromName))
        mail_text = translate(mail_text, 's17.taskmanager', context=self.request)
        return mail_text

    @property
    def subject(self):
        context = aq_inner(self.context)
        subject = _(
            'email_new_response_subject_template',
            u'Re: ${task_title}',
            mapping=dict(task_title=su(context.title)))
        # Ensure that the subject is unicode and translate it too.
        subject = su(subject)
        subject = translate(subject, 's17.taskmanager', context=self.request)
        return subject


class ClosedTaskMail(BaseMail):
    grok.context(ITask)
    grok.name('closed-task-mail')
    grok.require('zope2.View')

    @property
    def plain(self):
        context = aq_inner(self.context)
        portal = getSite()
        fromName = portal.getProperty('email_from_name', '')
        portal_membership = getToolByName(portal, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        memberInfo = portal_membership.getMemberInfo(member.getUserName())
        stateChanger = member.getUserName()
        if memberInfo:
            stateChanger = memberInfo['fullname'] or stateChanger
        mail_text = _(
            'email_task_closed_template',
            u"""The task **${task_title}** has been marked as resolved by **${response_author}**.
Please visit the task and either confirm that it has been
satisfactorily resolved or re-open it.

Response Information
--------------------

Task
  ${task_title} (${task_url})


* This is an automated email, please do not reply - ${from_name}""",
            mapping=dict(
                task_title=su(context.title),
                response_author=su(stateChanger),
                task_url=su(context.absolute_url()),
                from_name=su(fromName)))

        # Translate the body text
        mail_text = translate(mail_text, 's17.taskmanager', context=self.request)
        return mail_text

    @property
    def subject(self):
        context = aq_inner(self.context)
        subject = _(
            'email_task_closed_subject_template',
            u'[Resolved #${task_title}]',
            mapping=dict(task_title=su(context.title))
        )
        # Make the subject unicode and translate it too.
        subject = su(subject)
        subject = translate(subject, 's17.taskmanager', context=self.request)
        return subject
