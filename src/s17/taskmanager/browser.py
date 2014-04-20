# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from collective.watcherlist.interfaces import IWatcherList
from datetime import date
from five import grok
from plone import api
from plone.directives import dexterity
from plone.memoize.view import memoize
from s17.taskmanager import MessageFactory as _
from s17.taskmanager.adapters import IResponseContainer
from s17.taskmanager.adapters import Response
from s17.taskmanager.content import ITask
from s17.taskmanager.content import ITaskPanel
from zope.component import getUtility
from zope.lifecycleevent import modified
from zope.schema.interfaces import IVocabularyFactory

grok.templatedir('templates')


class WatcherView(grok.View):
    grok.context(ITask)
    grok.name('watching')
    grok.require('zope2.View')

    def render(self):
        context = aq_inner(self.context)
        watchers = IWatcherList(context)
        watchers.toggle_watching()
        self.request.RESPONSE.redirect(context.absolute_url())


class BaseView:

    @property
    @memoize
    def can_edit_response(self):
        context = aq_inner(self.context)
        mt = api.portal.get_tool('portal_membership')
        return mt.checkPermission('Modify portal content', context)

    @property
    @memoize
    def can_delete_response(self):
        context = aq_inner(self.context)
        mt = api.portal.get_tool('portal_membership')
        return mt.checkPermission('Delete objects', context)

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
                {'checked': 'checked', 'value': '', 'label': _('Nobody')},
            ]
        else:
            options = [
                {'checked': '', 'value': '', 'label': _('Nobody')},
            ]
        for value in users:
            values = {}
            values['checked'] = (value.token == self.res) and 'checked' or ''
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
        membership = api.portal.get_tool('portal_membership')
        if not membership.checkPermission('Modify portal content', context):
            return []

        wftool = api.portal.get_tool('portal_workflow')
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
            checked = (value == self.priority) and 'checked' or ''
            options.append(
                dict(value=value, label=vocab[value], checked=checked))
        return options

    @property
    def available_priorities(self):
        vocab = {1: _(u'High'), 2: _(u'Normal'), 3: _(u'Low')}
        return vocab


class TaskPanelView(grok.View):
    grok.context(ITaskPanel)
    grok.name('view')
    grok.template('taskpanel_view')
    grok.require('zope2.View')

    def get_fullname(self, username):
        """Return the fullname of user specified, or its username if fullname
        is not set.
        """
        if username:
            user = api.user.get(username=username)
            if user:
                fullname = user.getProperty('fullname')
                return fullname if fullname else username

    def tasks(self):
        """Return all tasks in the Task Panel.
        """
        catalog = api.portal.get_tool('portal_catalog')
        results = catalog(
            object_provides=ITask.__identifier__,
            path='/'.join(self.context.getPhysicalPath())
        )

        tasks = []
        for i in results:
            obj = i.getObject()
            t = dict(
                title=obj.title,
                url=i.getURL(),
                status=i.review_state.capitalize(),
                responsible=self.get_fullname(obj.responsible),
                priority=obj.priority,
            )
            tasks.append(t)
        return tasks


