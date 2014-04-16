# -*- coding: utf-8 -*-
from plone.testing import layered
from s17.taskmanager.testing import FUNCTIONAL_TESTING

import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            robotsuite.RobotTestSuite('test_tasks.txt'),
            layer=FUNCTIONAL_TESTING),
    ])
    return suite
