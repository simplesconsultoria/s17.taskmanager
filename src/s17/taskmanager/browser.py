# -*- coding: utf-8 -*-

from Acquisition import aq_inner

from five import grok

from collective.watcherlist.interfaces import IWatcherList

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.cachedescriptors.property import Lazy
from zope.i18n import translate
from zope.lifecycleevent import modified

from plone.directives import dexterity
from plone.memoize.view import memoize

from Products.CMFPlone.utils import getToolByName
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IATImage
from Products.statusmessages.interfaces import IStatusMessage

from s17.taskmanager.content import ITask, ITaskFolder
from s17.taskmanager.adapters import Response, IResponseContainer
from s17.taskmanager import MessageFactory as _

from datetime import date

grok.templatedir("templates")


class WatcherView(grok.View):
    grok.context(ITask)
    grok.name("watching")
    grok.require("zope2.View")

    def render(self):
        context = aq_inner(self.context)
        watchers = IWatcherList(context)
        watchers.toggle_watching()
        self.request.RESPONSE.redirect(context.absolute_url())


class BaseView:

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
        users_factory = getUtility(IVocabularyFactory, name=u'plone.app.vocabularies.Users')
        users = users_factory(context)
        if not self.res:
            options = [
                {'checked': 'checked', 'value': 'nobody', 'label': _('Nobody')},
            ]
        else:
            options = [
                {'checked': '', 'value': 'nobody', 'label': _('Nobody')},
            ]
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
        if not self.memship.checkPermission('Modify portal content', context):
            return []
        wftool = getToolByName(context, 'portal_workflow')
        transitions = []
        transitions.append(
            dict(value='', label=_(u'No change'), checked='checked'))
        for tdef in wftool.getTransitionsFor(context):
            transitions.append(
                dict(value=tdef['id'], label=tdef['title_or_id'], checked=''))
        return transitions

    @property
    def available_transitions(self):
        """Get the available transitions for this issue.
        """
        return [x['value'] for x in self.transitions_for_display]

    @property
    def priority_for_display(self):
        """Get the available priorities for this issue.
        """
        vocab = {1: _(u'High'), 2: _(u'Normal'), 3: _(u'Low')}
        options = []
        for value in vocab:
            checked = (value == self.priority) and "checked" or ""
            options.append(
                dict(value=value, label=vocab[value], checked=checked))
        return options

    @property
    def available_priority(self):
        vocab = {1: _(u'High'), 2: _(u'Normal'), 3: _(u'Low')}
        return vocab

    @property
    def available_responsibles(self):
        context = aq_inner(self.context)
        users_factory = getUtility(IVocabularyFactory, name=u'plone.app.vocabularies.Users')
        users = users_factory(context)
        if users:
            return [value.token for value in users]
        else:
            return []


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
        ct = getToolByName(self.context, 'portal_catalog')
        tasks = ct(
            object_provides=ITask.__identifier__,
            path='/'.join(self.context.getPhysicalPath())
        )
        if tasks:
            return [dict(title=task.Title,
                         url=task.getURL(),
                         status=task.review_state.capitalize(),
                         responsible=self.responsible(task.getObject()),
                         priority=task.getObject().priority,)
                    for task in tasks]
        else:
            return None