class TaskView(dexterity.DisplayForm, BaseView):
    grok.context(ITask)
    grok.name('view')
    grok.template('task_view')
    grok.require('zope2.View')

    calendar_type = 'gregorian'

    popup_calendar_icon = '.css("background","url(popup_calendar.png)")'\
                          '.css("height", "16px")'\
                          '.css("width", "16px")'\
                          '.css("display", "inline-block")'\
                          '.css("vertical-align", "middle")'
    value = ('', '', '')

    jquerytools_dateinput_config = 'selectors: true, '\
                                   'trigger: true, '\
                                   'yearRange: [-10, 10]'

    def images(self):
        """Return a list of image objects inside the Task.
        """
        return self.context.listFolderContents({'portal_type': 'Image'})

    def files(self):
        """Return a list of file objects inside the Task.
        """
        return self.context.listFolderContents({'portal_type': 'File'})

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

        return """
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
            </script>""" % dict(id='date', name='date',
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
        mt = api.portal.get_tool('portal_membership')
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
        return self.available_priorities[priority]


class CreateResponse(grok.View, BaseView):
    grok.context(ITask)
    grok.name('create-response')
    grok.require('zope2.View')

    def _valid_values(self, fieldname):
        """Return a vocabulary of valid values for a field name.
        """
        if fieldname == 'priority':
            return self.available_priorities
        elif fieldname == 'responsible':
            users = getUtility(
                IVocabularyFactory, name=u'plone.app.vocabularies.Users')
            users = users(self.context)
            return [v.token for v in users]
        else:
            raise AttributeError(_(u'Invalid fieldname specified'))

    def _update_text_field(self, fieldname):
        """Compare the value of the field with the one on the request and
        change it if different.

        :param fieldname: [required] value to be converted
        :type fieldname: string
        :returns: a tuple containing the values (old, new) or False is no
                  update was made
        :rtype: tuple of boolean
        """
        updated = False
        new = self.request.form.get(fieldname, None)
        if new in self._valid_values(fieldname):
            old = getattr(self.context, fieldname)
            if old != new:
                setattr(self.context, fieldname, new)
                updated = (old, new)
        return updated

    def _update_workflow(self):
        """Make the workflow transition defined on the request, if available.

        :returns: a tuple containing the values (old, new) or False is no
                  update was made
        :rtype: tuple of boolean
        """
        updated = False
        transition = self.request.form.get('transition', None)
        if transition and (transition in self.available_transitions):
            wftool = api.portal.get_tool('portal_workflow')
            old = wftool.getInfoFor(self.context, 'review_state')
            old = wftool.getTitleForStateOnType(old, 'Task')
            wftool.doActionFor(self.context, transition)
            new = wftool.getInfoFor(self.context, 'review_state')
            new = wftool.getTitleForStateOnType(new, 'Task')
            return (old, new)
        return updated

    def _update_date(self):
        """Compare the value of the provided_date field with the one on the
        request and change it if different.

        :returns: a tuple containing the values (old, new) or False is no
                  update was made
        :rtype: tuple of boolean
        """
        updated = False
        form = self.request.form
        # the date came split in 3 different fields
        day = form.get('date-day', None)
        month = form.get('date-month', None)
        year = form.get('date-year', None)

        if day == '' or year == '':
            # either there were no changes or we want to clear current value
            new = None
        else:
            try:
                year, month, day = map(int, (year, month, day))
                new = date(year, month, day)
            except TypeError, ValueError:
                raise ValueError(_(u'Invalid date specified'))

        old = self.context.provided_date
        if old != new:
            self.context.provided_date = new
            return (old, new)

        return updated

    def render(self):
        form = self.request.form
        task_has_changed = False

        # XXX: I do not get the point on storing the responsible on the
        #      response annotation; that information is not being used
        #      anywhere so this could be way simpler
        current_responsible = self.context.responsible
        response_text = form.get('response', u'')
        responsible = form.get('responsible', u'')
        if responsible != current_responsible:
            self.context.responsible = responsible
            task_has_changed = True
            new_response = Response(response_text, responsible)
        else:
            new_response = Response(response_text)

        result = self._update_workflow()
        if result:
            old, new = result
            new_response.add_change('review_state', _(u'State'), old, new)
            task_has_changed = True

        result = self._update_text_field('priority')
        if result:
            old, new = result
            new_response.add_change('priority', _(u'Priority'), old, new)
            task_has_changed = True

        result = self._update_text_field('responsible')
        if result:
            old, new = result
            new_response.add_change('responsible', _(u'Responsible'), old, new)
            task_has_changed = True

        result = self._update_date()
        if result:
            old, new = result
            new_response.add_change('provided_date', _(u'Expected date'), old, new)
            task_has_changed = True

        if len(response_text) == 0 and not task_has_changed:
            msg = _(u'No response text added and no issue changes made.')
            api.portal.show_message(message=msg, request=self.request)
        else:
            folder = IResponseContainer(self.context)
            folder.add(new_response)
        self.request.response.redirect(self.context.absolute_url())


class EditResponse(grok.View, BaseView):
    grok.context(ITask)
    grok.name('edit-response')
    grok.require('zope2.View')
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
    grok.name('save-response')
    grok.require('zope2.View')

    def render(self):
        folder = IResponseContainer(self.context)
        form = self.request.form
        context = aq_inner(self.context)
        if not self.can_edit_response:
            msg = _(u'You are not allowed to edit responses.')
            api.portal.show_message(message=msg, request=self.request, type='error')
        else:
            response_id = form.get('response_id', None)
            if response_id is None:
                msg = _(u'No response selected for saving.')
                api.portal.show_message(message=msg, request=self.request, type='error')
            elif folder[response_id] is None:
                msg = _(u'Response does not exist anymore; perhaps it was removed by another user.')
                api.portal.show_message(message=msg, request=self.request, type='error')
            else:
                response = folder[response_id]
                response_text = form.get('response', u'')
                response.text = response_text
                msg = _(
                    u'Changes saved to response id ${response_id}.',
                    mapping=dict(response_id=response_id)
                )
                api.portal.show_message(message=msg, request=self.request)
                modified(response, context)
        self.request.response.redirect(context.absolute_url())


class DeleteResponse(grok.View, BaseView):
    grok.context(ITask)
    grok.name('delete-response')
    grok.require('zope2.View')

    def render(self):
        folder = IResponseContainer(self.context)
        context = aq_inner(self.context)

        if not self.can_delete_response:
            msg = _(u'You are not allowed to delete responses.')
            api.portal.show_message(message=msg, request=self.request, type='error')
        else:
            response_id = self.request.form.get('response_id', None)
            if response_id is None:
                msg = _(u'No response selected for removal.')
                api.portal.show_message(message=msg, request=self.request, type='error')
            else:
                try:
                    response_id = int(response_id)
                except ValueError:
                    msg = _(
                        u'Response id ${response_id} is no integer so it cannot be removed.',
                        mapping=dict(response_id=response_id)
                    )
                    api.portal.show_message(message=msg, request=self.request, type='error')
                    self.request.response.redirect(context.absolute_url())
                    return
                if response_id >= len(folder):
                    msg = _(
                        u'Response id ${response_id} does not exist so it cannot be removed.',
                        mapping=dict(response_id=response_id)
                    )
                    api.portal.show_message(message=msg, request=self.request, type='error')
                else:
                    folder.delete(response_id)
                    msg = _(
                        u'Removed response id ${response_id}.',
                        mapping=dict(response_id=response_id)
                    )
                    api.portal.show_message(message=msg, request=self.request)

        self.request.response.redirect(context.absolute_url())
