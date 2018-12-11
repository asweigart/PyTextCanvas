"""
PyTextCanvas is a module for writing text and ascii art to a 2D canvas in Python.


"""

"""
TODO

!!!!! Set it up so that Cells can hold arbitrary objects. - Wait, how is this different from just a generic matrix data structure

Change properties to descriptors
Add PyTextCanvasException class (maybe?)
Add tkinter window
Docstrings

NOTE: PyTextCanvas is not thread safe.

"""

"""
TODO

Design considerations:
- Canvas must track steps for undo/redo
- Canvas must track the written areas for clipping. This won't include use of fill.

TODO docs:
- Each position is called a cell.
- Setting a cell to ' ' makes it "blank" and opaque, setting it to None makes it transparent.

Road Map of Features:
- colors
- arbitrary data associated with the cells
- export as html
"""

# TODO - add a mode where drawing ooutside the canvas is a no-op instead of raising an exception.

__version__ = '0.0.3'

import doctest
import math

import colorama
from colorama import Fore, Back
import pybresenham

import pytextcanvas.terminal

# Constants
DEFAULT_CANVAS_WIDTH = 80
DEFAULT_CANVAS_HEIGHT = 25

DEFAULT_FG = '#000000'
DEFAULT_BG = '#ffffff'

CLEAR, BLACK, WHITE, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW = range(9)
COLORAMA_FG_MAP = {CLEAR: Fore.RESET, BLACK: Fore.BLACK, WHITE: Fore.WHITE, RED: Fore.RED, GREEN: Fore.GREEN, BLUE: Fore.BLUE, CYAN: Fore.CYAN, MAGENTA: Fore.MAGENTA, YELLOW: Fore.YELLOW}
COLORAMA_BG_MAP = {CLEAR: Back.RESET, BLACK: Back.BLACK, WHITE: Back.WHITE, RED: Back.RED, GREEN: Back.GREEN, BLUE: Back.BLUE, CYAN: Back.CYAN, MAGENTA: Back.MAGENTA, YELLOW: Back.YELLOW}

# Terminal functions:
getTerminalSize = pytextcanvas.terminal.getTerminalSize
clearScreen = pytextcanvas.terminal.clearScreen


# Initialize colorama module:
colorama.init()


def _checkForIntOrFloat(arg):
    if not isinstance(arg, (int, float)):
        raise PyTextCanvasException('argument must be int or float, not %s' % (arg.__class__.__name__))


def isInside(point_x, point_y, area_left, area_top, area_width, area_height):
    """
    Returns `True` if the point of `point_x`, `point_y` is inside the area
    described, inclusive of `area_left` and `area_top`.

    >>> isInside(0, 0, 0, 0, 10, 10)
    True
    >>> isInside(10, 0, 0, 0, 10, 10)
    False
    """
    return (area_left <= point_x < area_left + area_width) and (area_top <= point_y < area_top + area_height)


class PyTextCanvasException(Exception):
    """
    Generic exception for the `pytextcanvase` module. PyTextCanvas should never
    produce an exception that isn't `PyTextCanvasException`. If it does, it should
    be considered a bug."""
    pass


