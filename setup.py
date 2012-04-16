# -*- coding:utf-8 -*-
import os
from setuptools import setup, find_packages

version = '0.1'

long_description = open("README.rst").read() + "\n" +\
                   open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +\
                   open(os.path.join("docs", "CREDITS.txt")).read() + "\n" +\
                   open(os.path.join("docs", "HISTORY.txt")).read()


# TODO: move this to another place
def get_install_requirements():
    """ XXX: document me!
    """
    import ConfigParser
    path = os.path.join('src', 's17', 'app', 'taskmanager', 'dependencies.txt')
    requirements = []
    defaults = dict(version='')
    config = ConfigParser.SafeConfigParser(defaults)
    config.read([path])
    for section in config.sections():
        version = config.get(section, 'version')
        if version and version[0].isdigit():
            version = '==' + version
        requirements.append('%s%s' % (section, version))
    return requirements

setup(name='s17.app.taskmanager',
      version=version,
      description="",
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='python plone zope simples_consultoria',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='http://www.simplesconsultoria.com.br',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['s17', 
                         's17.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools','plone.namedfile[blobs]'] + get_install_requirements(),
      extras_require={
        'test': ['plone.app.testing'],
        },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )