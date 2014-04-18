# -*- coding: utf-8 -*-
from plone import api
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IATImage
from s17.taskmanager.testing import INTEGRATION_TESTING

import unittest


class ViewTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        with api.env.adopt_roles(['Manager']):
            taskpanel = api.content.create(self.portal, 'TaskPanel', 'taskpanel')
        self.task = api.content.create(taskpanel, 'Task', 'task')

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
