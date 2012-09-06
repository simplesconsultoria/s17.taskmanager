# -*- coding: utf-8 -*-

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import setRoles
from plone.app.testing import login

from s17.app.taskmanager.testing import INTEGRATION_TESTING

ctype = 's17.app.taskmanager.task'
workflow_id = 'taskmanager_workflow'


class WorkflowTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def _loginAsManager(self):
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def _transition_poll(self, poll, action):
        self._loginAsManager()
        self.wt.doActionFor(poll, action)

    def setUp(self):
        self.portal = self.layer['portal']
        self.wt = self.portal['portal_workflow']
        portal_membership = self.portal['portal_membership']
        self.checkPermission = portal_membership.checkPermission
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('s17.app.taskmanager.taskfolder', 'test-folder')
        self.folder = self.portal['test-folder']
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        self.folder.invokeFactory(ctype, 'obj')
        self.obj = self.folder['obj']

    def test_workflow_installed(self):
        ids = self.wt.getWorkflowIds()
        self.assertTrue(workflow_id in ids)

    def test_default_workflow(self):
        chain = self.wt.getChainForPortalType(self.obj.portal_type)
        self.assertEqual(len(chain), 1)
        self.assertEqual(chain[0], workflow_id)

    def test_workflow_initial_state(self):
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'opened')

    def test_workflow_all_stages(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.fail(NotImplemented)

    def test_workflow_direct(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.fail(NotImplemented)

    def test_workflow_transitions_not_allowed(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.fail(NotImplemented)

    def test_workflow_permissions(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.fail(NotImplemented)
