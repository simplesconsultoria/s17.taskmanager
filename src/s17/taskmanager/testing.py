# -*- coding: utf-8 -*-

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.testing.z2 import ZSERVER_FIXTURE


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import s17.taskmanager
        self.loadZCML(package=s17.taskmanager)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 's17.taskmanager:default')

        from zope.component import getGlobalSiteManager
        from s17.taskmanager.subscribers import set_task_initial_date
        from s17.taskmanager.subscribers import added_response

        gsm = getGlobalSiteManager()
        gsm.unregisterHandler(set_task_initial_date)
        gsm.unregisterHandler(added_response)

FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='s17.taskmanager:Integration',
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, ZSERVER_FIXTURE,),
    name='s17.taskmanager:Functional',
)
