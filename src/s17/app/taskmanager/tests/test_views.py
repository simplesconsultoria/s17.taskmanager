# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.interface import alsoProvides, directlyProvides

from plone.app.customerize import registration

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

from Products.CMFPlone.utils import _createObjectByType

from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from s17.app.taskmanager.content import ITask, ITaskFolder
from s17.app.taskmanager.testing import INTEGRATION_TESTING


class BrowserLayerTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('s17.app.taskmanager.taskfolder',\
            'tasks', title='Tasks')
        folder = self.portal['tasks']
        folder.invokeFactory('s17.app.taskmanager.task',\
            'task', title='Task')
        self.task = folder['task']

    def test_views_registered_task(self):
        views = ['view','create_response','edit_response','save_response',\
                 'delete_response','watching']
        registered = [v.name for v in registration.getViews(IDefaultBrowserLayer)]
        # empty set only if all 'views' are 'registered'
        self.assertEquals(set(views) - set(registered), set([]))

    def test_watcher_view(self):
        name = '@@watching'
        try:
            self.task.unrestrictedTraverse(name)
        except AttributeError:
            self.fail('%s has no view %s' % (self.task, name))

        view = self.task.restrictedTraverse(name)
        self.assertTrue(view.render() is None)

    def test_create_response_view(self):
        name = '@@create_response'
        try:
            self.task.unrestrictedTraverse(name)
        except AttributeError:
            self.fail('%s has no view %s' % (self.task, name))

        view = self.task.restrictedTraverse(name)
        view.update()

        responsibles = [{'checked': 'checked',
                         'value': 'nobody',
                         'label': u'Nobody'},
                        {'checked': '',
                         'value': 'test_user_1_',
                         'label': 'test-user'}]

        self.assertFalse(responsibles != view.responsibles_for_display)

#        import pdb;pdb.set_trace()


#
#        self.assertEquals(0, len(view.download()))
#        self.assertEquals(0, len(view.uploaded()))
#
#        # add a file as customer; skip permissions
#        _createObjectByType('File', self.client, 'file-not-marked')
#        _file = self.client['file-not-marked']
#        self.assertFalse(ISOAPFileMarker.providedBy(_file))
#
#        self.assertEquals(0, len(view.download()))
#        self.assertEquals(1, len(view.uploaded()))
#
#        self.make_user_member_of_soap()
#        self.assertEquals(1, len(view.download()))
#        self.assertEquals(0, len(view.uploaded()))
#
#        # add a file as Soap staff
#        _createObjectByType('File', self.client, 'file-marked')
#        _file = self.client['file-marked']
#        alsoProvides(_file, ISOAPFileMarker)
#        _file.reindexObject()
#        self.assertTrue(ISOAPFileMarker.providedBy(_file))
#
#        self.assertEquals(1, len(view.download()))
#        self.assertEquals(1, len(view.uploaded()))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)