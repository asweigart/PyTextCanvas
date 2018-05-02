"""
PyTextCanvas is a module for writing text and ascii art to a 2D canvas in Python.


"""




"""
TODO

Change properties to descriptors
Add PyTextCanvasException class (maybe?)
Add tkinter window
Docstrings

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

import doctest
import math

from ctypes import windll, create_string_buffer

# Constants for Canvas size.
DEFAULT_CANVAS_WIDTH = 80
DEFAULT_CANVAS_HEIGHT = 25


class PyTextCanvasException(Exception):
    """Base class for PyTextCanvas exceptions."""
    pass


class PyTextCanvasValueError(PyTextCanvasException):
    """Value error class for PyTextCanvas."""
    pass


class PyTextCanvasTypeError(PyTextCanvasException):
    """Type error class for PyTextCanvas."""
    pass


class PyTextCanvasAttributeError(PyTextCanvasException):
    """Attribute error class for PyTextCanvas."""
    pass


class PyTextCanvasKeyError(PyTextCanvasException):
    """Key error class for PyTextCanvas."""
    pass


def _checkForIntOrFloat(arg):
    if not isinstance(arg, (int, float)):
        raise PyTextCanvasTypeError('argument must be int or float, not %s' % (arg.__class__.__name__))


def getTerminalSize():
    if sys.platform() == 'win32':
        # From http://code.activestate.com/recipes/440694-determine-size-of-console-window-on-windows/
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

        if res:
            import struct
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
        else:
            sizex, sizey = 80, 25 # can't determine actual size - return default values
        return sizex, sizey

    # Linux:
    # sizex, sizey = os.popen('stty size', 'r').read().split()
    # return int(sizex), int(sizey)

    #else:
    #    raise PyTextCanvasException('Cannot determine the platform')

def clearScreen():
    if sys.platform() == 'win32':
        os.system('cls')
    else:
        os.system('clear')


def getLinePoints(x1, y1, x2, y2):
    """Returns a list of (x, y) tuples of every point on a line between
    (x1, y1) and (x2, y2). The x and y values inside the tuple are integers.

    Line generated with the Bresenham algorithm.

    Args:
      x1 (int, float): The x coordinate of the line's start point.
      y1 (int, float): The y coordinate of the line's start point.
      x2 (int, float): The x coordinate of the line's end point.
      y2 (int, float): The y coordiante of the line's end point.

    Returns:
      [(x1, y1), (x2, y2), (x3, y3), ...]

    Example:
    >>> getLinePoints(0, 0, 6, 6)
    [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]
    >>> getLinePoints(0, 0, 3, 6)
    [(0, 0), (0, 1), (1, 2), (1, 3), (2, 4), (2, 5), (3, 6)]
    >>> getLinePoints(3, 3, -3, -3)
    [(3, 3), (2, 2), (1, 1), (0, 0), (-1, -1), (-2, -2), (-3, -3)]
    """

    # from http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm#Python

    # Note: Handling the case where rev == True is why it's hard to implement
    # this as an iterator.

    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    points = []
    issteep = abs(y2-y1) > abs(x2-x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = x1 > x2
    if rev:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    deltax = x2 - x1
    deltay = abs(y2-y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points


def isInside(point_x, point_y, area_left, area_top, area_width, area_height):
    """Returns True if the point of point_x, point_y is inside the area described.

    >>> isInside(0, 0, 0, 0, 1, 1)
    True
    >>> isInside(1, 0, 0, 0, 1, 1)
    False
    >>> isInside(0, 1, 0, 0, 1, 1)
    False
    >>> isInside(1, 1, 0, 0, 1, 1)
    False
    >>> isInside(5, 5, 4, 4, 4, 4)
    True
    >>> isInside(8, 8, 4, 4, 4, 4)
    False
    >>> isInside(10, 10, 4, 4, 4, 4)
    False
    """
    return (area_left <= point_x < area_left + area_width) and (area_top <= point_y < area_top + area_height)


class Canvas:
    """Initialize a new Canvas, which represents a rectangular area of
        text characters. The coordinates start in the upper left corner at
        0, 0 and coordinates increase going right and down. Each position
        in the canvas is called a cell and can contain a single text
        character.

        The size of the canvas is immutable. The size is specified in the
        intializer through the width and height parameters or with a loads
        string, which sets the size based on the maximum width and number
        of lines in the loads string.
        """
    def __init__(self, width=None, height=None, loads=None):
        """Initializes a new Canvas object."""

        if width is None and height is None and loads is not None:
            # self.width and self.height are set based on the size of the loads string
            loadsLines = loads.split('\n') # TODO - how to handle \r\n cases?
            self._width = max([len(line) for line in loadsLines])
            self._height = len(loadsLines)
        else:
            # self.width and self.height are set based on the width and height parameters
            if width is None:
                self._width = DEFAULT_CANVAS_WIDTH
            else:
                if not isinstance(width, int):
                    raise PyTextCanvasTypeError('`width` arg must be an int, not %r' % (width.__class__.__name__))
                if width < 1:
                    raise PyTextCanvasValueError('`width` arg must be 1 or greater, not %r' % (width))
                self._width = width

            if height is None:
                self._height = DEFAULT_CANVAS_HEIGHT
            else:
                if not isinstance(height, int):
                    raise PyTextCanvasTypeError('`height` arg must be an int, not %r' % (height.__class__.__name__))
                if height < 1:
                    raise PyTextCanvasValueError('`height` arg must be 1 or greater, not %r' % (height))
                self._height = height

        self.chars = {}
        self._cursor = (0, 0) # The cursors are always set to integers.

        if loads is not None:
            # Pre-populate with a string.
            self.loads(loads)

        # The cache for the __str__() function.
        self._strDirty = True
        self._strCache = None


    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        raise PyTextCanvasAttributeError('%r size is immutable' % (self.__class__.__name__))

    @width.deleter
    def width(self):
        raise PyTextCanvasAttributeError('%r size is immutable' % (self.__class__.__name__))


    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        raise PyTextCanvasAttributeError('%r size is immutable' % (self.__class__.__name__))

    @height.deleter
    def height(self):
        raise PyTextCanvasAttributeError('%r size is immutable' % (self.__class__.__name__))


    @property
    def size(self):
        return self._width * self._height

    @size.setter
    def size(self, value):
        raise PyTextCanvasAttributeError('%r size is immutable' % (self.__class__.__name__))

    @size.deleter
    def size(self):
        raise PyTextCanvasAttributeError('%r size is immutable' % (self.__class__.__name__))



    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        # TODO - validate arg
        self.goto(value[0], value[1])



    @property
    def cursorx(self):
        return self._cursor[0]

    @cursorx.setter
    def cursorx(self, value):
        self.setx(value)


    @property
    def cursory(self):
        return self._cursor[1]

    @cursory.setter
    def cursory(self, value):
        self.sety(value)


    def isOnCanvas(self, x, y):
        """
        Returns True if `x` and `y` are valid coordinates for a cell on this
        canvas.

        >>> canvas = Canvas(10, 10)
        >>> canvas.isOnCanvas(0, 0)
        True
        >>> canvas.isOnCanvas(9, 9)
        True
        >>> canvas.isOnCanvas(0, 9)
        True
        >>> canvas.isOnCanvas(9, 0)
        True
        >>> canvas.isOnCanvas(10, 0)
        False
        >>> canvas.isOnCanvas(0, 10)
        False
        >>> canvas.isOnCanvas(10, 10)
        False
        >>> canvas.isOnCanvas(-1, 0)
        False
        >>> canvas.isOnCanvas(0, -1)
        False
        >>> canvas.isOnCanvas(-1, -1)
        False
        """
        return 0 <= x < self.width and 0 <= y < self.height


    def __repr__(self):
        """Return a limited representation of this Canvas object. The width,
        and height information is included."""
        return '<%r object, width=%r, height=%r>' % \
            (self.__class__.__name__, self._width, self._height)


    def __str__(self):
        """Return a multiline string representation of this Canvas object.
        The bottom row does not end with a newline character."""

        if not self._strDirty:
            return self._strCache

        # TODO - make this thread safe
        result = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                c = self.chars.get((x, y), ' ')
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
            return self.chars.get((x, y), None)

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
            raise PyTextCanvasKeyError('key must be a tuple of two ints')

    def __setitem__(self, key, value):
        self._checkForSlicesInKey(key)

        if isinstance(key, tuple):
            if value is not None:
                value = str(value)
                if len(value) == 0:
                    raise PyTextCanvasValueError('value must have a length of 1, set to None or use del to delete a cell, or set to " " to make the cell blank')
                elif len(value) != 1:
                    raise PyTextCanvasValueError('value must have a length of 1')

            x, y = self._checkKey(key)

            if value is None and (x, y) in self.chars:
                del self[x, y]
                return

            self._strDirty = True
            self._strCache = None
            self.chars[(x, y)] = value

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
                    self[ix, iy] = value
            return

        else:
            raise PyTextCanvasKeyError('key must be a tuple of two ints')


    def __delitem__(self, key):
        self._checkForSlicesInKey(key)

        if isinstance(key, tuple):
            x, y = self._checkKey(key)

            if (x, y) in self.chars:
                self._strDirty = True
                self._strCache = None
                del self.chars[x, y]
                return

        elif isinstance(key, slice):
            self._strDirty = True
            self._strCache = None
            x1, y1, x2, y2, xStep, yStep = self._normalizeKeySlice(key)
            for ix in range(x1, x2, xStep):
                for iy in range(y1, y2, yStep):
                    if (ix, iy) in self.chars:
                        del self.chars[ix, iy]

        else:
            raise PyTextCanvasKeyError('key must be a tuple of two ints')


    def _checkForSlicesInKey(self, key):
        """Check that the user didn't incorrectly specify the slice by forgetting
        the parentheses."""
        if isinstance(key, tuple):
            for i, v in enumerate(key):
                if isinstance(v, slice):
                    raise PyTextCanvasKeyError('Use parentheses when specifying slices, i.e. spam[(0, 0):(9, 9)] not spam[0, 0:9, 9].')

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
            raise PyTextCanvasKeyError('key must be a tuple of two ints')

        x, y = tupleKey # syntactic sugar

        # check x and y are in range
        if not (-self.width <= x < self.width):
            raise PyTextCanvasKeyError('key\'s x (`%r`) is out of range' % (x))
        if not (-self.height <= y < self.height):
            raise PyTextCanvasKeyError('key\'s y (`%r`) is out of range' % (y))

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
            raise PyTextCanvasKeyError('key must be a tuple of two ints')

        return (x1, y1, x2, y2, kstep[0], kstep[1])

    def __contains__(self, item):
        return self.chars.get(item, None) is not None


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if other.width != self.width or other.height != self.height:
            return False

        for x in range(self.width):
            for y in range(self.height):
                if self[x, y] != other[x, y]:
                    return False
        return True

    def shift(self, xOffset, yOffset):
        """Shifts the characters on the canvas horizontally and vertically.
        Unlike the rotate() method, characters will not wrap around the edges
        of the canvas, but are lost instead.
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
        """Clears the entire canvas by setting every cell to None. These
        cells are transparent. To make the cells blank, call fill(' ')."""

        self.fill(None)


    def copy(self, left=0, top=0, width=None, height=None):
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        if (left, top, width, height) == (0, 0, self.width, self.height):
            # Copy the entire area, we'll just wrap __copy__().
            return self.__copy__()

        canvasCopy = Canvas(width=width, height=height)
        for x in range(width):
            for y in range(height):
                canvasCopy[x, y] = self[x + left] # LEFT OFF

    def __copy__(self):
        pass

    def loads(self, content):
        # TODO - how to handle \r?
        y = 0
        for line in str(content).split('\n'):
            for x, v in enumerate(line):
                if x >= self.width:
                    break
                self[x, y] = v
            y += 1
            if y >= self.height:
                break

    def goto(self, x, y=None):
        """Sets the curor to a specific xy point on the Canvas. `x` and `y`
        are the x and y coordinates (which can be ints or floats), or `x`
        is a tuple of two int/float values."""

        # Note: This function manipulates _position and _cursor directly.
        # These properties rely on goto() to for their functionality.
        if isinstance(x, (int, float)):
            _checkForIntOrFloat(y)

        else:
            try:
                x, y = tuple(x)
            except TypeError:
                raise PyTextCanvasTypeError('argument must be iterable of two int or float values')
            _checkForIntOrFloat(x)
            _checkForIntOrFloat(y)

        # TODO - handle

        self._cursor = (int(x), int(y))

    def rotate(self):
        pass

    def scale(self):
        pass

    def flip(self, vertical=False, horizontal=False):
        pass

    def vflip(self):
        self.flip(vertical=True, horizontal=False)

    def hflip(self):
        self.flip(vertical=False, horizontal=True)

    def fill(self, char=' '):
        """Clears the entire canvas by setting every cell to char, which
        is ' ' by default."""
        if char is not None:
            char = str(char)
            if len(char) != 1:
                raise PyTextCanvasValueError('char must be a single character')

        for x in range(self.width):
            for y in range(self.height):
                self[x, y] = char

    def blit(self, dstCanvas):
        pass

    def square(self):
        pass

    def rect(self, *args):
        pass

    def diamond(self, *args):
        pass

    def hexagon(self):
        pass

    def arrow(self):
        pass

    def corner(self):
        pass # must be "horizontal" or "vertical"

    def line(self):
        pass

    def lines(self):
        pass

    def polygon(self):
        pass

    def ellipse(self):
        pass

    def circle(self):
        pass

    def arc(self):
        pass

