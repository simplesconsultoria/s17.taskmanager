# -*- coding:utf-8 -*-
from five import grok

from Acquisition import aq_parent

from Products.CMFCore.interfaces import IActionSucceededEvent

from collective.polls.content.poll import IPoll
from s17.app.taskmanager.content import ITask

ALL_ROLES = ['Anonymous', 'Contributor', 'Editor', 'Manager', 'Member',
             'Reader', 'Reviewer', 'Site Administrator']

#
#@grok.subscribe(ITask, IActionSucceededEvent)
#def send_email(task, event):
#    ''' This subscriber will send emails to the
#        responsible for the task
#    '''
#    import pdb;pdb.set_trace()
#    if event.action in ['open', ]:
#        parent = aq_parent(task)
#        parent_view_roles = parent.rolesOfPermission('View')
#        parent_view_roles = [r['name'] for r in parent_view_roles
#                             if r['selected']]
#        # Poll has been opened
#        allow_anonymous = task.allow_anonymous
#        if ('Anonymous' in parent_view_roles) and allow_anonymous:
#            task.manage_permission(PERMISSION_VOTE,
#                ALL_ROLES,
#                acquire=0)