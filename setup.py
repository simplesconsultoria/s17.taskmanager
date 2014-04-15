# -*- coding:utf-8 -*-

import os
from setuptools import setup, find_packages

version = '1.0b2.dev0'
long_description = open("README.txt").read() + "\n" + \
                   open(os.path.join("docs", "INSTALL.txt")).read() + "\n" + \
                   open(os.path.join("docs", "CREDITS.txt")).read() + "\n" + \
                   open(os.path.join("docs", "HISTORY.txt")).read()

setup(name='s17.taskmanager',
      version=version,
      description="",
      long_description=long_description,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Intended Audience :: End Users/Desktop",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='dexterity plone contenttypes taskmanager',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='http://www.simplesconsultoria.com.br',
      license='GPLv2',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['s17'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'AccessControl',
          'collective.upload',
          'collective.watcherlist',
          'five.grok',
          'plone.api',
          'plone.app.dexterity',
          'plone.app.referenceablebehavior',
          'plone.app.relationfield',
          'plone.app.vocabularies',
          'plone.directives.dexterity',
          'plone.memoize',
          'plone.namedfile [blobs]',
          'Products.ATContentTypes',
          'Products.CMFCore',
          'Products.CMFPlone >=4.2',
          'Products.GenericSetup',
          'setuptools',
          'zope.component',
          'zope.container',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
      ],
      extras_require={
          'test': [
              'plone.app.robotframework',
              'plone.app.testing [robot] >=4.2.2',
              'plone.dexterity',
              'plone.testing',
              'plone.uuid',
              'robotsuite',
          ],
      },
      )