# TODO - should I use camelcase? I want to match the original Turtle module, but it uses, well, just lowercase.

    def _convertNegativeWidthIndexToPositiveIndex(self, negIndex):
        # check the type of negIndex
        if not isinstance(negIndex, int):
            raise PyTextCanvasTypeError('x index must be of type int, not %r' % (negIndex.__class__.__name__))

        # check that negIndex is in range
        if not (-self.width <= negIndex < self.width):
            raise PyTextCanvasValueError('x index must be in between range of %s and %s' % (-self.width, self.width - 1))

        if negIndex < 0:
            return self.width + negIndex
        else:
            return negIndex # if negIndex is positive, just return it as is


    def _convertNegativeHeightIndexToPositiveIndex(self, negIndex):
        # check the type of negIndex
        if not isinstance(negIndex, int):
            raise PyTextCanvasTypeError('y index must be of type int, not %r' % (negIndex.__class__.__name__))

        # check that negIndex is in range
        if not (-self.height <= negIndex < self.height):
            raise PyTextCanvasValueError('y index must be in between range of %s and %s' % (-self.height, self.height - 1))

        if negIndex < 0:
            return self.height + negIndex
        else:
            return negIndex # if negIndex is positive, just return it as is



# Constants for pen drawing.
NORTH = 90.0
SOUTH = 270.0
EAST = 0.0
WEST = 180.0
DEFAULT_PEN_CHAR = '#'


