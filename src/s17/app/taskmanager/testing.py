# -*- coding: utf-8 -*-

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import s17.app.taskmanager
        self.loadZCML(package=s17.app.taskmanager)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 's17.app.taskmanager:default')
        pl = portal.portal_languages
        if pl.getDefaultLanguage() != 'pt-br':
            pl.setDefaultLanguage('pt-br')
        from zope.component import getGlobalSiteManager
        from s17.app.taskmanager.subscribers import set_task_initial_date
        gsm = getGlobalSiteManager()
        gsm.unregisterHandler(set_task_initial_date)

FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='s17.app.taskmanager:Integration',
    )
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='s17.app.taskmanager:Functional',
    )
