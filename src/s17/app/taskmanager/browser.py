# -*- coding: utf-8 -*-

from five import grok

from plone.directives import dexterity

from Products.CMFPlone.utils import getToolByName

from s17.app.taskmanager.content import ITask, ITaskFolder

grok.templatedir("templates")

class TaskFolderView(dexterity.DisplayForm):
    grok.context(ITaskFolder)
    grok.name("view")
    grok.template('taskfolder_view')
    grok.require("zope2.View")

class TaskView(dexterity.DisplayForm):
    grok.context(ITask)
    grok.name("view")
    grok.template('task_view')
    grok.require("zope2.View")

    def images(self):
        ct = getToolByName(self.context,'portal_catalog')
        images = ct(portal_type='Image',path = '/'.join(self.context.getPhysicalPath()))
        if images:
            images = [ image.getObject() for image in images ]
            return images
        else:
            return None

    def files(self):
        ct = getToolByName(self.context,'portal_catalog')
        files = ct(portal_type='File',path = '/'.join(self.context.getPhysicalPath()))
        if files:
            return files
        else:
            return None

    def responsible(self):
        """ Return the fullname of the responsible for the task
        """
        mt = getToolByName(self.context, 'portal_membership')
        username = self.context.responsible
        if username:
            fullname = mt.getMemberById(username).getProperty('fullname')
            if fullname:
                return fullname
            else:
                return username
        else:
            return None



