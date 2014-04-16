# -*- coding: utf-8 -*-
from collective.watcherlist.interfaces import IWatcherList
from datetime import date
from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
from s17.taskmanager.adapters import IResponse
from s17.taskmanager.content import ITask
from s17.taskmanager.content import ITaskPanel
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


def send_response_notification_mail(task):
    watchers = IWatcherList(task)
    watchers.send('new-response-mail')


def send_task_notification_mail(task):
    watchers = IWatcherList(task)
    watchers.send('new-task-mail')


def send_closed_task_mail(task):
    watchers = IWatcherList(task)
    watchers.send('closed-task-mail')


@grok.subscribe(IResponse, IObjectAddedEvent)
def added_response(object, event):
    ''' A response has been added.
    '''
    task = event.newParent
    watchers = IWatcherList(task)
    if object.responsible:
        watchers.watchers.append(object.responsible)
        for user in task.users_with_local_role('Manager'):
            task.manage_delLocalRoles(userids=[user])
        task.manage_setLocalRoles(task.responsible, ['Manager'],)
    if ITask.providedBy(task):
        send_response_notification_mail(task)


@grok.subscribe(ITask, IObjectAddedEvent)
def set_task_initial_date(task, event):
    ''' This subscriber will set the initial date
        for the task and send email for the
        author and for the responsible for the task.
        And create a local role enable responsible to
        add tasks
    '''
    watchers = IWatcherList(task)
    watchers.toggle_watching()
    if task.responsible:
        watchers.watchers.append(task.responsible)
        task.manage_setLocalRoles(task.responsible, ['Manager'],)
    task.initial_date = date.today()
    send_task_notification_mail(task)


@grok.subscribe(ITask, IActionSucceededEvent)
def set_task_end_date(task, event):
    ''' This subscriber will set the end date
        for the task
    '''
    if event.action in ['close', ]:
        task.end_date = date.today()
        send_closed_task_mail(task)

    if event.action in ['reopen', ]:
        task.end_date = None


@grok.subscribe(ITaskPanel, IObjectAddedEvent)
def set_add_taskfolder_local_role(taskfolder, event):
    ''' This subscriber will create a local role enable responsible to
        add tasks
    '''
    if taskfolder.can_add_tasks:
        for user in taskfolder.can_add_tasks:
            taskfolder.manage_setLocalRoles(user, ['Owner'],)
    if taskfolder.responsible:
        taskfolder.manage_setLocalRoles(taskfolder.responsible, ['Manager'],)


@grok.subscribe(ITaskPanel, IObjectModifiedEvent)
def set_edit_taskfolder_local_role(taskfolder, event):
    ''' This subscriber will create a local role enable responsible to
        add tasks
    '''
    for user in taskfolder.users_with_local_role('Owner'):
        taskfolder.manage_delLocalRoles(userids=[user])
    if taskfolder.can_add_tasks:
        for user in taskfolder.can_add_tasks:
            taskfolder.manage_setLocalRoles(user, ['Owner'],)

    for user in taskfolder.users_with_local_role('Manager'):
        taskfolder.manage_delLocalRoles(userids=[user])
    if taskfolder.responsible:
        taskfolder.manage_setLocalRoles(taskfolder.responsible, ['Manager'],)
