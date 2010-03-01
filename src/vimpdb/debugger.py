import bdb
from pdb import Pdb
import sys
import StringIO
from vimpdb.proxy import ProxyToVim


def captured(method):

    def decorated(self, line):
        self.capture_stdout()
        stop = method(self, line)
        self.stop_capture()
        self.vim.showFeedback(self.pop_output())
        return stop

    return decorated


def moved(method):

    def decorated(self, line):
        stop = method(self, line)
        self.showFileAtLine()
        return stop

    return decorated


class VimPdb(Pdb):
    """
    debugger integrated with Vim
    """

    def __init__(self):
        bdb.Bdb.__init__(self)
        # attributes needed to remain compatible with Pdb methods
        self.aliases = {}
        self.vim = ProxyToVim()
        self.mainpyfile = ''
        self._wait_for_mainpyfile = 0

    def trace_dispatch(self, frame, event, arg):
        """allow to switch to Pdb instance"""
        if hasattr(self, 'pdb'):
            return self.pdb.trace_dispatch(frame, event, arg)
        else:
            return Pdb.trace_dispatch(self, frame, event, arg)

    def execRcLines(self):
        pass

    def cmdloop(self):
        stop = None
        self.preloop()
        while not stop:
            line = self.vim.waitFor(self)
            line = self.precmd(line)
            stop = self.onecmd(line)
            stop = self.postcmd(stop, line)
        self.postloop()

    def preloop(self):
        filename, lineno = self.getFileAndLine()
        self.vim.showFileAtLine(filename, lineno)

    def getFileAndLine(self):
        frame, lineno = self.stack[self.curindex]
        filename = self.canonic(frame.f_code.co_filename)
        return filename, lineno

    def showFileAtLine(self):
        filename, lineno = self.getFileAndLine()
        self.vim.showFileAtLine(filename, lineno)

    # stdout captures to send back to Vim
    def capture_stdout(self):
        self.stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
        self.captured = True

    def stop_capture(self):
        if self.captured:
            self.captured = False
            self.textOutput = sys.stdout.getvalue()
            sys.stdout = self.stdout

    def pop_output(self):
        result = self.textOutput
        self.textOutput = ''
        return result

    def do_pdb(self, line):
        """
        'pdb' command:
        switches back to debugging with (almost) standard pdb.Pdb
        except for added 'vim' command.
        """
        self.stop_capture()
        print self.pop_output()
        self.vim.closeSocket()
        self.pdb = get_hooked_pdb()
        self.pdb.set_trace_without_step(self.curframe)
        self.pdb.interaction(self.curframe, None)
        return 1

    def set_trace_without_step(self, frame):
        set_trace_without_step(self, frame)

    do_u = do_up = moved(Pdb.do_up)
    do_d = do_down = moved(Pdb.do_down)
    do_a = do_args = captured(Pdb.do_args)
    do_b = do_break = captured(Pdb.do_break)

    @captured
    def default(self, line):
        print line, "=",
        return Pdb.default(self, line)


def set_trace():
    """
    can be called like pdb.set_trace()
    """
    VimPdb().set_trace(sys._getframe().f_back)


# hook vimpdb  #
################


def trace_dispatch(self, frame, event, arg):
    """allow to switch to Vimpdb instance"""
    if hasattr(self, 'vimpdb'):
        return self.vimpdb.trace_dispatch(frame, event, arg)
    else:
        return self._orig_trace_dispatch(frame, event, arg)


def set_trace_without_step(self, frame):
    """
    set trace while switching from pdb to vimpdb
    and vice versa
    """
    self.reset()
    while frame:
        frame.f_trace = self.trace_dispatch
        self.botframe = frame
        frame = frame.f_back
    sys.settrace(self.trace_dispatch)


def do_vim(self, arg):
    """
    'vim' command:
    it switches to debugging with vimpdb
    """
    self.vimpdb = VimPdb()
    self.vimpdb.set_trace_without_step(self.curframe)
    self.vimpdb.interaction(self.curframe, None)
    return 1


def hook(klass):
    """
    monkey-patch pdb.Pdb class

    adds a 'vim' (and 'v') command:
    it switches to debugging with vimpdb
    """

    def setupMethod(klass, method):
        name = method.__name__
        orig = getattr(klass, name)
        orig_attr = '_orig_' + name
        if not hasattr(klass, orig_attr):
            setattr(klass, '_orig_' + name, orig)
            setattr(klass, name, method)

    setupMethod(klass, trace_dispatch)
    if not hasattr(klass, 'do_vim'):
        klass.set_trace_without_step = set_trace_without_step
        klass.do_vim = do_vim
        klass.do_v = do_vim


def get_hooked_pdb():
    hook(Pdb)
    debugger = Pdb()
    return debugger
