# uncompyle6 version 3.7.4
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.0 (v3.6.0:41df79263a11, Dec 23 2016, 08:06:12) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: multiprocessing\dummy\__init__.py
__all__ = [
 'Process', 'current_process', 'active_children', 'freeze_support',
 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Condition',
 'Event', 'Barrier', 'Queue', 'Manager', 'Pipe', 'Pool', 'JoinableQueue']
import threading, sys, weakref, array
from .connection import Pipe
from threading import Lock, RLock, Semaphore, BoundedSemaphore
from threading import Event, Condition, Barrier
from queue import Queue

class DummyProcess(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._pid = None
        self._children = weakref.WeakKeyDictionary()
        self._start_called = False
        self._parent = current_process()

    def start(self):
        assert self._parent is current_process()
        self._start_called = True
        if hasattr(self._parent, '_children'):
            self._parent._children[self] = None
        threading.Thread.start(self)

    @property
    def exitcode(self):
        if self._start_called:
            if not self.is_alive():
                return 0
        return


Process = DummyProcess
current_process = threading.current_thread
current_process()._children = weakref.WeakKeyDictionary()

def active_children():
    children = current_process()._children
    for p in list(children):
        if not p.is_alive():
            children.pop(p, None)

    return list(children)


def freeze_support():
    pass


class Namespace(object):

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __repr__(self):
        items = list(self.__dict__.items())
        temp = []
        for name, value in items:
            if not name.startswith('_'):
                temp.append('%s=%r' % (name, value))

        temp.sort()
        return '%s(%s)' % (self.__class__.__name__, ', '.join(temp))


dict = dict
list = list

def Array(typecode, sequence, lock=True):
    return array.array(typecode, sequence)


class Value(object):

    def __init__(self, typecode, value, lock=True):
        self._typecode = typecode
        self._value = value

    def _get(self):
        return self._value

    def _set(self, value):
        self._value = value

    value = property(_get, _set)

    def __repr__(self):
        return '<%s(%r, %r)>' % (type(self).__name__, self._typecode, self._value)


def Manager():
    return sys.modules[__name__]


def shutdown():
    pass


def Pool(processes=None, initializer=None, initargs=()):
    from ..pool import ThreadPool
    return ThreadPool(processes, initializer, initargs)


JoinableQueue = Queue