# -*- coding: utf-8 -*-
from five import grok
from plone.dexterity import content
from s17.taskmanager.interfaces import ITask
from s17.taskmanager.interfaces import ITaskPanel


class TaskPanel(content.Container):
    """A task panel."""
    grok.implements(ITaskPanel)


class Task(content.Container):
    """A task."""
    grok.implements(ITask)
