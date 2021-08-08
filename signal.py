# uncompyle6 version 3.7.4
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.0 (v3.6.0:41df79263a11, Dec 23 2016, 08:06:12) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: signal.py
import _signal
from _signal import *
from functools import wraps as _wraps
from enum import IntEnum as _IntEnum
_globals = globals()
_IntEnum._convert('Signals', __name__, lambda name: name.isupper() and name.startswith('SIG') and not name.startswith('SIG_') or name.startswith('CTRL_'))
_IntEnum._convert('Handlers', __name__, lambda name: name in ('SIG_DFL', 'SIG_IGN'))
if 'pthread_sigmask' in _globals:
    _IntEnum._convert('Sigmasks', __name__, lambda name: name in ('SIG_BLOCK', 'SIG_UNBLOCK', 'SIG_SETMASK'))

def _int_to_enum(value, enum_klass):
    """Convert a numeric value to an IntEnum member.
    If it's not a known member, return the numeric value itself.
    """
    try:
        return enum_klass(value)
    except ValueError:
        return value


def _enum_to_int(value):
    """Convert an IntEnum member to a numeric value.
    If it's not an IntEnum member return the value itself.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return value


@_wraps(_signal.signal)
def signal(signalnum, handler):
    handler = _signal.signal(_enum_to_int(signalnum), _enum_to_int(handler))
    return _int_to_enum(handler, Handlers)


@_wraps(_signal.getsignal)
def getsignal(signalnum):
    handler = _signal.getsignal(signalnum)
    return _int_to_enum(handler, Handlers)


if 'pthread_sigmask' in _globals:

    @_wraps(_signal.pthread_sigmask)
    def pthread_sigmask(how, mask):
        sigs_set = _signal.pthread_sigmask(how, mask)
        return set(_int_to_enum(x, Signals) for x in sigs_set)


    pthread_sigmask.__doc__ = _signal.pthread_sigmask.__doc__
if 'sigpending' in _globals:

    @_wraps(_signal.sigpending)
    def sigpending():
        sigs = _signal.sigpending()
        return set(_int_to_enum(x, Signals) for x in sigs)


if 'sigwait' in _globals:

    @_wraps(_signal.sigwait)
    def sigwait(sigset):
        retsig = _signal.sigwait(sigset)
        return _int_to_enum(retsig, Signals)


    sigwait.__doc__ = _signal.sigwait
del _globals
del _wraps