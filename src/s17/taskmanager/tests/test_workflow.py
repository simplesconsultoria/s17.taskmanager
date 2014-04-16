# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.WorkflowCore import WorkflowException
from s17.taskmanager.testing import INTEGRATION_TESTING

import unittest

ctype = 'Task'
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
        self.portal.invokeFactory('TaskPanel', 'test-folder')
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
        self.wt.doActionFor(self.obj, 'assign')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'assigned')
        self.wt.doActionFor(self.obj, 'close')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')

    def test_tasks_can_be_reopened(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.wt.doActionFor(self.obj, 'close')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')
        self.wt.doActionFor(self.obj, 'reopen')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'opened')
        self.wt.doActionFor(self.obj, 'reject')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')
        self.wt.doActionFor(self.obj, 'reopen')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'opened')
        self.wt.doActionFor(self.obj, 'assign')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'assigned')
        self.wt.doActionFor(self.obj, 'close')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')
        self.wt.doActionFor(self.obj, 'reopen')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'opened')
        self.wt.doActionFor(self.obj, 'close')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')

    def test_workflow_direct(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.wt.doActionFor(self.obj, 'close')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')

    def test_workflow_transitions_not_allowed(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.wt.doActionFor(self.obj, 'assign')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'assigned')
        # We cannot open a assigned task
        self.assertRaises(
            WorkflowException, self.wt.doActionFor, self.obj, 'reopen')

        # We can however, close it
        self.wt.doActionFor(self.obj, 'close')

        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')

        # we cannot assigned a closed task

        self.assertRaises(
            WorkflowException, self.wt.doActionFor, self.obj, 'assign')
