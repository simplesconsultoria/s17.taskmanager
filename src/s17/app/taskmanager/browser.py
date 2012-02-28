# -*- coding: utf-8 -*-

from five import grok

from plone.directives import dexterity

from zope.component import getMultiAdapter

from Products.CMFPlone.utils import getToolByName

from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IATImage

from s17.app.taskmanager.content import ITask, ITaskFolder



grok.templatedir("templates")

class TaskFolderView(dexterity.DisplayForm):
    grok.context(ITaskFolder)
    grok.name("view")
    grok.template('taskfolder_view')
    grok.require("zope2.View")

    def responsible(self, obj):
        """ Return the fullname of the responsible for the task
        """
        mt = getToolByName(self.context, 'portal_membership')
        username = obj.responsible
        if username:
            fullname = mt.getMemberById(username).getProperty('fullname')
            if fullname:
                return fullname
            else:
                return username
        else:
            return None

    def tasks(self):
        ''' function to return all tasks in the container
        '''
        ct = getToolByName(self.context,'portal_catalog')
        tasks = ct(object_provides=ITask.__identifier__, path='/'.join(self.context.getPhysicalPath()))
        if tasks:
            return [dict(title=task.Title,
                         url=task.getURL(),
                         status=task.review_state.capitalize(),
                         responsible=self.responsible(task.getObject()),
                         priority=task.getObject().priority,)
                            for task in tasks]
        else:
            return None

class TaskView(dexterity.DisplayForm):
    grok.context(ITask)
    grok.name("view")
    grok.template('task_view')
    grok.require("zope2.View")

    def images(self):
        ct = getToolByName(self.context,'portal_catalog')
        images = ct(object_provides=IATImage.__identifier__,path = '/'.join(self.context.getPhysicalPath()))
        if images:
            images = [ image.getObject() for image in images ]
            return images
        else:
            return None

    def files(self):
        ct = getToolByName(self.context,'portal_catalog')
        files = ct(object_provides=IATFile.__identifier__,path = '/'.join(self.context.getPhysicalPath()))
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



