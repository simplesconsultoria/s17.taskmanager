# -*- coding: utf-8 -*-
from datetime import date
from plone import api
from plone.testing.z2 import Browser
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IATImage
from s17.taskmanager.testing import FUNCTIONAL_TESTING
from s17.taskmanager.testing import INTEGRATION_TESTING

import unittest


class BaseTaskViewTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        with api.env.adopt_roles(['Manager']):
            taskpanel = api.content.create(self.portal, 'TaskPanel', 'taskpanel')
        self.task = api.content.create(taskpanel, 'Task', 'task')


class ViewTestCase(BaseTaskViewTestCase):

    def test_images(self):
        view = api.content.get_view('view', self.task, self.request)
        self.assertEqual(len(view.images()), 0)
        api.content.create(self.task, 'Image', 'image')
        self.assertEqual(len(view.images()), 1)
        self.assertTrue(IATImage.providedBy(view.images()[0]))
        api.content.delete(self.task['image'])
        self.assertEqual(len(view.images()), 0)

    def test_files(self):
        view = api.content.get_view('view', self.task, self.request)
        self.assertEqual(len(view.files()), 0)
        api.content.create(self.task, 'File', 'file')
        self.assertEqual(len(view.files()), 1)
        self.assertTrue(IATFile.providedBy(view.files()[0]))
        api.content.delete(self.task['file'])
        self.assertEqual(len(view.files()), 0)


class CreateResponseTestCase(BaseTaskViewTestCase):

    def test_update_text_field(self):
        self.task.priority = 1
        self.task.responsible = 'user1'
        self.request.form = dict(priority=2, responsible='user1')
        view = api.content.get_view('create-response', self.task, self.request)

        self.assertEqual(view._update_text_field('priority'), (1, 2))
        self.assertFalse(view._update_text_field('responsible'))

        with self.assertRaises(AttributeError):
            view._update_text_field('invalid')

    def test_update_date(self):
        this_month = date.today().replace(day=1)  # first day of this month
        next_year = this_month.replace(year=this_month.year + 1)

        self.task.provided_date = this_month
        # we will use a trailing 0 to test the way the widget behaves
        self.request.form = {
            'date-day': '{0:02}'.format(this_month.day),
            'date-month': this_month.month,
            'date-year': this_month.year,
        }
        view = api.content.get_view('create-response', self.task, self.request)
        self.assertFalse(view._update_date())

        self.request.form['date-year'] = this_month.year + 1
        view = api.content.get_view('create-response', self.task, self.request)
        self.assertEqual(view._update_date(), (this_month, next_year))

        # setting day or year to an empty string will clear the date
        self.request.form['date-year'] = ''
        view = api.content.get_view('create-response', self.task, self.request)
        self.assertEqual(view._update_date(), (next_year, None))

        with self.assertRaises(ValueError):
            self.request.form['date-year'] = 'invalid'
            view = api.content.get_view('create-response', self.task, self.request)
            view._update_date()

        with self.assertRaises(ValueError):
            self.request.form['date-year'] = '-1'
            view = api.content.get_view('create-response', self.task, self.request)
            view._update_date()


class DeleteResponseTestCase(BaseTaskViewTestCase):

    layer = FUNCTIONAL_TESTING

    @unittest.skip('FIXME: getting notFoundError, why? missing layer?')
    def test_render(self):
        browser = Browser(self.app)
        browser.handleErrors = False
        task = self.task.absolute_url()

        browser.open(task + '/@@delete-response')
        self.assertIn('No response selected for removal', browser.contents)

        browser.open(task + '/@@delete-response?response_id=invalid')
        self.assertIn(
            'Response id invalid is no integer so it cannot be removed',
            browser.contents
        )

        browser.open(task + '/@@delete-response?response_id=123')
        self.assertIn(
            'Response id 123 does not exist so it cannot be removed',
            browser.contents
        )