class Turtle(object):
    """A LOGO-like turtle to draw on a canvas."""

    def __init__(self, canvas):
        self.canvas = canvas
        self._x = 0.0
        self._y = 0.0
        self.heading = EAST

        """ Heading:
               90
                |
          180 --*-- 0
                |
               270
        """
        self._isDown = False
        self._pen = DEFAULT_PEN_CHAR

    @property
    def position(self):
        return (self._x, self._y)

    @position.setter
    def position(self, value):
        self.goto(value[0], value[1])

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self.goto(value, self.y)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self.goto(self._x, value)


    @property
    def isDown(self):
        return self._isDown

    @isDown.setter
    def isDown(self, value):
        if value:
            self.penDown()
        else:
            self.penUp()

    @property
    def pen(self):
        return self._pen

    @pen.setter
    def pen(self, value):
        value = str(value)
        if len(value) != 1:
            raise PyTextCanvasValueError('pen must be set to a single character string')

        self._pen = value

    def __repr__(self):
        """Returns a string representation of the Turtle object, including its coordiantes."""
        return '<%r object, x=%r, y=%r, pen=%r>' % \
            (self.__class__.__name__, self._x, self._y, self._pen)


    def __eq__(self, other):
        try:
            return self._x == other[0] and self._y == other[1]
        except:
            pass # Nothing need to be done if other wasn't an iterable.

        if not isinstance(other, self.__class__):
            return False

        return self._x == other._x and self._y == other._y


    def forward(self, distance):
        # TODO - note that the position can move off of the edge of the canvas. Any drawing done here is lost.
        pass

    fd = forward

    def backward(self, distance):
        pass

    bk = back = backward

    def right(self, angle):
        pass

    rt = right

    def left(self, angle):
        pass

    lt = left


    def goto(self, x, y=None):
        """Sets the curor to a specific xy point on the Canvas. `x` and `y`
        are the x and y coordinates (which can be ints or floats), or `x`
        is a tuple of two int/float values."""

        # Note: This function manipulates _position and _cursor directly.
        # These properties rely on goto() to for their functionality.
        if isinstance(x, (int, float)):
            _checkForIntOrFloat(y)

        else:
            try:
                x, y = tuple(x)
            except TypeError:
                raise PyTextCanvasTypeError('argument must be iterable of two int or float values')
            _checkForIntOrFloat(x)
            _checkForIntOrFloat(y)

        # TODO - handle

        self._position = (x, y)


    setpost = setposition = goto

    def setx(self, x):
        self.goto(x, self.position[1])

    def sety(self, y):
        self.goto(self.position[0], y)

    def setheading(self, toAngle):
        pass

    seth = setheading


    def north(self, distance=1.0):
        """Move the turtle cursor north (upwards).

        Args:
            distance: An int or float for how far to move the cursor. This
            number can also be negative.
        """
        _checkForIntOrFloat(distance)
        self._y -= distance
    n = north

    def south(self, distance=1.0):
        """Move the turtle cursor south (downwards).

        Args:
            distance: An int or float for how far to move the cursor. This
            number can also be negative.
        """
        _checkForIntOrFloat(distance)
        self._y += distance
    s = south

    def east(self, distance=1.0):
        """Move the turtle cursor east (right).

        Args:
            distance: An int or float for how far to move the cursor. This
            number can also be negative.
        """
        _checkForIntOrFloat(distance)
        self._x += distance
    e = east

    def west(self, distance=1.0):
        """Move the turtle cursor west (left).

        Args:
            distance: An int or float for how far to move the cursor. This
            number can also be negative.
        """
        _checkForIntOrFloat(distance)
        self._x -= distance
    w = west

    def northeast(self, distance=1.0):
        """Move the turtle cursor northeast (up and right).

        Args:
            distance: An int or float for how far to move the cursor. This
            number can also be negative.
        """
        _checkForIntOrFloat(distance)
        self._x += distance
        self._y -= distance
    ne = northeast

    def northwest(self, distance=1.0):
        """Move the turtle cursor northwest (up and left).

        Args:
            distance: An int or float for how far to move the cursor. This
            number can also be negative.
        """
        _checkForIntOrFloat(distance)
        self._x -= distance
        self._y -= distance
    nw = northwest

    def southeast(self, distance=1.0):
        """Move the turtle cursor southeast (down and right).

        Args:
            distance: An int or float for how far to move the cursor. This
            number can also be negative.
        """
        _checkForIntOrFloat(distance)
        self._x += distance
        self._y += distance
    se = southeast

    def southwest(self, distance=1.0):
        """Move the turtle cursor southwest (down and left).

        Args:
            distance: An int or float for how far to move the cursor. This
            number can also be negative.
        """
        _checkForIntOrFloat(distance)
        self._x -= distance
        self._y += distance
    sw = southwest


    def home(self):
        self._x = 0.0
        self._y = 0.0

    # NOTE: No undo in PyTextCanvas.

    def towards(self, x, y=None):
        pass

    def distance(self, x, y=None):
        pass

    def degrees(self):
        pass

    def radians(self):
        pass

    def penDown(self):
        self._isDown = True
        x, y = self.cursor
        if self.isOnCanvas(x, y):
            self[x, y] = self.pen

    pd = down = penDown

    def penUp(self):
        self._isDown = False

    pu = up = penUp

    def penColor(self):
        pass # TODO - rename to just "color"?

    def fillColor(self):
        pass

    """
    def filling(self):
        pass

    def begin_fill(self):
        pass

    def end_fill(self):
        pass
    """

    def reset(self):
        pass

    #def write(self):
    #    pass

    def showCursor(self):
        pass

    sc = showCursor

    def hideCursor(self):
        pass

    hc = hideCursor