class TaskView(dexterity.DisplayForm, BaseView):
    grok.context(ITask)
    grok.name("view")
    grok.template('task_view')
    grok.require("zope2.View")

    calendar_type = 'gregorian'

    popup_calendar_icon = '.css("background","url(popup_calendar.gif)")'\
                          '.css("height", "16px")'\
                          '.css("width", "16px")'\
                          '.css("display", "inline-block")'\
                          '.css("vertical-align", "middle")'
    value = ('', '', '')

    jquerytools_dateinput_config = 'selectors: true, '\
                                   'trigger: true, '\
                                   'yearRange: [-10, 10]'

    def images(self):
        ct = getToolByName(self.context, 'portal_catalog')
        images = ct(
            object_provides=IATImage.__identifier__,
            path='/'.join(self.context.getPhysicalPath())
        )
        if images:
            images = [image.getObject() for image in images]
            return images
        else:
            return None

    def files(self):
        ct = getToolByName(self.context, 'portal_catalog')
        files = ct(
            object_provides=IATFile.__identifier__,
            path='/'.join(self.context.getPhysicalPath())
        )
        if files:
            return files
        else:
            return None

    def is_watching(self):
        """
        Determine if the current user is watching this task or not.
        """
        context = aq_inner(self.context)
        watchers = IWatcherList(context)
        return watchers.isWatching()

    @property
    def year(self):
        year = self.request.get('date-year', None)
        if year is not None:
            return year
        try:
            year = self.context.provided_date.strftime('%Y')
            return year
        except:
            return self.value[0]

    @property
    def month(self):
        month = self.request.get('date-month', None)
        if month:
            return month
        try:
            month = self.context.provided_date.strftime('%m')
            return month
        except:
            return self.value[1]

    @property
    def day(self):
        day = self.request.get('date-day', None)
        if day is not None:
            return day
        try:
            day = self.context.provided_date.strftime('%d')
            return day
        except:
            return self.value[2]

    def show_jquerytools_dateinput_js(self):
        language = getattr(self.request, 'LANGUAGE', 'en')
        calendar = self.request.locale.dates.calendars[self.calendar_type]
        localize = 'jQuery.tools.dateinput.localize("' + language + '", {'
        localize += 'months: "%s",' % ','.join(calendar.getMonthNames())
        localize += 'shortMonths: "%s",' % ','.join(calendar.getMonthAbbreviations())
        localize += 'days: "%s",' % ','.join(calendar.getDayNames())
        localize += 'shortDays: "%s"' % ','.join(calendar.getDayAbbreviations())
        localize += '});'

        config = 'lang: "%s", ' % language
        value_date = self.value[:3]
        if '' not in value_date:
            config += 'value: new Date("%s/%s/%s"), ' % (value_date)

        config += 'change: function() { ' \
                  'var value = this.getValue("yyyy-m-dd").split("-"); \n' \
                  'jQuery("#%(id)s-year").val(value[0]); \n' \
                  'jQuery("#%(id)s-month").val(value[1]); \n' \
                  'jQuery("#%(id)s-day").val(value[2]); \n' \
                  '}, ' % dict(id='date')
        config += self.jquerytools_dateinput_config

        return '''
            <input type="hidden" name="%(name)s-calendar"
                   id="%(id)s-calendar" />
            <script type="text/javascript">
                if (jQuery().dateinput) {
                    %(localize)s
                    jQuery("#%(id)s-calendar").dateinput({%(config)s}).unbind('change')
                        .bind('onShow', function (event) {
                            var trigger_offset = jQuery(this).next().offset();
                            jQuery(this).data('dateinput').getCalendar().offset(
                                {top: trigger_offset.top+20, left: trigger_offset.left}
                            );
                        });
                    jQuery("#%(id)s-calendar").next()%(popup_calendar_icon)s;
                }
            </script>''' % dict(id='date', name='date',
                                day=self.day, month=self.month, year=self.year,
                                config=config, language=language, localize=localize,
                                popup_calendar_icon=self.popup_calendar_icon)

    @property
    def months(self):
        try:
            selected = int(self.month)
        except:
            selected = -1

        calendar = self.request.locale.dates.calendars['gregorian']
        month_names = calendar.getMonthNames()

        for i, month in enumerate(month_names):
            yield dict(name=month, value=i + 1, selected=i + 1 == selected)

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
        folder = IResponseContainer(context)
        for id, response in enumerate(folder):
            if response is None:
                # Has been removed.
                continue
            html = response.text or u''
            info = dict(id=id, response=response, html=html)
            items.append(info)
        return items

    def get_priority(self):
        priority = self.context.priority
        return self.available_priority[priority]


class CreateResponse(grok.View, BaseView):
    grok.context(ITask)
    grok.name("create_response")
    grok.require("zope2.View")

    # FIXME: this method is way too complex (17)
    def render(self):  # noqa
        form = self.request.form
        context = aq_inner(self.context)

        task_has_changed = False

        try:
            current_responsible = context.__getattribute__('responsible')
        except AttributeError:
            current_responsible = None
        response_text = form.get('response', u'')
        responsible = form.get('responsible', u'')
        if responsible and responsible != current_responsible:
            if responsible == 'nobody':
                responsible = ''
            else:
                responsible = responsible
            self.context.responsible = responsible
            task_has_changed = True
            new_response = Response(response_text, responsible)
        else:
            new_response = Response(response_text)
        folder = IResponseContainer(self.context)

        options = [
            ('priority', _(u'Priority'), 'available_priority'),
            ('responsible', _(u'Responsible'), 'available_responsibles'),
        ]

        # Changes that need to be applied to the issue (apart from
        # workflow changes that need to be handled separately).

        changes = {}
        for option, title, vocab in options:
            new = form.get(option, u'')
            if new and new in self.__getattribute__(vocab):
                try:
                    current = context.__getattribute__(option)
                except AttributeError:
                    current = None
                if option == 'responsible':
                    current = current_responsible
                if current != new:
                    changes[option] = new
                    new_response.add_change(option, title, current, new)
                    task_has_changed = True

        transition = form.get('transition', u'')
        if transition and transition in self.available_transitions:
            wftool = getToolByName(context, 'portal_workflow')
            before = wftool.getInfoFor(context, 'review_state')
            before = wftool.getTitleForStateOnType(before, 's17.taskmanager.task')
            wftool.doActionFor(context, transition)
            after = wftool.getInfoFor(context, 'review_state')
            after = wftool.getTitleForStateOnType(after, 's17.taskmanager.task')
            new_response.add_change('review_state', _(u'Task state'), before, after)
            task_has_changed = True

        try:
            current_priority = context.__getattribute__('priority')
        except AttributeError:
            current_priority = None
        priority = form.get('priority', u'')
        if priority and priority in self.available_priority and priority != current_priority:
            context.priority = priority
            task_has_changed = True

        day = form.get('date-day', None)
        month = form.get('date-month', None)
        if month and len(month) == 1:
            month = '0' + month
        year = form.get('date-year', None)

        if day and month and year:
            value = []
            value.append(year)
            value.append(month)
            value.append(day)
            dateobj = date(*map(int, value))
            try:
                current = context.__getattribute__('provided_date')
            except AttributeError:
                current = None
            context.provided_date = dateobj
            changes['provided_date'] = dateobj
            new_response.add_change(
                'provided_date', _(u'Expected date'), current, dateobj)
            task_has_changed = True

        if len(response_text) == 0 and not task_has_changed:
            status = IStatusMessage(self.request)
            msg = _(u"No response text added and no issue changes made.")
            msg = translate(msg, 's17.taskmanager', context=self.request)
            status.addStatusMessage(msg, type='error')
        else:
            # Apply changes to issue
            self.update(**changes)
            # Add response
            folder.add(new_response)
        self.request.response.redirect(context.absolute_url())