class Canvas:
    def __init__(self, width=None, height=None, loads=None, fg=None, bg=None):
        """
        Initialize a new Canvas, which represents a rectangular area of
        text characters. The coordinates start in the upper left corner at
        0, 0 and coordinates increase going right and down. Each position
        in the canvas is called a cell and can contain a single text
        character.

        The size of the canvas is immutable. The size is specified in the
        intializer through the `width` and `height` parameters or with a multi-line `loads`
        string, which sets the size based on the maximum width and number
        of lines in the `loads` string.

        The default size is 80 x 25 characters.

        Currently, color is not supported and the `fg` and `bg` arguments do nothing.
        """
        if width is None and height is None and loads is not None:
            # self.width and self.height are set based on the size of the loads string
            loadsLines = loads.splitlines() # TODO - how to handle \r\n cases?
            self._width = max([len(line) for line in loadsLines])
            self._height = len(loadsLines)
        else:
            # self.width and self.height are set based on the width and height parameters
            if width is None:
                self._width = DEFAULT_CANVAS_WIDTH
            else:
                if not isinstance(width, int):
                    raise PyTextCanvasException('`width` arg must be an int, not %r' % (width.__class__.__name__))
                if width < 1:
                    raise PyTextCanvasException('`width` arg must be 1 or greater, not %r' % (width))
                self._width = width

            if height is None:
                self._height = DEFAULT_CANVAS_HEIGHT
            else:
                if not isinstance(height, int):
                    raise PyTextCanvasException('`height` arg must be an int, not %r' % (height.__class__.__name__))
                if height < 1:
                    raise PyTextCanvasException('`height` arg must be 1 or greater, not %r' % (height))
                self._height = height

        # The data structure for the characters in this canvas. The None value
        # represents a "transparent" character when canvases are layered on
        # top of each other, as opposed to a space ' ' which will cover up
        # that cell with a blank space.

        # =====================================
        # ============= IMPORTANT =============
        # =====================================
        # If you directly modify _chars, be sure to set _strDirty to True, otherwise
        # the cached version of the string will be returned and any changes won't
        # be reflected.
        self._chars = [[None] * self._height for i in range(self._width)]


        # NOTE: A None value for color is like a None value for character, while CLEAR would be similar to a space character.
        if fg is not None and fg not in range(9):
            raise PyTextCanvasException('fg arg must be None or one of the CLEAR, BLACK, WHITE, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW constants.')
        if bg is not None and bg not in range(9):
            raise PyTextCanvasException('bg arg must be None or one of the CLEAR, BLACK, WHITE, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW constants.')
        self._fg = fg
        self._bg = bg

        # The foreground & background of each cell in the canvas. These are
        # stored as one of the six color constants, which are ints 0-7. The None
        # value represents the RESET'd color in colorama.
        # Currently we're sticking to the 8 colors in the colorama module. More might be added later.
        self._fginfo = [[None] * self._height for i in range(self._width)]
        self._bginfo = [[None] * self._height for i in range(self._width)]
        # TODO - the rest of the color implementation needs to be done.

        self._cursor = (0, 0) # The cursor is always set to integers.

        if loads is not None:
            # Pre-populate with a string.
            self.loads(loads)

        self._strCache = None # Cached returned value from __str__()
        self._strDirty = True # If False, __str__() uses the cached value.


    @property
    def fg(self):
        """The current foreground color. TODO"""
        return self._fg

    @fg.setter
    def fg(self, value):
        if value is not None and value not in range(9):
            raise PyTextCanvasException('fg attribute must be None or one of the CLEAR, BLACK, WHITE, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW constants.')
        self._fg = value

    @property
    def bg(self):
        """The current background color. TODO"""
        return self._bg

    @bg.setter
    def bg(self, value):
        if value is not None and value not in range(9):
            raise PyTextCanvasException('bg attribute must be None or one of the CLEAR, BLACK, WHITE, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW constants.')
        self._bg = value



    @property
    def width(self):
        """The integer width of the canvas.

        This is a read-only attribute.

        >>> canvas = Canvas(10, 5)
        >>> canvas.width
        10
        """
        return self._width


    @property
    def height(self):
        """The integer height of the canvas.

        This is a read-only attribute.

        >>> canvas = Canvas(10, 5)
        >>> canvas.height
        5
        """
        return self._height


    @property
    def size(self):
        """The integer width and height of the canvas.

        This is a read-only attribute.

        >>> canvas = Canvas(10, 5)
        >>> canvas.size
        (10, 5)
        """
        return (self._width, self._height)


    @property
    def area(self):
        """The integer number of characters that can fit in the area of the canvas. This is the width multiplied by the height.

        This attribute is read-only.

        >>> canvas = Canvas(10, 5)
        >>> canvas.area
        50
        """
        return self._width * self._height


    @property
    def cursor(self):
        """
        The cursor location as an (x, y) tuple. The cursor is where
        text is written from in the `write()` method.
        """
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self.goto(value)



    @property
    def cursorx(self):
        return self._cursor[0]

    @cursorx.setter
    def cursorx(self, value):
        self.goto(value, self._cursor[1])



    @property
    def cursory(self):
        return self._cursor[1]

    @cursory.setter
    def cursory(self, value):
        self.goto(self._cursor[0], value)


    def isOnCanvas(self, x, y):
        """
        Returns True if `x` is between `0` and the canvas's `width - 1`, and
        if `y` is between `0` and the canvas's `height - 1`, inclusive.

        >>> canvas = Canvas(10, 10)
        >>> canvas.isOnCanvas(0, 0)
        True
        >>> canvas.isOnCanvas(10, 10)
        False
        >>> canvas.isOnCanvas(-1, 0)
        False
        """
        return 0 <= x < self.width and 0 <= y < self.height


    def __repr__(self):
        """Return a limited representation of this Canvas object. The width,
        and height information is included.

        >>> canvas = Canvas()
        >>> print(repr(canvas))
        <'Canvas' object, width=80, height=25>
        """
        return '<%r object, width=%r, height=%r>' % \
            (self.__class__.__name__, self._width, self._height)


    def __str__(self):
        """Return a multiline string representation of this Canvas object.
        The bottom row does not end with a newline character.

        >>> canvas = Canvas(10, 4)
        >>> canvas.fill('x')
        >>> print(canvas)
        xxxxxxxxxx
        xxxxxxxxxx
        xxxxxxxxxx
        xxxxxxxxxx
        """

        if not self._strDirty:
            return self._strCache

        # TODO - make this thread safe
        result = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                c = self._chars[x][y]
                if c is None:
                    row.append(' ')
                else:
                    row.append(c)
            result.append(''.join(row))

        self._strDirty = False
        self._strCache = '\n'.join(result)
        return self._strCache


    def __len__(self):
        """Returns the length of this Canvas object, which is the length of
        its string as returned by str(), not the width * height.

        The string representation includes newline characters at the end of
        each row, except for the last row."""
        return (self.width * self.height) + (self.height - 1)


    def __iadd__(self):
        pass # TODO


    def __getitem__(self, key):
        """Return the character in this Canvas object, specified by `key`.
        The `key` can be a tuple of integers (x, y) or a single integer
        (treating the Canvas as a single-lined string). This integer can
        also be negative to return a character from the end of the string.

        The `key` can also be a slice object of two tuples which represents
        the top left and bottom right corners of the area to return as a new
        Canvas object. The slice cannot be made up of two integers.

        Leaving the first item in the slice defaults to the top left corner
        of the canvas, while leaving the second item in the slice efaults
        to the bottom right corner of the object. Using [:] is the syntax
        to get a copy of the canvas.

        This method only raises KeyError, never IndexError."""
        self._checkForSlicesInKey(key)

        if isinstance(key, tuple):
            x, y = self._checkKey(key)
            return self._chars[x][y]

        elif isinstance(key, slice):
            x1, y1, x2, y2, xStep, yStep = self._normalizeKeySlice(key)

            # create the new Canvas object
            subWidth = math.ceil((x2 - x1) / float(xStep))
            subHeight = math.ceil((y2 - y1) / float(yStep))

            subcanvas = Canvas(width=subWidth, height=subHeight)

            # copy the characters to the new Canvas object
            for ix, xoffset in enumerate(range(0, subWidth, xStep)):
                for iy, yoffset in enumerate(range(0, subHeight, yStep)):
                    subcanvas[ix, iy] = self[x1 + xoffset, y1 + yoffset]
            return subcanvas

        else:
            raise PyTextCanvasException('key must be a tuple of two ints')

    def __setitem__(self, key, value):
        self._checkForSlicesInKey(key)

        if isinstance(key, tuple):
            if value is not None:
                value = str(value)
                if len(value) == 0:
                    raise PyTextCanvasException('value must have a length of 1, set to None or use del to delete a cell, or set to " " to make the cell blank')
                elif len(value) != 1:
                    raise PyTextCanvasException('value must have a length of 1')

            x, y = self._checkKey(key)

            self._strDirty = True
            self._strCache = None
            self._chars[x][y] = value

        elif isinstance(key, slice):
            if value is None: # delete the cells
                del self[key]
                return

            x1, y1, x2, y2, xStep, yStep = self._normalizeKeySlice(key)

            self._strDirty = True
            self._strCache = None

            # copy the value to every place in the slice
            for ix in range(x1, x2, xStep):
                for iy in range(y1, y2, yStep):
                    self._chars[ix][iy] = value
            return

        else:
            raise PyTextCanvasException('key must be a tuple of two ints')


    def __delitem__(self, key):
        self._checkForSlicesInKey(key)

        if isinstance(key, tuple):
            x, y = self._checkKey(key)

            self._strDirty = True
            self._strCache = None
            self._chars[x][y] = None
            return

        elif isinstance(key, slice):
            self._strDirty = True
            self._strCache = None
            x1, y1, x2, y2, xStep, yStep = self._normalizeKeySlice(key)
            for ix in range(x1, x2, xStep):
                for iy in range(y1, y2, yStep):
                    self._chars[ix][iy] = None
        else:
            raise PyTextCanvasException('key must be a tuple of two ints')


    def _checkForSlicesInKey(self, key):
        """Check that the user didn't incorrectly specify the slice by forgetting
        the parentheses."""
        if isinstance(key, tuple):
            for i, v in enumerate(key):
                if isinstance(v, slice):
                    raise PyTextCanvasException('Use parentheses when specifying slices, i.e. spam[(0, 0):(9, 9)] not spam[0, 0:9, 9].')

    def _checkKey(self, key):
        """Returns an (x, y) tuple key for all integer/tuple key formats.

        >>> canvas = Canvas()
        >>> canvas._checkKey((0, 0))
        (0, 0)
        >>> canvas._checkKey((-1, 0))
        (79, 0)
        >>> canvas._checkKey((0, -1))
        (0, 24)
        >>> canvas._checkKey((-2, -2))
        (78, 23)
        """
        x, y = self._convertNegativeTupleKeyToPositiveTupleKey(key)
        return x, y

    def _convertNegativeTupleKeyToPositiveTupleKey(self, tupleKey):
        """Returns a tuple key with positive integers instead of negative
        integers.

        >>> canvas = Canvas()
        >>> canvas._convertNegativeTupleKeyToPositiveTupleKey((-1, -1))
        (79, 24)
        >>> canvas._convertNegativeTupleKeyToPositiveTupleKey((-1, 0))
        (79, 0)
        >>> canvas._convertNegativeTupleKeyToPositiveTupleKey((0, -1))
        (0, 24)
        >>> canvas._convertNegativeTupleKeyToPositiveTupleKey((0, 0))
        (0, 0)
        """
        # check that tuple key is well formed: two ints as (x, y)

        if len(tupleKey) != 2 or not isinstance(tupleKey[0], int) or not isinstance(tupleKey[1], int):
            raise PyTextCanvasException('key must be a tuple of two ints')

        x, y = tupleKey # syntactic sugar

        # check x and y are in range
        if not (-self.width <= x < self.width):
            raise PyTextCanvasException('key\'s x (`%r`) is out of range' % (x))
        if not (-self.height <= y < self.height):
            raise PyTextCanvasException('key\'s y (`%r`) is out of range' % (y))

        # convert negative x & y to corresponding x & y
        if x < 0:
            x = self.width + x
        if y < 0:
            y = self.height + y

        return x, y


    def _normalizeKeySlice(self, key):
        """Takes a slice object and returns a tuple of three tuples, each with
        two integers, for the start, stop, and step aspects of the slice.

        The start is guaranteed to be the top-left corner and the stop the
        bottom-right corner of a rectangular area within the canvas. Negative
        integers in the start and stop tuples are normalized to positive
        integers.

        >>> canvas = Canvas()

        """
        if key.start is None:
            kstart = (0, 0)
        else:
            kstart = key.start

        if key.stop is None:
            kstop = (self.width, self.height)
        else:
            kstop = key.stop

        if key.step is None:
            kstep = (1, 1)
        elif isinstance(key.step, int):
            # if only one int is specified, use it for both steps
            kstep = (key.step, key.step)
        else:
            kstep = key.step

        # x1 & y1 should be top-left, x2 & y2 should be bottom-right
        # So swap these values if need be.
        x1, y1 = kstart
        x2, y2 = kstop
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        try:
            x1, y1 = self._convertNegativeTupleKeyToPositiveTupleKey((x1, y1))

            # Because x2 and y2 can go 1 past the end of the max index, the
            # _convertNegativeTupleKeyToPositiveTupleKey() may raise an exception.
            # So we need to pass dummy values so the exception isn't raised.
            if x2 != self.width and x2 != -(self.width - 1) and \
               y2 != self.height and y2 != -(self.height - 1):
                x2, y2 = self._convertNegativeTupleKeyToPositiveTupleKey((x2, y2))
            elif x2 != self.width and x2 != -(self.width - 1):
                x2, _dummy = self._convertNegativeTupleKeyToPositiveTupleKey((x2, 0))
            elif y2 != self.height and y2 != -(self.height - 1):
                _dummy, y2 = self._convertNegativeTupleKeyToPositiveTupleKey((0, y2))
            else:
                pass # In this case, we don't need to adust x2 and y2 at all. So do nothing.
        except KeyError:
            raise PyTextCanvasException('key must be a tuple of two ints')

        return (x1, y1, x2, y2, kstep[0], kstep[1])

    def _convertSingleIndexToTupleIndexes(self, index):
        return (index % self._width, index // self._width)


    def _convertTupleIndexsToSingleIndex(self, xindex, yindex):
        return (yindex * self._width) + xindex


    def __contains__(self, item):
        """Returns True if item exists as a substring in a row in the string
        representation of this canvas. This string representation will
        include \n newline characters at the end of each row (but not on the
        last row)."""
        if not isinstance(item, str):
            raise PyTextCanvasException('string required for left operand')
        return item in str(self)


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if other._width != self._width or other._height != self._height:
            return False

        for x in range(self._width):
            for y in range(self._height):
                if self._chars[x][y] != other._chars[x][y]:
                    return False
        return True


    def print(self):
        """Prints the canvas to the screen. The difference between calling
        this method and passing the Canvas object to the print() function
        is that this method will displays colors using Colorama."""
        currentFgColor = CLEAR
        currentBgColor = CLEAR
        print(Fore.RESET + Back.RESET, end='')

        for y in range(self._height):
            for x in range(self._width):
                # Set colorama fg color if the fg color has changed.
                fg = self._fginfo[x][y]
                if fg is None:
                    fg = CLEAR
                if fg != currentFgColor:
                    print(COLORAMA_FG_MAP[fg], end='')
                    currentFgColor = fg

                # Set colorama bg color if the bg color has changed.
                bg = self._bginfo[x][y]
                if bg is None:
                    bg = CLEAR
                if bg != currentBgColor:
                    print(COLORAMA_BG_MAP[bg], end='')
                    currentBgColor = bg

                # Display the character.
                c = self._chars[x][y]
                if c is None:
                    c = ' '
                print(c, end='') # TODO - see if there's ways to optimize this.
            print()
        print(Fore.RESET + Back.RESET, end='')



    def write(self, text, x=None, y=None):
        """
        Writes text to the canvas, starting at the cursor location (or the `x`
        and `y` arguments, if provided).

        The cursor will automatically wrap around the right edge and go
        back to the topleft afterwards.

        >>> canvas = Canvas(20, 4)
        >>> canvas.cursor
        (0, 0)
        >>> canvas.write('Hello world!' * 10)
        >>> print(canvas)
        rld!Hello world!Hell
        o world!Hello world!
        o world!Hello world!
        Hello world!Hello wo
        >>> canvas.cursor
        (0, 2)
        >>> canvas.write('ABC')
        >>> print(canvas)
        rld!Hello world!Hell
        o world!Hello world!
        ABCorld!Hello world!
        Hello world!Hello wo
        """

        # TODO - change this so that the cursor moves.
        if x is None:
            x = self.cursorx
        if y is None:
            y = self.cursory

        self._strDirty = True
        startIndex = self._convertTupleIndexsToSingleIndex(x, y)
        for i in range(startIndex, startIndex + len(text)):
            cx, cy = self._convertSingleIndexToTupleIndexes(i % self.area)
            if not self.isOnCanvas(cx, cy):
                break

            self._chars[cx][cy] = text[i - startIndex]
            self._fginfo[cx][cy] = self._fg
            self._bginfo[cx][cy] = self._bg

        self.cursor = self._convertSingleIndexToTupleIndexes((startIndex + len(text)) % self.area)


    def shift(self, xOffset, yOffset):
        """Shifts the characters on the canvas horizontally and vertically.
        Characters will not wrap around the edges of the canvas, but are
        lost instead. These cells are set to `None`.

        >>> canvas = Canvas(5, 5)
        >>> canvas.fill('x')
        >>> canvas.shift(2, 3)
        >>> print(canvas)
        <BLANKLINE>
        <BLANKLINE>
        <BLANKLINE>
          xxx
          xxx
        """
        if xOffset >= self.width or xOffset <= -self.width or \
           yOffset >= self.height or yOffset <= -self.height:
           # If either offset is greater than the width/height, just clear the
           # entire canvas.
           self.clear()
           return

        # Get the appropriate range objects.
        if xOffset > 0:
            xRangeObj = range(self.width - 1 - xOffset, -1, -1)
        else:
            xRangeObj = range(self.width - xOffset)

        if yOffset > 0:
            yRangeObj = range(self.height - 1 - yOffset, -1, -1)
        else:
            yRangeObj = range(self.height - yOffset)

        for x in xRangeObj:
            for y in yRangeObj:
                self[x + xOffset, y + yOffset] = self[x, y]

        # Clear the old, original cells.
        # TODO - this can be made more efficient by not clearing the overlapping regions twice.
        if xOffset >= 0:
            for x in range(xOffset):
                for y in range(self.height):
                    del self[x, y]
        else:
            for x in range(self.width - 1 - xOffset, self.width):
                for y in range(self.height):
                    del self[x, y]

        if yOffset >= 0:
            for x in range(self.width):
                for y in range(yOffset):
                    del self[x, y]
        else:
            for x in range(self.width):
                for y in range(self.height - 1 - yOffset):
                    del self[x, y]


    def clear(self):
        """Clears the entire canvas by setting every cell to `None`. These
        cells are transparent, not blank. To make the cells blank, call `fill(' ')`."""
        self.fill(None)


    def copy(self, left=0, top=0, width=None, height=None):
        """
        Returns a new Canvas object created from a subregion of this Canvas object.

        This returned Canvas can be "pasted" to other Canvas objects using `paste()`.
        """
        if width is None:
            width = self.width # By default, use the entire width of the canvas.
        if height is None:
            height = self.height # By default, use the entire height of the canvas.

        # Create the new Canvas object for the copied data.
        canvasCopy = Canvas(width=width, height=height)

        # Copy the character, fg color, and bg color data.
        for x in range(width):
            for y in range(height):
                canvasCopy._chars[x][y] = self._chars[x + left][y + top]
                canvasCopy._fginfo[x][y] = self._fginfo[x + left][y + top]
                canvasCopy._bginfo[x][y] = self._bginfo[x + left][y + top]

        # Copy the various properties.
        canvasCopy._cursor = self._cursor

        return canvasCopy


    def __copy__(self):
        return self.copy(0, 0, self.width, self.height)


    def paste(self, canvasToPaste, left, top):
        """
        Paste the character, foreground color, and background color data from
        `canvasToPaste` to this `Canvas` object.
        """
        # Paste the characters on this Canvas.
        for x in range(canvasToPaste.width):
            for y in range(canvasToPaste.height):
                if self.isOnCanvas(x + left, y + top):
                    self._chars[x + left][y + top] = canvasToPaste._chars[x][y]
                    self._fginfo[x + left][y + top] = canvasToPaste._fginfo[x][y]
                    self._bginfo[x + left][y + top] = canvasToPaste._bginfo[x][y]
        self._strDirty = True


    def loads(self, content):
        r"""
        Load the multi-line string in `content` as the text on this canvas.

        This method is used by the `loads` argument in `Canvas`'s constructor function.

        >>> canvas = Canvas(5, 2)
        >>> canvas.loads('Hello\nworld')
        >>> print(canvas)
        Hello
        world
        >>> canvas2 = Canvas(6, 2)
        >>> canvas2.loads('Hellooooo\nworld!!!\nHow are you?')
        >>> print(canvas2)
        Helloo
        world!
        """
        # TODO - how to handle \r?

        y = 0
        for line in str(content).splitlines():
            for x, v in enumerate(line):
                if x >= self.width:
                    # Excess text that goes beyond the right edge will be truncated.
                    break
                self[x, y] = v
            y += 1
            if y >= self.height:
                # Excess text that goes beyond the bottom edge will be truncated.
                break

    def goto(self, x, y=None):
        """Sets the cursor to a specific xy point on the Canvas. `x` and `y`
        are the x and y coordinates (which can be ints or floats), or `x`
        is a tuple of two int/float values.

        `PyTextCanvas.goto()` affects the PyTextCanvas object's cursor,
        which is always set to int values. `Turtle.goto()` affects the
        position of the Turtle object's cursor, which can be set to a float."""

        # Note: This function manipulates _cursor directly.
        # These properties rely on goto() to for their functionality.
        if y is None or (not isinstance(x, int) and not isinstance(y, int)):
            try:
                x, y = tuple(x)
            except:
                raise PyTextCanvasException('arguments must be two ints or an iterable of two ints, not %r' % (x.__class__.__name__))

        if not isinstance(x, int):
            raise PyTextCanvasException('x argument must be an int, not %r' % (x.__class__.__name__))
        if not isinstance(y, int):
            raise PyTextCanvasException('y argument must be an int, not %r' % (y.__class__.__name__))

        if not isInside(x, y, -self._width, -self._height, self._width * 2, self._height * 2):
            raise PyTextCanvasException('x or y argument is not in range, x=%s y=%s and canvas width=%s height=%s' % (x, y, self._width, self._height))

        # Handle any negative coordinates.
        if x < 0:
            x = self._width + x
        if y < 0:
            y = self._height + y

        self._cursor = (x, y)


    '''
    # TODO - implement, probably using pybresenham
    def rotate(self):
        # TODO - need to decide if this should return a new, larger canvas to handle non-modulo-90 rotations
        pass

    def scale(self):
        # TODO - need to decide if this should return a new canvas. (I think it should, why would you want the text scaled but not the canvas size?)
        pass
    '''


    def vflip(self):
        """
        Vertically flips the characters on this canvas.

        >>> canvas = Canvas(4, 4)
        >>> canvas.fill(',')
        >>> canvas[0, 0] = 'A'
        >>> canvas[1, 1] = 'B'
        >>> canvas[2, 2] = 'C'
        >>> canvas[3, 3] = 'D'
        >>> print(canvas)
        A,,,
        ,B,,
        ,,C,
        ,,,D
        >>> canvas.vflip()
        >>> print(canvas)
        ,,,D
        ,,C,
        ,B,,
        A,,,
        """
        for y in range(0, self.height // 2):
            for x in range(0, self.width):
                self._chars[x][y], self._chars[x][self.height - 1 - y] = self._chars[x][self.height - 1 - y], self._chars[x][y]
                self._fginfo[x][y], self._fginfo[x][self.height - 1 - y] = self._fginfo[x][self.height - 1 - y], self._fginfo[x][y]
                self._bginfo[x][y], self._bginfo[x][self.height - 1 - y] = self._bginfo[x][self.height - 1 - y], self._bginfo[x][y]
        self._strDirty = True


    def hflip(self):
        """
        Horizontally flips the characters on this canvas.

        >>> canvas = Canvas(4, 4)
        >>> canvas.fill(',')
        >>> canvas[0, 0] = 'A'
        >>> canvas[1, 1] = 'B'
        >>> canvas[2, 2] = 'C'
        >>> canvas[3, 3] = 'D'
        >>> print(canvas)
        A,,,
        ,B,,
        ,,C,
        ,,,D
        >>> canvas.hflip()
        >>> print(canvas)
        ,,,A
        ,,B,
        ,C,,
        D,,,
        """
        for x in range(0, self.width // 2):
            for y in range(0, self.height):
                self._chars[x][y], self._chars[self.width - 1 - x][y] = self._chars[self.width - 1 - x][y], self._chars[x][y]
                self._fginfo[x][y], self._fginfo[self.width - 1 - x][y] = self._fginfo[self.width - 1 - x][y], self._fginfo[x][y]
                self._bginfo[x][y], self._bginfo[self.width - 1 - x][y] = self._bginfo[self.width - 1 - x][y], self._bginfo[x][y]
        self._strDirty = True


    def fill(self, char=' '):
        """Clears the entire canvas by setting every cell to `char`, which
        is ' ' by default.

        >>> canvas = Canvas(4, 4)
        >>> canvas.fill('x')
        >>> print(canvas)
        xxxx
        xxxx
        xxxx
        xxxx
        >>> canvas.fill('Q')
        >>> print(canvas)
        QQQQ
        QQQQ
        QQQQ
        QQQQ
        """
        if char is not None:
            char = str(char)
            if len(char) != 1:
                raise PyTextCanvasException('char must be a single character or None')

        for x in range(self.width):
            for y in range(self.height):
                self._chars[x][y] = char
                self._fginfo[x][y] = self._fg
                self._bginfo[x][y] = self._bg
        self._strDirty = True


    def replace(self, oldChar, newChar):
        r"""
        Replaces every instance of the `oldChar` single-character string with
        the `newChar` single-character string on the canvas.

        >>> canvas = Canvas(4, 4, loads='__He\nllo_\nworl\nd___')
        >>> print(canvas)
        __He
        llo_
        worl
        d___
        >>> canvas.replace('_', 'x')
        >>> print(canvas)
        xxHe
        llox
        worl
        dxxx
        """
        if oldChar is not None:
            oldChar = str(oldChar)
            if len(oldChar) != 1:
                raise PyTextCanvasException('oldChar must be a single character or None')

        if newChar is not None:
            newChar = str(newChar)
            if len(newChar) != 1:
                raise PyTextCanvasException('newChar must be a single character or None')

        for x in range(self.width):
            for y in range(self.height):
                if self._chars[x][y] == oldChar:
                    self._chars[x][y] = newChar
                    self._fginfo[x][y] = self.fg
                    self._bginfo[x][y] = self.bg
                    self._strDirty = True

    '''
    # TODO - implement these
    def blit(self, dstCanvas):
        pass
    '''

    def paint(self, x, y, fg=None, bg=None):
        """
        Change the foreground and/or background color of a cell on the canvas.

        `fg` and `bg` are one of the color constants CLEAR, BLACK, WHITE, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW
        """
        if self.isOnCanvas(x, y):
            if fg is not None:
                self._fginfo[x][y] = fg
            if bg is not None:
                self._bginfo[x][y] = bg


    def points(self, char, pointsIterable):
        """
        Draws the `char` character at all the (x, y) tuple coordinates in `pointsIterable`.
        """
        self._strDirty = True

        try:
            for x, y in pointsIterable:
                if self.isOnCanvas(x, y):
                    self._chars[x][y] = char
                    self._fginfo[x][y] = self.fg
                    self._bginfo[x][y] = self.bg
                    self._strDirty = True
        except PyTextCanvasException:
            raise # Reraise the exception to keep its exception message.
        except Exception:
            raise PyTextCanvasException('pointsIterable argument must be an iterable of (x, y) integer tuples')


    def square(self, char, left, top, length, filled=False, thickness=1):
        """
        Draws a square composed of `char` characters. The square's topleft
        corner is specified by `left` and `top`. The size is specified by
        `length`. If `filled` is `True`, the interior is also filled in with
        `char` characers.

        >>> canvas = Canvas(7, 7)
        >>> canvas.square('x', 0, 0, 7)
        >>> canvas.square('o', 2, 2, 5)
        >>> print(canvas)
        xxxxxxx
        x     x
        x ooooo
        x o   o
        x o   o
        x o   o
        xxooooo
        """
        pointsIterable = pybresenham.rectangle(left, top, length, length, filled, thickness)
        self.points(char, pointsIterable)

    def rectangle(self, char, left, top, width, height, filled=False, thickness=1):
        """
        Draws a rectangle composed of `char` characters. The rectangle's topleft
        corner is specified by `left` and `top`. The size is specified by
        `width` and `height`. If `filled` is `True`, the interior is also filled in with
        `char` characers.

        >>> canvas = Canvas(6, 6)
        >>> canvas.rectangle('o', 0, 0, 6, 6)
        >>> canvas.rectangle('x', 2, 2, 2, 4)
        >>> print(canvas)
        oooooo
        o    o
        o xx o
        o xx o
        o xx o
        ooxxoo
        """

        if thickness != 1:
            raise NotImplementedError('The pytextcanvas module is under development and the filled, thickness, and endcap parameters are not implemented. You can contribute at https://github.com/asweigart/pytextcanvas')

        pointsIterable = pybresenham.rectangle(left, top, width, height, filled, thickness)
        self.points(char, pointsIterable)

    def diamond(self, char, left, top, radius, filled=False, thickness=1):
        pointsIterable = pybresenham.diamond(left, top, radius, filled, thickness)
        self.points(char, pointsIterable)


    def line(self, char, x1, y1, x2, y2, thickness=1, endcap=None):
        pointsIterable = pybresenham.line(x1, y1, x2, y2, thickness, endcap)
        self.points(char, pointsIterable)


    def lines(self, char, points, closed=False, thickness=1, endcap=None):
        pointsIterable = pybresenham.lines(points, closed, thickness, endcap)
        self.points(char, pointsIterable)


    def polygon(self, char, centerx, centery, radius, sides, rotationDegrees=0, stretchHorizontal=1.0, stretchVertical=1.0, filled=False, thickness=1):
        pointsIterable = pybresenham.polygon(centerx, centery, radius, sides, rotationDegrees, stretchHorizontal, stretchVertical, filled, thickness)
        self.points(char, pointsIterable)


    def polygonVertices(self, char, centerx, centery, radius, sides, rotationDegrees=0, stretchHorizontal=1.0, stretchVertical=1.0):
        pointsIterable = pybresenham.polygonVertices(centerx, centery, radius, sides, rotationDegrees, stretchHorizontal, stretchVertical)
        self.points(char, pointsIterable)


    def floodFill(self, char, x, y):
        points = set()
        for cx in range(self.width):
            for cy in range(self.height):
                if self._chars[cx][cy] != char:
                    points.add((cx, cy))

        pointsIterable = pybresenham.floodFill(points, x, y)
        self.points(char, pointsIterable)


    def circle(self, char, centerx, centery, radius, filled=False, thickness=1):
        pointsIterable = pybresenham.circle(centerx, centery, radius, filled, thickness)
        self.points(char, pointsIterable)


    def grid(self, char, gridLeft, gridTop, numBoxesWide, numBoxesHigh, boxWidth, boxHeight, thickness=1):
        pointsIterable = pybresenham.grid(gridLeft, gridTop, numBoxesWide, numBoxesHigh, boxWidth, boxHeight, thickness)
        self.points(char, pointsIterable)


# TODO - should I use camelcase? I want to match the original Turtle module, but it uses, well, just lowercase.

    def _convertNegativeWidthIndexToPositiveIndex(self, negIndex):
        # check the type of negIndex
        if not isinstance(negIndex, int):
            raise PyTextCanvasException('x index must be of type int, not %r' % (negIndex.__class__.__name__))

        # check that negIndex is in range
        if not (-self.width <= negIndex < self.width):
            raise PyTextCanvasException('x index must be in between range of %s and %s' % (-self.width, self.width - 1))

        if negIndex < 0:
            return self.width + negIndex
        else:
            return negIndex # if negIndex is positive, just return it as is


    def _convertNegativeHeightIndexToPositiveIndex(self, negIndex):
        # check the type of negIndex
        if not isinstance(negIndex, int):
            raise PyTextCanvasException('y index must be of type int, not %r' % (negIndex.__class__.__name__))

        # check that negIndex is in range
        if not (-self.height <= negIndex < self.height):
            raise PyTextCanvasException('y index must be in between range of %s and %s' % (-self.height, self.height - 1))

        if negIndex < 0:
            return self.height + negIndex
        else:
            return negIndex # if negIndex is positive, just return it as is


    def rows(self):
        for y in range(self.height):
            yield tuple([self._chars[x][y] for x in range(self.width)])


    def cols(self):
        for x in range(self.width):
            yield tuple([self._chars[x][y] for y in range(self.height)])




if __name__ == '__main__':
    print(doctest.testmod())