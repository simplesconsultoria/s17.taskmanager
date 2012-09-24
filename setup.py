# -*- coding:utf-8 -*-

import os
from setuptools import setup, find_packages

version = '1.0a4.dev0'
long_description = open("README.txt").read() + "\n" + \
                   open(os.path.join("docs", "INSTALL.txt")).read() + "\n" + \
                   open(os.path.join("docs", "CREDITS.txt")).read() + "\n" + \
                   open(os.path.join("docs", "HISTORY.txt")).read()

setup(name='s17.taskmanager',
      version=version,
      description="",
      long_description=long_description,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
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
      namespace_packages=['s17',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'Products.CMFPlone>=4.1',
        'plone.app.dexterity>=1.2.1',
        'plone.app.referenceablebehavior',
        'plone.app.relationfield',
        'plone.namedfile[blobs]',
        'plone.principalsource',
        'collective.watcherlist',
        'collective.upload>=1.0b2',
        ],
      extras_require={
        'test': ['plone.app.testing'],
        },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