class CanvasDict(dict):
    # TODO - a way to add generic data to the canvas (such as fg or bg)
    def __init__(self, width, height):
        pass # TODO

    def __getitem__(self):
        pass

    def __setitem__(self, value):
        pass


class Scene:
    def __init__(self, canvasesAndPositions):
        self.canvasesAndPositions = []
        # NOTE: The Canvas at index 0 is significant because it sets the size
        # of the entire Scene. All other Canvases will be truncated to fit.

        try:
            for i, canvasAndPosition in enumerate(self.canvasesAndPositions):
                canvas, top, left = canvasAndPosition
                if not isinstance(canvas, Canvas):
                    raise PyTextCanvasTypeError('item at index %s does not have Canvas object' % (i))
                if not isinstance(top, int):
                    raise PyTextCanvasTypeError('item at index %s does not have an int top value' % (i))
                if not isinstance(left, int):
                    raise PyTextCanvasTypeError('item at index %s does not have an int left value' % (i))
                self.canvasesAndPositions.appendCanvas(*(canvas, top, left))
        except TypeError:
            raise PyTextCanvasTypeError('%r object is not iterable' % (canvasesAndPositions.__class__.__name__))

    def __len__(self):
        if self.canvasesAndPositions == []:
            return 0
        else:
            return len(self.canvasesAndPositions[0][0])

    def __str__(self):
        pass # TODO

    def __eq__(self, other):
        pass # TODO - can be compared against Canvas objects and other Scene objects.

    # TODO - implement __getitem__ and __setitem__ and __del__ as well? How do we move the canvases around?

    def __iadd__(self, other):
        pass # TODO - calls appendCanvas.

    def appendCanvas(self, canvas, top, left):
        pass

    def moveCanvas(self, indexName, movex, movey):
        pass # used to move the canvas around



    def append(self, canvas, position):
        pass



if __name__ == '__main__':
    doctest.testmod()