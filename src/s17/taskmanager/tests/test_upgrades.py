# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityFTI
from s17.taskmanager.testing import INTEGRATION_TESTING
from zope.component import getUtility

import unittest


class UpgradeTestCaseBase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self, from_version, to_version):
        self.portal = self.layer['portal']
        self.setup = self.portal['portal_setup']
        self.profile_id = u's17.taskmanager:default'
        self.from_version = from_version
        self.to_version = to_version

    def _get_upgrade_step(self, title):
        """Get one of the upgrade steps.

        Keyword arguments:
        title -- the title used to register the upgrade step
        """
        self.setup.setLastVersionForProfile(self.profile_id, self.from_version)
        upgrades = self.setup.listUpgrades(self.profile_id)
        steps = [s for s in upgrades[0] if s['title'] == title]
        return steps[0] if steps else None

    def _do_upgrade_step(self, step):
        """Execute an upgrade step.

        Keyword arguments:
        step -- the step we want to run
        """
        request = self.layer['request']
        request.form['profile_id'] = self.profile_id
        request.form['upgrades'] = [step['id']]
        self.setup.manage_doUpgrades(request=request)

    def _how_many_upgrades_to_do(self):
        self.setup.setLastVersionForProfile(self.profile_id, self.from_version)
        upgrades = self.setup.listUpgrades(self.profile_id)
        return len(upgrades[0])


class Upgrade5to6TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'1000', u'1001')

    def test_upgrade_to_1001_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertTrue(version >= self.to_version)
        self.assertEqual(self._how_many_upgrades_to_do(), 1)

    def test_update_content_type_information(self):
        # check if the upgrade step is registered
        title = u'Update content type information'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        fti = getUtility(IDexterityFTI, name='TaskPanel')
        fti.icon_expr = 'string:${portal_url}/++resource++s17.taskmanager/taskfolder_icon.png'
        fti.schema = 's17.taskmanager.content.ITaskFolder'
        fti.klass = 'plone.dexterity.content.Container'

        fti = getUtility(IDexterityFTI, name='Task')
        fti.schema = 's17.taskmanager.content.ITask'
        fti.klass = 'plone.dexterity.content.Container'

        # run the upgrade step and validate the update
        self._do_upgrade_step(step)

        fti = getUtility(IDexterityFTI, name='TaskPanel')
        self.assertEqual(
            fti.getIcon(), '++resource++s17.taskmanager/taskpanel_icon.png')
        self.assertEqual(fti.schema, 's17.taskmanager.interfaces.ITaskPanel')
        self.assertEqual(fti.klass, 's17.taskmanager.content.TaskPanel')

        fti = getUtility(IDexterityFTI, name='Task')
        self.assertEqual(fti.schema, 's17.taskmanager.interfaces.ITask')
        self.assertEqual(fti.klass, 's17.taskmanager.content.Task')
