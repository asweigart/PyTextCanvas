# TODO - to be implemented, currently not accessible through pytextcanvas



# Constants for pen drawing.
NORTH = 90.0
SOUTH = 270.0
EAST = 0.0
WEST = 180.0
DEFAULT_PEN_CHAR = '#'



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
