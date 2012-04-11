# -*- coding: utf-8 -*-

from Acquisition import aq_inner

from five import grok

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.cachedescriptors.property import Lazy
from zope.i18n import translate

from plone.directives import dexterity
from plone.memoize.view import memoize

from Products.CMFPlone.utils import getToolByName
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IATImage
from Products.statusmessages.interfaces import IStatusMessage

from s17.app.taskmanager.content import ITask, ITaskFolder
from s17.app.taskmanager.adapters import Response, IResponseContainer
from s17.app.taskmanager import MessageFactory as _


grok.templatedir("templates")

class TaskFolderView(dexterity.DisplayForm):
    grok.context(ITaskFolder)
    grok.name("view")
    grok.template('taskfolder_view')
    grok.require("zope2.View")

    def responsible(self, obj):
        """ Return the fullname of the responsible for the task
        """
        mt = getToolByName(self.context, 'portal_membership')
        username = obj.responsible
        if username:
            fullname = mt.getMemberById(username).getProperty('fullname')
            if fullname:
                return fullname
            else:
                return username
        else:
            return None

    def tasks(self):
        ''' function to return all tasks in the container
        '''
        ct = getToolByName(self.context,'portal_catalog')
        tasks = ct(object_provides=ITask.__identifier__, path='/'.join(self.context.getPhysicalPath()))
        if tasks:
            return [dict(title=task.Title,
                         url=task.getURL(),
                         status=task.review_state.capitalize(),
                         responsible=self.responsible(task.getObject()),
                         priority=task.getObject().priority,)
                            for task in tasks]
        else:
            return None

class TaskView(dexterity.DisplayForm):
    grok.context(ITask)
    grok.name("view")
    grok.template('task_view')
    grok.require("zope2.View")

    def images(self):
        ct = getToolByName(self.context,'portal_catalog')
        images = ct(object_provides=IATImage.__identifier__,path = '/'.join(self.context.getPhysicalPath()))
        if images:
            images = [ image.getObject() for image in images ]
            return images
        else:
            return None

    def files(self):
        ct = getToolByName(self.context,'portal_catalog')
        files = ct(object_provides=IATFile.__identifier__,path = '/'.join(self.context.getPhysicalPath()))
        if files:
            return files
        else:
            return None

    def responsible(self):
        """ Return the fullname of the responsible for the task
        """
        mt = getToolByName(self.context, 'portal_membership')
        username = self.context.responsible
        if username:
            fullname = mt.getMemberById(username).getProperty('fullname')
            if fullname:
                return fullname
            else:
                return username
        else:
            return None

    def responses(self):
        context = aq_inner(self.context)
        items = []
        folder = IResponseContainer(self.context)
        for id, response in enumerate(folder):
            if response is None:
                # Has been removed.
                continue
            html = response.text or u''
            info = dict(id=id,
                response=response,
                html=html)
            items.append(info)
        return items

    @Lazy
    def memship(self):
        context = aq_inner(self.context)
        return getToolByName(context, 'portal_membership')

    @property
    @memoize
    def can_edit_response(self):
        context = aq_inner(self.context)
        return self.memship.checkPermission('Modify portal content', context)

    @property
    @memoize
    def can_delete_response(self):
        context = aq_inner(self.context)
        return self.memship.checkPermission('Delete objects', context)

    @property
    def priority(self):
        context = aq_inner(self.context)
        return context.priority

    @property
    def res(self):
        context = aq_inner(self.context)
        return context.responsible

    @property
    @memoize
    def responsibles_for_display(self):
        context = aq_inner(self.context)
        users_factory = getUtility(IVocabularyFactory, name=u"plone.principalsource.Users")
        users = users_factory(context)
        options = []
        for value in users:
            values = {}
            values['checked'] = (value.token == self.res) and "checked" or ""
            values['value'] = value.token
            values['label'] = value.title
            options.append(values)
        return options

    @property
    @memoize
    def transitions_for_display(self):
        """Display the available transitions for this issue.
        """
        context = aq_inner(self.context)
        if not self.memship.checkPermission('Modify portal content',context):
            return []
        wftool = getToolByName(context, 'portal_workflow')
        transitions = []
        transitions.append(dict(value='', label=_(u'No change'),
            checked="checked"))
        for tdef in wftool.getTransitionsFor(context):
            transitions.append(dict(value=tdef['id'],
                label=tdef['title_or_id'], checked=''))
        return transitions

    @property
    def priority_for_display(self):
        """Get the available priorities for this issue.
        """
        vocab = [_(u'Baixa'), _(u'Normal'), _(u'Alta')]
        options = []
        for value in vocab:
            checked = (value == self.priority) and "checked" or ""
            options.append(dict(value=value, label=value,
                checked=checked))
        return options

