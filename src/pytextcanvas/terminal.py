import os
import sys

def getTerminalSize():
    """
    Returns the size of the terminal as a tuple of two ints (width, height).

    Raises `PyTextCanvasException` when called by a program that is not run from a terminal window.

    NOTE - Currently this feature only works on Windows.
    """
    import ctypes # getTerminalSize() will most likely rarely be used, so don't bother importing ctypes all the time. TODO - Is this line of thinking valid? Does it really make a difference?
    if sys.platform == 'win32':
        # From http://code.activestate.com/recipes/440694-determine-size-of-console-window-on-windows/
        h = ctypes.windll.kernel32.GetStdHandle(-12)
        csbi = ctypes.create_string_buffer(22)
        res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

        if res:
            import struct
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            return right - left + 1, bottom - top + 1
        else:
            raise PyTextCanvasException('Unable to determine terminal size. This happens when in a non-terminal environment, such as IDLE.') #sizex, sizey = 80, 25 # can't determine actual size - return default values

    # TODO - finish for non windows platforms.
    # Linux:
    # sizex, sizey = os.popen('stty size', 'r').read().split()
    # return int(sizex), int(sizey)

    #else:
    #    raise PyTextCanvasException('Cannot determine the platform')


def setTerminalSize():
    pass # TODO

def clearScreen():
    """
    Clears the terminal by calling `cls` or `clear`, depending on what platform
    this Python script is running from.
    """
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')

