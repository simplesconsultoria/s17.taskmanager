# -*- coding: utf-8 -*-

from plone import api
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing.z2 import ZSERVER_FIXTURE


def create_test_users_and_groups():
    test_users = [
        ('manager', 'manager@foo.com', 'manager'),
        ('user1', 'user1@foo.com', 'user1'),
        ('user2', 'user2@foo.com', 'user2'),
    ]

    api.group.create(groupname='staff', roles=['Site Administrator'])

    for username, email, password in test_users:
        if api.user.get(username=username) is None:
            api.user.create(username=username, email=email, password=password)
            api.group.add_user(groupname='staff', username=username)


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import s17.taskmanager
        self.loadZCML(package=s17.taskmanager)

    def setUpPloneSite(self, portal):
        create_test_users_and_groups()
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

ROBOT_TESTING = FunctionalTesting(
    bases=(FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, ZSERVER_FIXTURE),
    name='s17.taskmanager:Robot',
)
