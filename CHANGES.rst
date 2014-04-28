Changelog
=========

There's a frood who really knows where his towel is.

1.0b2 (2014-04-28)
------------------

- A bug that prevented edition of responses because of missing property
  ``wysiwyg_editor`` was fixed.
  [ericof]

- Brazilian Portuguese translations were updated.
  [hvelarde]

- Notification views were renamed to ``create-response``, ``delete-response``,
  ``edit-response`` and ``save-response``.
  [hvelarde]

- Task panel and task views were refactored; some bugs were fixed: information
  displayed was reordered and markup was simplified.
  [hvelarde]

- Fix content type information as previous rename was incomplete (an upgrade
  step is available).
  [hvelarde]

- Support for z3c.autoinclude plugin was removed.
  [hvelarde]

- Package dependencies were updated; dependencies on plone.principalsource,
  unittest2 and zope.app.container were removed. We now depend on plone.api.
  [hvelarde]


1.0b1 (2012-09-28)
------------------

- Test Plone 4.3 compatibility. [hvelarde]

- Deprecate use on Plone 4.1; we will support only Plone>=4.2. [lepri]

- Fix package i18n. [lepri]

- Rename content type from "s17.app.taskmanager.taskfolder" to "TaskPanel".
  [lepri]

- Rename content type from "s17.app.taskmanager.task" to "Task". [lepri]

- Rename package from s17.app.taskmanager to s17.taskmanager. [lepri]

- Added the script rebuild_i18n.sh. [lepri]

- Improved the internationalization in the vocabularies and javascripts.
  [lepri]

- Some adjusts in task view [lepri]


1.0a3 (2012-06-08)
------------------

- Improved history for changes in the task. [lepri]

- Improved view for task. [lepri]

- Added icon for task content. [lepri]


1.0a2 (2012-05-21)
------------------

- Fixed distribution. [hvelarde]


1.0a1 (2012-05-21)
------------------

- Initial release.
