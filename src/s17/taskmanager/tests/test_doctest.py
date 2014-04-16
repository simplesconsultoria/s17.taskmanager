# -*- coding: utf-8 -*-
from plone.testing import layered
from s17.taskmanager.testing import FUNCTIONAL_TESTING

import doctest
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite('tests/functional.txt', package='s17.taskmanager'),
            layer=FUNCTIONAL_TESTING),
    ])
    return suite