class EditResponse(grok.View, BaseView):
    grok.context(ITask)
    grok.name("edit_response")
    grok.require("zope2.View")
    grok.template('edit_response')

    @property
    @memoize
    def response(self):
        folder = IResponseContainer(self.context)
        form = self.request.form
        response_id = form.get('response_id', None)
        if response_id is None:
            return None
        try:
            response_id = int(response_id)
        except ValueError:
            return None
        if response_id >= len(folder):
            return None
        return folder[response_id]

    @property
    def response_found(self):
        return self.response is not None


class SaveResponse(grok.View, BaseView):
    grok.context(ITask)
    grok.name("save_response")
    grok.require("zope2.View")

    def render(self):
        folder = IResponseContainer(self.context)
        form = self.request.form
        context = aq_inner(self.context)
        status = IStatusMessage(self.request)
        if not self.can_edit_response:
            msg = _(u"You are not allowed to edit responses.")
            msg = translate(msg, 's17.taskmanager', context=self.request)
            status.addStatusMessage(msg, type='error')
        else:
            response_id = form.get('response_id', None)
            if response_id is None:
                msg = _(u"No response selected for saving.")
                msg = translate(msg, 's17.taskmanager', context=self.request)
                status.addStatusMessage(msg, type='error')
            elif folder[response_id] is None:
                msg = _(u"Response does not exist anymore; perhaps it was "
                        "removed by another user.")
                msg = translate(msg, 's17.taskmanager', context=self.request)
                status.addStatusMessage(msg, type='error')
            else:
                response = folder[response_id]
                response_text = form.get('response', u'')
                response.text = response_text
                msg = _(
                    u'Changes saved to response id ${response_id}.',
                    mapping=dict(response_id=response_id)
                )
                msg = translate(msg, 's17.taskmanager', context=self.request)
                status.addStatusMessage(msg, type='info')
                modified(response, context)
        self.request.response.redirect(context.absolute_url())


class DeleteResponse(grok.View, BaseView):
    grok.context(ITask)
    grok.name("delete_response")
    grok.require("zope2.View")

    def render(self):
        folder = IResponseContainer(self.context)
        context = aq_inner(self.context)
        status = IStatusMessage(self.request)

        if not self.can_delete_response:
            msg = _(u"You are not allowed to delete responses.")
            msg = translate(msg, 's17.taskmanager', context=self.request)
            status.addStatusMessage(msg, type='error')
        else:
            response_id = self.request.form.get('response_id', None)
            if response_id is None:
                msg = _(u"No response selected for removal.")
                msg = translate(msg, 's17.taskmanager', context=self.request)
                status.addStatusMessage(msg, type='error')
            else:
                try:
                    response_id = int(response_id)
                except ValueError:
                    msg = _(
                        u'Response id ${response_id} is no integer so it cannot be removed.',
                        mapping=dict(response_id=response_id)
                    )
                    msg = translate(msg, 's17.taskmanager', context=self.request)
                    status.addStatusMessage(msg, type='error')
                    self.request.response.redirect(context.absolute_url())
                    return
                if response_id >= len(folder):
                    msg = _(
                        u'Response id ${response_id} does not exist so it cannot be removed.',
                        mapping=dict(response_id=response_id)
                    )
                    msg = translate(msg, 's17.taskmanager', context=self.request)
                    status.addStatusMessage(msg, type='error')
                else:
                    folder.delete(response_id)
                    msg = _(
                        u'Removed response id ${response_id}.',
                        mapping=dict(response_id=response_id)
                    )
                    msg = translate(msg, 's17.taskmanager', context=self.request)
                    status.addStatusMessage(msg, type='info')
        self.request.response.redirect(context.absolute_url())
