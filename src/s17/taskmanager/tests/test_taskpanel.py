# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from plone.app.referenceablebehavior.referenceable import IReferenceable
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.uuid.interfaces import IAttributeUUID
from s17.taskmanager.content import ITaskPanel
from s17.taskmanager.testing import INTEGRATION_TESTING
from zope.component import createObject
from zope.component import queryUtility

import unittest

ctype = 'TaskPanel'


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

        self.folder.invokeFactory(ctype, 'obj')
        self.obj = self.folder['obj']

    def test_adding(self):
        self.assertTrue(ITaskPanel.providedBy(self.obj))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name=ctype)
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name=ctype)
        schema = fti.lookupSchema()
        self.assertEqual(ITaskPanel, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name=ctype)
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ITaskPanel.providedBy(new_object))

    def test_is_referenceable(self):
        self.assertTrue(IReferenceable.providedBy(self.obj))
        self.assertTrue(IAttributeUUID.providedBy(self.obj))

    def test_allowed_content_types(self):
        expected = ['Task']
        allowed_types = [t.getId() for t in self.obj.allowedContentTypes()]
        self.assertListEqual(expected, allowed_types)

        # trying to add any other content type raises an error
        self.assertRaises(ValueError,
                          self.obj.invokeFactory, 'Document', 'foo')

        try:
            self.obj.invokeFactory('Task', 'foo')
        except Unauthorized:
            self.fail()
