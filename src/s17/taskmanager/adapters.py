# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from DateTime import DateTime
from persistent import Persistent
from persistent.list import PersistentList
from s17.taskmanager.content import ITask
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.container.contained import ObjectAddedEvent
from zope.container.contained import ObjectRemovedEvent
from zope.event import notify
from zope.interface import Attribute
from zope.interface import implements
from zope.interface import Interface


class IResponseContainer(Interface):
    pass


class IResponse(Interface):

    text = Attribute('Text of this response')
    rendered_text = Attribute('Rendered text (html) for caching')
    changes = Attribute('Changes made to the task in this response.')
    creator = Attribute('Id of user making this change.')
    date = Attribute('Date (plus time) this response was made.')
    responsible = Attribute('Responsible for the task.')

    def add_change(id, name, before, after):
        """Add change to the list of changes.
        """


class ResponseContainer(Persistent):

    implements(IResponseContainer)
    adapts(ITask)
    ANNO_KEY = 'task.responses'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)
        self.__mapping = annotations.get(self.ANNO_KEY, None)
        if self.__mapping is None:
            self.__mapping = PersistentList()
            annotations[self.ANNO_KEY] = self.__mapping

    def __contains__(self, key):
        """See interface IReadContainer

        Reimplement this method, since has_key() returns the key if available,
        while we expect True or False.

        >>> c = ResponseContainer()
        >>> 'a' in c
        False
        >>> c['a'] = 1
        >>> 'a' in c
        True
        >>> 'A' in c
        False
        """
        return key in self.__mapping

    has_key = __contains__

    def __getitem__(self, i):
        i = int(i)
        return self.__mapping.__getitem__(i)

    def __delitem__(self, item):
        self.__mapping.__delitem__(item)

    def __len__(self):
        return self.__mapping.__len__()

    def __setitem__(self, i, y):
        self.__mapping.__setitem__(i, y)

    def append(self, item):
        self.__mapping.append(item)

    def remove(self, id):
        """Remove item 'id' from the list.

        We don't actually remove the item, we just set it to None,
        so that when you edit item 3 out of 3 and someone deletes
        item 2 you are not left in the water.

        Note that we used to get passed a complete item, not an id.
        """
        id = int(id)
        self[id] = None

    def add(self, item):
        self.append(item)
        id = str(len(self))
        event = ObjectAddedEvent(item, newParent=self.context, newName=id)
        notify(event)

    def delete(self, id):
        # We need to fire an ObjectRemovedEvent ourselves here because
        # self[id].__parent__ is not exactly the same as self, which
        # in the end means that __delitem__ does not fire an
        # ObjectRemovedEvent for us.
        #
        # Also, now we can say the oldParent is the issue instead of
        # this adapter.
        event = ObjectRemovedEvent(self[id], oldParent=self.context, oldName=id)
        self.remove(id)
        notify(event)


class Response(Persistent):

    implements(IResponse)

    def __init__(self, text, responsible=None):
        self.__parent__ = self.__name__ = None
        self.text = text
        self.changes = PersistentList()
        sm = getSecurityManager()
        user = sm.getUser()
        self.creator = user.getId() or '(anonymous)'
        self.date = DateTime()
        self.responsible = responsible

    def add_change(self, id, name, before, after):
        """Add a new issue change.
        """
        delta = dict(
            id=id,
            name=name,
            before=before,
            after=after)
        self.changes.append(delta)
