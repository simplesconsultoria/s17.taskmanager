# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from s17.taskmanager.notifications import BaseMail
from s17.taskmanager.testing import INTEGRATION_TESTING
from zope.component import getMultiAdapter

import unittest


MAIL_ITEMS = [('MIME-Version', '1.0'),
              ('Content-Type', 'multipart/alternative')]

NEW_TASK_MESSAGE = u'A new task has been submitted by **test_user_1_**.\n\n' \
                   u'Task Information\n' \
                   u'----------------\n\n' \
                   u'Task\n  ' \
                   u'Task (http://nohost/plone/tasks/task)\n\n\n' \
                   u'**Task Details**::\n\n' \
                   u'No details in the task \n\n\n' \
                   u'* This is an automated email, please do not reply - '

NEW_TASK_SUBJECT = u'[New task: Task]'

NEW_RESPONSE_MESSAGE = u'A new response has been given to the task **Task**\n' \
                       u'by **test_user_1_**.\n\n' \
                       u'Response Information\n' \
                       u'--------------------\n\n' \
                       u'Task\n  ' \
                       u'Task (http://nohost/plone/tasks/task)\n\n\n\n\n\n' \
                       u'* This is an automated email, please do not reply - '

NEW_RESPONSE_SUBJECT = u'Re: Task'

CLOSED_TASK_MESSAGE = u'The task **Task** has been marked as resolved by ' \
                      u'**test-user**.\n' \
                      u'Please visit the task and either confirm that it has been\n' \
                      u'satisfactorily resolved or re-open it.\n\n' \
                      u'Response Information\n--------------------\n\n' \
                      u'Task\n  ' \
                      u'Task (http://nohost/plone/tasks/task)\n\n\n' \
                      u'* This is an automated email, please do not reply - '

CLOSED_TASK_SUBJECT = u'[Resolved #Task]'


class TestNotifications(unittest.TestCase):
    """Test email notifications
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('TaskPanel', 'tasks', title='Tasks')
        folder = self.portal['tasks']
        folder.invokeFactory('Task', 'task', title='Task')
        self.task = folder['task']

    def _baseMail(self):
        return BaseMail(self.portal, self.request)

    def test_plain(self):
        mailer = self._baseMail()
        self.assertTrue(mailer.plain == '')

    def test_subject(self):
        mailer = self._baseMail()
        self.assertTrue(mailer.subject == '[No subject]')

    def test_base_render(self):
        mailer = self._baseMail()
        self.assertTrue(mailer.render is not None)
        self.assertTrue(mailer.prepare_email_message() is None)

    def test_new_task_mail(self):
        new_task_mail = getMultiAdapter(
            (self.task, self.request), name=u'new-task-mail')

        for item in new_task_mail.prepare_email_message().items():
            self.assertTrue(item in MAIL_ITEMS)

        # self.assertTrue(new_task_mail.plain == NEW_TASK_MESSAGE)
        self.assertTrue(new_task_mail.subject == NEW_TASK_SUBJECT)

    def test_new_response_mail(self):
        new_response_mail = getMultiAdapter(
            (self.task, self.request), name=u'new-response-mail')
        create_response = getMultiAdapter(
            (self.task, self.request), name=u'create-response')

        self.request.form['responsible'] = 'someuser'
        # we need to provide some date fields to avoid ValueError
        self.request.form['date-day'] = self.request.form['date-year'] = ''
        create_response.render()

        self.request.set('response_id', 0)

        for item in new_response_mail.prepare_email_message().items():
            self.assertTrue(item in MAIL_ITEMS)

        self.assertTrue(new_response_mail.plain == NEW_RESPONSE_MESSAGE)
        self.assertTrue(new_response_mail.subject == NEW_RESPONSE_SUBJECT)

    def test_closed_task_mail(self):
        closed_task_mail = getMultiAdapter(
            (self.task, self.request), name=u'closed-task-mail')

        for item in closed_task_mail.prepare_email_message().items():
            self.assertTrue(item in MAIL_ITEMS)

        self.assertTrue(closed_task_mail.plain == CLOSED_TASK_MESSAGE)
        self.assertTrue(closed_task_mail.subject == CLOSED_TASK_SUBJECT)
