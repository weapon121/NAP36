# uncompyle6 version 3.7.4
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.0 (v3.6.0:41df79263a11, Dec 23 2016, 08:06:12) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: multiprocessing\process.py
__all__ = [
 'BaseProcess', 'current_process', 'active_children']
import os, sys, signal, itertools
from _weakrefset import WeakSet
try:
    ORIGINAL_DIR = os.path.abspath(os.getcwd())
except OSError:
    ORIGINAL_DIR = None

def current_process():
    """
    Return process object representing the current process
    """
    global _current_process
    return _current_process


def active_children():
    """
    Return list of process objects corresponding to live child processes
    """
    global _children
    _cleanup()
    return list(_children)


def _cleanup():
    for p in list(_children):
        if p._popen.poll() is not None:
            _children.discard(p)


class BaseProcess(object):
    __doc__ = '\n    Process objects represent activity that is run in a separate process\n\n    The class is analogous to `threading.Thread`\n    '

    def _Popen(self):
        raise NotImplementedError

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        global _process_counter
        assert group is None, 'group argument must be None for now'
        count = next(_process_counter)
        self._identity = _current_process._identity + (count,)
        self._config = _current_process._config.copy()
        self._parent_pid = os.getpid()
        self._popen = None
        self._target = target
        self._args = tuple(args)
        self._kwargs = dict(kwargs)
        self._name = name or type(self).__name__ + '-' + ':'.join(str(i) for i in self._identity)
        if daemon is not None:
            self.daemon = daemon
        _dangling.add(self)

    def run(self):
        """
        Method to be run in sub-process; can be overridden in sub-class
        """
        if self._target:
            (self._target)(*self._args, **self._kwargs)

    def start(self):
        """
        Start child process
        """
        if not self._popen is None:
            raise AssertionError('cannot start a process twice')
        else:
            assert self._parent_pid == os.getpid(), 'can only start a process object created by current process'
            assert not _current_process._config.get('daemon'), 'daemonic processes are not allowed to have children'
        _cleanup()
        self._popen = self._Popen(self)
        self._sentinel = self._popen.sentinel
        del self._target
        del self._args
        del self._kwargs
        _children.add(self)

    def terminate(self):
        """
        Terminate process; sends SIGTERM signal or uses TerminateProcess()
        """
        self._popen.terminate()

    def join(self, timeout=None):
        """
        Wait until child process terminates
        """
        if not self._parent_pid == os.getpid():
            raise AssertionError('can only join a child process')
        else:
            assert self._popen is not None, 'can only join a started process'
            res = self._popen.wait(timeout)
            if res is not None:
                _children.discard(self)

    def is_alive(self):
        """
        Return whether process is alive
        """
        if self is _current_process:
            return True
        else:
            if not self._parent_pid == os.getpid():
                raise AssertionError('can only test a child process')
            else:
                if self._popen is None:
                    return False
                returncode = self._popen.poll()
                if returncode is None:
                    return True
            _children.discard(self)
            return False

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        assert isinstance(name, str), 'name must be a string'
        self._name = name

    @property
    def daemon(self):
        """
        Return whether process is a daemon
        """
        return self._config.get('daemon', False)

    @daemon.setter
    def daemon(self, daemonic):
        """
        Set whether process is a daemon
        """
        assert self._popen is None, 'process has already started'
        self._config['daemon'] = daemonic

    @property
    def authkey(self):
        return self._config['authkey']

    @authkey.setter
    def authkey(self, authkey):
        """
        Set authorization key of process
        """
        self._config['authkey'] = AuthenticationString(authkey)

    @property
    def exitcode(self):
        """
        Return exit code of process or `None` if it has yet to stop
        """
        if self._popen is None:
            return self._popen
        else:
            return self._popen.poll()

    @property
    def ident(self):
        """
        Return identifier (PID) of process or `None` if it has yet to start
        """
        if self is _current_process:
            return os.getpid()
        else:
            return self._popen and self._popen.pid

    pid = ident

    @property
    def sentinel(self):
        """
        Return a file descriptor (Unix) or handle (Windows) suitable for
        waiting for process termination.
        """
        try:
            return self._sentinel
        except AttributeError:
            raise ValueError('process not started')

    def __repr__(self):
        if self is _current_process:
            status = 'started'
        else:
            if self._parent_pid != os.getpid():
                status = 'unknown'
            else:
                if self._popen is None:
                    status = 'initial'
                else:
                    if self._popen.poll() is not None:
                        status = self.exitcode
                    else:
                        status = 'started'
        if type(status) is int:
            if status == 0:
                status = 'stopped'
            else:
                status = 'stopped[%s]' % _exitcode_to_name.get(status, status)
        return '<%s(%s, %s%s)>' % (type(self).__name__, self._name,
         status, self.daemon and ' daemon' or '')

    def _bootstrap(self):
        global _children
        global _current_process
        global _process_counter
        from . import util, context
        try:
            try:
                if self._start_method is not None:
                    context._force_start_method(self._start_method)
                _process_counter = itertools.count(1)
                _children = set()
                util._close_stdin()
                old_process = _current_process
                _current_process = self
                try:
                    util._finalizer_registry.clear()
                    util._run_after_forkers()
                finally:
                    del old_process

                util.info('child process calling self.run()')
                try:
                    self.run()
                    exitcode = 0
                finally:
                    util._exit_function()

            except SystemExit as e:
                if not e.args:
                    exitcode = 1
                else:
                    if isinstance(e.args[0], int):
                        exitcode = e.args[0]
                    else:
                        sys.stderr.write(str(e.args[0]) + '\n')
                        exitcode = 1
            except:
                exitcode = 1
                import traceback
                sys.stderr.write('Process %s:\n' % self.name)
                traceback.print_exc()

        finally:
            util.info('process exiting with exitcode %d' % exitcode)
            sys.stdout.flush()
            sys.stderr.flush()

        return exitcode


class AuthenticationString(bytes):

    def __reduce__(self):
        from .context import get_spawning_popen
        if get_spawning_popen() is None:
            raise TypeError('Pickling an AuthenticationString object is disallowed for security reasons')
        return (
         AuthenticationString, (bytes(self),))


class _MainProcess(BaseProcess):

    def __init__(self):
        self._identity = ()
        self._name = 'MainProcess'
        self._parent_pid = None
        self._popen = None
        self._config = {'authkey':AuthenticationString(os.urandom(32)),  'semprefix':'/mp'}


_current_process = _MainProcess()
_process_counter = itertools.count(1)
_children = set()
del _MainProcess
_exitcode_to_name = {}
for name, signum in list(signal.__dict__.items()):
    if name[:3] == 'SIG' and '_' not in name:
        _exitcode_to_name[-signum] = name

_dangling = WeakSet()