class Create(grok.View):
    grok.context(ITask)
    grok.name("create_response")
    grok.require("zope2.View")


    @Lazy
    def memship(self):
        context = aq_inner(self.context)
        return getToolByName(context, 'portal_membership')

    @property
    @memoize
    def transitions_for_display(self):
        """Display the available transitions for this issue.
        """
        context = aq_inner(self.context)
        if not self.memship.checkPermission('Modify portal content',context):
            return []
        wftool = getToolByName(context, 'portal_workflow')
        transitions = []
        transitions.append(dict(value='', label=_(u'No change'),
            checked="checked"))
        for tdef in wftool.getTransitionsFor(context):
            transitions.append(dict(value=tdef['id'],
                label=tdef['title_or_id'], checked=''))
        return transitions

    @property
    def available_transitions(self):
        """Get the available transitions for this issue.
        """
        return [x['value'] for x in self.transitions_for_display]

    @property
    @memoize
    def responsibles_for_display(self):
        context = aq_inner(self.context)
        users_factory = getUtility(IVocabularyFactory, name=u"plone.principalsource.Users")
        users = users_factory(context)
        options = []
        for value in users:
            values = {}
            values['checked'] = (value.token == context.responsible) and "checked" or ""
            values['value'] = value.token
            values['label'] = value.title
            options.append(values)
        return options

    @property
    def available_priority(self):
        vocab = [_(u'Baixa'), _(u'Normal'), _(u'Alta')]
        return vocab

    @property
    def priority_for_display(self):
        """Get the available priorities for this issue.
        """
        vocab = [_(u'Baixa'), _(u'Normal'), _(u'Alta')]
        options = []
        for value in vocab:
            checked = (value == self.context.priority) and "checked" or ""
            options.append(dict(value=value, label=value,
                checked=checked))
        return options

    def render(self):
        form = self.request.form
        context = aq_inner(self.context)
        response_text = form.get('response', u'')
        new_response = Response(response_text)
        folder = IResponseContainer(self.context)

        issue_has_changed = False
        transition = form.get('transition', u'')
        if transition and transition in self.available_transitions:
            wftool = getToolByName(context, 'portal_workflow')
            before = wftool.getInfoFor(context, 'review_state')
            before = wftool.getTitleForStateOnType(before, 's17.app.taskmanager.task')
            wftool.doActionFor(context, transition)
            after = wftool.getInfoFor(context, 'review_state')
            after = wftool.getTitleForStateOnType(after, 's17.app.taskmanager.task')
            new_response.add_change('review_state', _(u'Task state'),
                before, after)
            issue_has_changed = True

        options = [
            ('priority', _(u'Priority'), 'available_priority'),
#            ('responsible', _(u'Responsible'),'available_responsibles'),
        ]
        # Changes that need to be applied to the issue (apart from
        # workflow changes that need to be handled separately).
        changes = {}
        for option, title, vocab in options:
            new = form.get(option, u'')
            if new and new in self.__getattribute__(vocab):
                current = context.__getattribute__(option)
                if current != new:
                    changes[option] = new
                    new_response.add_change(option, title,
                        current, new)
                    issue_has_changed = True

        if len(response_text) == 0 and not issue_has_changed:
            status = IStatusMessage(self.request)
            msg = _(u"No response text added and no issue changes made.")
            msg = translate(msg, 's17.app.taskmanager', context=self.request)
            status.addStatusMessage(msg, type='error')
        else:
            # Apply changes to issue
            self.update(**changes)
            # Add response
            folder.add(new_response)
        self.request.response.redirect(context.absolute_url())