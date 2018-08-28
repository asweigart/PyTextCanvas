"""
PyTextCanvas is a module for writing text and ascii art to a 2D canvas in Python.


"""




"""
TODO

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

__version__ = '0.0.2'

import doctest
import math
import os
import sys

import pybresenham

# Constants for Canvas size.
DEFAULT_CANVAS_WIDTH = 80
DEFAULT_CANVAS_HEIGHT = 25


# Based off of the CSS3 standard names. Data from James Bennett's webcolors module: https://github.com/ubernostrum/webcolors
COLOR_NAMES_TO_HEX = {'aliceblue': '#f0f8ff','antiquewhite': '#faebd7','aqua': '#00ffff','aquamarine': '#7fffd4','azure': '#f0ffff','beige': '#f5f5dc','bisque': '#ffe4c4','black': '#000000','blanchedalmond': '#ffebcd','blue': '#0000ff','blueviolet': '#8a2be2','brown': '#a52a2a','burlywood': '#deb887','cadetblue': '#5f9ea0','chartreuse': '#7fff00','chocolate': '#d2691e','coral': '#ff7f50','cornflowerblue': '#6495ed','cornsilk': '#fff8dc','crimson': '#dc143c','cyan': '#00ffff','darkblue': '#00008b','darkcyan': '#008b8b','darkgoldenrod': '#b8860b','darkgray': '#a9a9a9','darkgrey': '#a9a9a9','darkgreen': '#006400','darkkhaki': '#bdb76b','darkmagenta': '#8b008b','darkolivegreen': '#556b2f','darkorange': '#ff8c00','darkorchid': '#9932cc','darkred': '#8b0000','darksalmon': '#e9967a','darkseagreen': '#8fbc8f','darkslateblue': '#483d8b','darkslategray': '#2f4f4f','darkslategrey': '#2f4f4f','darkturquoise': '#00ced1','darkviolet': '#9400d3','deeppink': '#ff1493','deepskyblue': '#00bfff','dimgray': '#696969','dimgrey': '#696969','dodgerblue': '#1e90ff','firebrick': '#b22222','floralwhite': '#fffaf0','forestgreen': '#228b22','fuchsia': '#ff00ff','gainsboro': '#dcdcdc','ghostwhite': '#f8f8ff','gold': '#ffd700','goldenrod': '#daa520','gray': '#808080','grey': '#808080','green': '#008000','greenyellow': '#adff2f','honeydew': '#f0fff0','hotpink': '#ff69b4','indianred': '#cd5c5c','indigo': '#4b0082','ivory': '#fffff0','khaki': '#f0e68c','lavender': '#e6e6fa','lavenderblush': '#fff0f5','lawngreen': '#7cfc00','lemonchiffon': '#fffacd','lightblue': '#add8e6','lightcoral': '#f08080','lightcyan': '#e0ffff','lightgoldenrodyellow': '#fafad2','lightgray': '#d3d3d3','lightgrey': '#d3d3d3','lightgreen': '#90ee90','lightpink': '#ffb6c1','lightsalmon': '#ffa07a','lightseagreen': '#20b2aa','lightskyblue': '#87cefa','lightslategray': '#778899','lightslategrey': '#778899','lightsteelblue': '#b0c4de','lightyellow': '#ffffe0','lime': '#00ff00','limegreen': '#32cd32','linen': '#faf0e6','magenta': '#ff00ff','maroon': '#800000','mediumaquamarine': '#66cdaa','mediumblue': '#0000cd','mediumorchid': '#ba55d3','mediumpurple': '#9370db','mediumseagreen': '#3cb371','mediumslateblue': '#7b68ee','mediumspringgreen': '#00fa9a','mediumturquoise': '#48d1cc','mediumvioletred': '#c71585','midnightblue': '#191970','mintcream': '#f5fffa','mistyrose': '#ffe4e1','moccasin': '#ffe4b5','navajowhite': '#ffdead','navy': '#000080','oldlace': '#fdf5e6','olive': '#808000','olivedrab': '#6b8e23','orange': '#ffa500','orangered': '#ff4500','orchid': '#da70d6','palegoldenrod': '#eee8aa','palegreen': '#98fb98','paleturquoise': '#afeeee','palevioletred': '#db7093','papayawhip': '#ffefd5','peachpuff': '#ffdab9','per': '#cd853f','pink': '#ffc0cb','plum': '#dda0dd','powderblue': '#b0e0e6','purple': '#800080','red': '#ff0000','rosybrown': '#bc8f8f','royalblue': '#4169e1','saddlebrown': '#8b4513','salmon': '#fa8072','sandybrown': '#f4a460','seagreen': '#2e8b57','seashell': '#fff5ee','sienna': '#a0522d','silver': '#c0c0c0','skyblue': '#87ceeb','slateblue': '#6a5acd','slategray': '#708090','slategrey': '#708090','snow': '#fffafa','springgreen': '#00ff7f','steelblue': '#4682b4','tan': '#d2b48c','teal': '#008080','thistle': '#d8bfd8','tomato': '#ff6347','turquoise': '#40e0d0','violet': '#ee82ee','wheat': '#f5deb3','white': '#ffffff','whitesmoke': '#f5f5f5','yellow': '#ffff00','yellowgreen': '#9acd32',}

def hexColor(color):
    """
    Converts the `color` parameter to a standard '#ffffff' color string of a # followed by six hexadecimal digits. The `color` parameter can formatted as a CSS3 name, #ffffff, ffffff, #fff, or fff.

    TODO: Expand to include rgb triplet integers, and three percentages?

    >>> hexColor('white')
    '#ffffff'
    >>> hexColor('#ffffff')
    '#ffffff'
    >>> hexColor('#fff')
    '#ffffff'
    >>> hexColor('ffffff')
    '#ffffff'
    >>> hexColor('fff')
    '#ffffff'
    >>> hexColor('#abc')
    '#aabbcc'
    """
    if type(color) != str:
        raise TypeError('Parameter `color` must be of type str, not %s.' % (type(color)))

    color = color.lower() # normalize to lowercase

    if color in COLOR_NAMES_TO_HEX:
        return COLOR_NAMES_TO_HEX[color]

    if color.startswith('#'):
        color = color[1:] # remove the leading #

    try:
        int(color, 16) # check that it's a hexadecimal number
        if len(color) == 3:
            return '#' + color[0] + color[0] + color[1] + color[1] + color[2] + color[2] # normalize to '#ffffff' format
        elif len(color) == 6:
            return '#' + color
        else:
            raise ValueError('Parameter `color` must be a hexadecimal number or valid color name.')
    except ValueError:
        raise ValueError('Parameter `color` must be a hexadecimal number, not %s.' % (type(color)))


def _checkForIntOrFloat(arg):
    if not isinstance(arg, (int, float)):
        raise PyTextCanvasException('argument must be int or float, not %s' % (arg.__class__.__name__))


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


def clearScreen():
    """
    Clears the terminal by calling `cls` or `clear`, depending on what platform
    this Python script is running from.
    """
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')


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


'''
# TODO - decide if this is a good idea
def charGrid(width=80, height=25):
    pass # TODO - A drastically simplified Canvas.


def printCharGrid(charGrid):
    pass
'''

class Canvas:
    def __init__(self, width=None, height=None, loads=None, fg='#000000', bg='#ffffff'):
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
        self._truncate = False # By default, text written beyond the edges of the canvas will raise exceptions, unless self._truncate is True.

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

        # The foreground & background of each cell in the canvas. These are
        # stored as strings like html color settings, i.e. '#ffffff'. The None
        # value represents the default canvas setting. If both fg and bg
        # are set to None, this canvas isn't "colorfied" and doesn't have
        # color information stored (to save memory).
        if fg is None and bg is None:
            self.colorfied = False
            # defaultFg, defaultBg, fg, and bg remain uninitialized.
        else:
            self.colorfied = True
            self.defaultFg = fg
            self.defaultBg = bg
            self.fg = [[None] * self._height for i in range(self._width)]
            self.bg = [[None] * self._height for i in range(self._width)]
        # TODO - the rest of the color implementation needs to be done.

        self._cursor = (0, 0) # The cursor is always set to integers.

        if loads is not None:
            # Pre-populate with a string.
            self.loads(loads)

        self._strCache = None # Cached returned value from __str__()
        self._strDirty = True # If False, __str__() uses the cached value.


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


    @property
    def truncate(self):
        """
        By default, attempting to write characters beyond the edges of the
        canvas will raise PyTextCanvasException, unless `truncate` is set
        to True.

        If the `truncate` attribute is `True`, this will override any
        `truncate` method argument settings.
        """
        return self._truncate

    @truncate.setter
    def truncate(self, value):
        self._truncate = bool(value)


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


    '''
    def printCanvas(self):
        """TODO Prints the canvas to the screen. Colors are displayed using Colorama."""
        pass
    '''

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

    '''
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

        # TODO - finish

    def __copy__(self):
        pass
    '''

    def loads(self, content, truncate=True):
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
        if self._truncate: # The truncate setting overrides this truncate argument.
            truncate = True

        if not truncate:
            lines = content.split('\n')
            if len(lines) > self.height:
                raise PyTextCanvasException('content argument is too tall for this canvas, pass True for truncate to ignore this error')
            if max([len(line) for line in lines]) > self.width:
                raise PyTextCanvasException('content argument is too wide for this canvas, pass True for truncate to ignore this error')

        y = 0
        for line in str(content).split('\n'):
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
                    self._strDirty = True

    '''
    # TODO - implement these
    def blit(self, dstCanvas):
        pass
    '''

    def points(self, char, pointsIterable, truncate=True):
        """
        Draws the `char` character at all the (x, y) tuple coordinates in `pointsIterable`.
        """
        if self._truncate: # The truncate setting overrides this truncate argument.
            truncate = True

        self._strDirty = True

        try:
            for x, y in pointsIterable:
                if self.isOnCanvas(x, y):
                    self._chars[x][y] = char
                    self._strDirty = True
                elif not truncate:
                    raise PyTextCanvasException('shape includes positions beyond the edge of the canvas')
        except PyTextCanvasException:
            raise # Reraise the exception to keep its exception message.
        except Exception:
            raise PyTextCanvasException('pointsIterable argument must be an iterable of (x, y) integer tuples')


    def square(self, char, left, top, length, filled=False, thickness=1, truncate=True):
        """
        Draws a square composed of `char` characters. The square's topleft
        corner is specified by `left` and `top`. The size is specified by
        `length`. If `filled` is `True`, the interior is also filled in with
        `char` characers.

        This method will raise `PyTextCanvasException` if the square goes
        beyond the edges of the canvas, unless `truncate` is set to `True`
        or the canvas's `truncate` attribute is `True`.

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
        self.points(char, pointsIterable, truncate)

    def rectangle(self, char, left, top, width, height, filled=False, thickness=1, truncate=True):
        """
        Draws a rectangle composed of `char` characters. The rectangle's topleft
        corner is specified by `left` and `top`. The size is specified by
        `width` and `height`. If `filled` is `True`, the interior is also filled in with
        `char` characers.

        This method will raise `PyTextCanvasException` if the square goes
        beyond the edges of the canvas, unless `truncate` is set to `True`
        or the canvas's `truncate` attribute is `True`.

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
        self.points(char, pointsIterable, truncate)

    def diamond(self, char, x, y, radius, filled=False, thickness=1, truncate=True):
        pointsIterable = pybresenham.diamond(x, y, radius, filled, thickness)
        self.points(char, pointsIterable, truncate)


    def line(self, char, x1, y1, x2, y2, thickness=1, endcap=None, truncate=True):
        pointsIterable = pybresenham.line(x1, y1, x2, y2, thickness, endcap)
        self.points(char, pointsIterable, truncate)


    def lines(self, char, points, closed=False, thickness=1, endcap=None, truncate=True):
        pointsIterable = pybresenham.lines(points, closed, thickness, endcap)
        self.points(char, pointsIterable, truncate)


    def polygon(self, char, x, y, radius, sides, rotationDegrees=0, stretchHorizontal=1.0, stretchVertical=1.0, filled=False, thickness=1, truncate=True):
        pointsIterable = pybresenham.polygon(char, x, y, radius, sides, rotationDegrees, stretchHorizontal, stretchVertical, filled, thickness)
        self.points(char, pointsIterable, truncate)


    def polygonVertices(self, char, x, y, radius, sides, rotationDegrees=0, stretchHorizontal=1.0, stretchVertical=1.0, truncate=True):
        pointsIterable = pybresenham.polygonVertices(x, y, radius, sides, rotationDegrees, stretchHorizontal, stretchVertical)
        self.points(char, pointsIterable, truncate)


    def floodFill(self, char, x, y, truncate=True):
        points = set()
        for cx in range(self.width):
            for cy in range(self.height):
                if self._chars[cx][cy] != char:
                    points.add((cx, cy))

        pointsIterable = pybresenham.floodFill(points, x, y)
        self.points(char, pointsIterable, truncate)


    def circle(self, char, x, y, radius, filled=False, thickness=1, truncate=True):
        pointsIterable = pybresenham.circle(x, y, radius, filled, thickness)
        self.points(char, pointsIterable, truncate)


    def grid(self, char, gridLeft, gridTop, numBoxesWide, numBoxesHigh, boxWidth, boxHeight, thickness=1, truncate=True):
        pointsIterable = pybresenham.grid(gridLeft, gridTop, numBoxesWide, numBoxesHigh, boxWidth, boxHeight, thickness)
        self.points(char, pointsIterable, truncate)


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


# Constants for pen drawing.
NORTH = 90.0
SOUTH = 270.0
EAST = 0.0
WEST = 180.0
DEFAULT_PEN_CHAR = '#'

'''
# TODO - to be implemented

class Turtle(object):
    """A LOGO-like turtle to draw on a canvas. The "turtle" is a position on
    the canvas that can be moved around using turtle-like movement methods,
    drawing characters to the canvas as it moves around. The method names
    have been chosen to be similar to the Python Standard Library's `turtle`
    module.
    """

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
        self._penChar = DEFAULT_PEN_CHAR

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
    def penChar(self):
        return self._penChar

    @penChar.setter
    def penChar(self, value):
        if not isinstance(value, str) or len(value) != 1:
            raise PyTextCanvasException('penChar must be set to a single character string')
        self._penChar = value
        if self.isDown and self.canvas.isOnCanvas(self.x, self.y):
            self.canvas._strDirty = True
            self.canvas._chars[int(self._x)][int(self._y)] = self._penChar


    def __repr__(self):
        """Returns a string representation of the Turtle object, including its coordiantes."""
        return '<%r object, x=%r, y=%r, pen=%r>' % \
            (self.__class__.__name__, self._x, self._y, self._penChar)


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
                raise PyTextCanvasException('argument must be iterable of two int or float values')
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
        if self.canvas.isOnCanvas(self.x, self.y):
            self.canvas._strDirty = True
            self.canvas._chars[int(self.x)][int(self.y)] = self._penChar

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
'''

'''
# TODO - to be implemented
class CanvasDict(dict):
    # TODO - a way to add generic data to the canvas (such as fg or bg)
    def __init__(self, width, height):
        pass # TODO

    def __getitem__(self):
        pass

    def __setitem__(self, value):
        pass


class Scene: # TODO - rename to "ChainCanvas" or "CanvasChain"?
    def __init__(self, canvasesAndPositions):
        self.canvasesAndPositions = []
        # NOTE: The Canvas at index 0 is significant because it sets the size
        # of the entire Scene. All other Canvases will be truncated to fit.

        try:
            for i, canvasAndPosition in enumerate(self.canvasesAndPositions):
                canvas, top, left = canvasAndPosition
                if not isinstance(canvas, Canvas):
                    raise PyTextCanvasException('item at index %s does not have Canvas object' % (i))
                if not isinstance(top, int):
                    raise PyTextCanvasException('item at index %s does not have an int top value' % (i))
                if not isinstance(left, int):
                    raise PyTextCanvasException('item at index %s does not have an int left value' % (i))
                self.canvasesAndPositions.appendCanvas(*(canvas, top, left))
        except TypeError:
            raise PyTextCanvasException('%r object is not iterable' % (canvasesAndPositions.__class__.__name__))

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
'''


if __name__ == '__main__':
    print(doctest.testmod())