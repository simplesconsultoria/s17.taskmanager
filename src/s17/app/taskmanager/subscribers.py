# -*- coding:utf-8 -*-
from five import grok

from datetime import date

from collective.watcherlist.interfaces import IWatcherList

from zope.lifecycleevent.interfaces import IObjectAddedEvent

from Products.CMFCore.interfaces import IActionSucceededEvent

from s17.app.taskmanager.content import ITask
from s17.app.taskmanager.adapters import IResponse


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
    if ITask.providedBy(task):
        send_response_notification_mail(task)


@grok.subscribe(ITask, IObjectAddedEvent)
def set_task_initial_date(task, event):
    ''' This subscriber will set the initial date
        for the task and send email for the
        author and for the responsible for the task
    '''
    watchers = IWatcherList(task)
    watchers.toggle_watching()
    if task.responsible:
        watchers.watchers.append(task.responsible)
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