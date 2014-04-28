***************
s17.taskmanager
***************

.. contents:: Table of Contents

Life, the Universe, and Everything
==================================

A package containing a Dexterity-based content type and behaviors to provide a simple structure for managing tasks.

Features
--------

- Tasks folder that contains tasks
- One person responsible for managing the tasks
- Define who can add tasks in the tasks folder
- One person responsible for each task
- Any user can watch the tasks

Mostly Harmless
===============

.. image:: https://secure.travis-ci.org/simplesconsultoria/s17.taskmanager.png?branch=master
    :alt: Travis CI badge
    :target: http://travis-ci.org/simplesconsultoria/s17.taskmanager

.. image:: https://coveralls.io/repos/simplesconsultoria/s17.taskmanager/badge.png?branch=master
    :alt: coveralls badge
    :target: https://coveralls.io/r/simplesconsultoria/s17.taskmanager

.. image:: https://pypip.in/d/s17.taskmanager/badge.png
    :target: https://pypi.python.org/pypi/s17.taskmanager/
    :alt: Downloads

Got an idea? Found a bug? Let us know by `opening a support ticket`_.

.. _`opening a support ticket`: https://github.com/simplesconsultoria/s17.taskmanager/issues

Don't Panic
===========

Installation
------------

To enable this product on a buildout based installation:

#. Edit your buildout.cfg and add ``s17.taskmanager`` to the list of eggs to install::

    [buildout]
    ...
    eggs =
        s17.taskmanager
    zcml =
        s17.taskmanager

After updating the configuration you need to run the ''bin/buildout'', which will take care of updating your system.

Go to the 'Site Setup' page in a Plone site and click on the 'Add-ons' link.

Check the box next to ``s17.taskmanager`` and click the 'Activate' button.

Choose the product (check its checkbox) and click the 'Install' button.

Usage
-----

TBD

Not entirely unlike
===================

`Poi`_
    Poi is an issue tracker product for Plone.

.. _`Poi`: https://pypi.python.org/pypi/Products.Poi
