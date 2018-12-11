from __future__ import division, print_function

import pytest

import pytextcanvas as pytc


def test_constants():
    """
    # Add these back in when we refactor the turtle submodule.
    # Test values of constants
    assert pytc.NORTH == 90.0
    assert pytc.SOUTH == 270.0
    assert pytc.EAST == 0.0
    assert pytc.WEST == 180.0
    assert pytc.DEFAULT_CANVAS_WIDTH == 80
    assert pytc.DEFAULT_CANVAS_HEIGHT == 25
    assert pytc.DEFAULT_PEN_CHAR == '#'

    # Test data types
    assert isinstance(pytc.NORTH, float)
    assert isinstance(pytc.SOUTH, float)
    assert isinstance(pytc.EAST, float)
    assert isinstance(pytc.WEST, float)
    assert isinstance(pytc.DEFAULT_CANVAS_WIDTH, int)
    assert isinstance(pytc.DEFAULT_CANVAS_HEIGHT, int)
    assert isinstance(pytc.DEFAULT_PEN_CHAR, str)
    """


def test_ctor():
    # Test default width and height settings.
    canvas = pytc.Canvas()
    assert canvas.width, pytc.DEFAULT_CANVAS_WIDTH
    assert canvas.height, pytc.DEFAULT_CANVAS_HEIGHT
    assert repr(canvas), "<'Canvas' object, width=%s, height=%s>" % (pytc.DEFAULT_CANVAS_WIDTH, pytc.DEFAULT_CANVAS_HEIGHT)

    assert canvas.cursor == (0, 0)

    # Test positional arguments.
    for canvas in (pytc.Canvas(width=20, height=10),
                   pytc.Canvas(20, 10, 'Alice')):
        assert canvas.width == 20
        assert canvas.height == 10
        assert canvas.area == 200
        assert canvas.size == (20, 10)
        assert canvas.colorfied == False
        assert repr(canvas) == "<'Canvas' object, width=20, height=10>"

    # Test invalid settings for ctor width and height.
    with pytest.raises(pytc.PyTextCanvasException):
        pytc.Canvas(width=3.0)
    with pytest.raises(pytc.PyTextCanvasException):
        pytc.Canvas(width='invalid')
    with pytest.raises(pytc.PyTextCanvasException):
        pytc.Canvas(width=0)
    with pytest.raises(pytc.PyTextCanvasException):
        pytc.Canvas(width=-1)

    with pytest.raises(pytc.PyTextCanvasException):
        pytc.Canvas(height=3.0)
    with pytest.raises(pytc.PyTextCanvasException):
        pytc.Canvas(height='invalid')
    with pytest.raises(pytc.PyTextCanvasException):
        pytc.Canvas(height=0)
    with pytest.raises(pytc.PyTextCanvasException):
        pytc.Canvas(height=-1)

    # Test invalid fg and bg settings.
    with pytest.raises(pytc.PyTextCanvasException):
        pytc.Canvas(fg='invalid')
    with pytest.raises(pytc.PyTextCanvasException):
        pytc.Canvas(bg='invalid')

    # Test fg and bg
    canvas = pytc.Canvas(fg=pytc.BLUE)
    assert canvas.colorfied == True
    pytc.Canvas(bg=pytc.BLUE)
    pytc.Canvas(fg=pytc.WHITE, bg=pytc.BLACK)




def test_width_height():
    # Make sure the ctor sets the width and height correctly.
    canvas = pytc.Canvas(width=4)
    assert canvas.width ==  4

    canvas = pytc.Canvas(height=4)
    assert canvas.height ==  4

    # Make sure the width, height, and area are immutable.
    with pytest.raises(AttributeError):
        canvas.width = 10
    with pytest.raises(AttributeError):
        del canvas.width
    with pytest.raises(AttributeError):
        canvas.height = 10
    with pytest.raises(AttributeError):
        del canvas.height
    with pytest.raises(AttributeError):
        canvas.area = 10
    with pytest.raises(AttributeError):
        del canvas.area


def test_colorifed_property():
    canvas = pytc.Canvas(fg=pytc.WHITE)
    assert canvas.colorfied == True
    canvas.colorfied = False
    assert canvas.colorfied == False
    canvas.colorfied = True
    assert canvas.colorfied == True

    # TODO - test to make sure color information gets stored/negated.


def test_truncate_property():
    canvas = pytc.Canvas()
    canvas.truncate = True
    assert canvas.truncate == True
    canvas.truncate = False
    assert canvas.truncate == False


def test_repr():
    canvas = pytc.Canvas()
    assert repr(canvas) == "<'Canvas' object, width=%s, height=%s>" % (pytc.DEFAULT_CANVAS_WIDTH, pytc.DEFAULT_CANVAS_HEIGHT)

    canvas = pytc.Canvas(10, 20, 'Alice')
    assert repr(canvas) == "<'Canvas' object, width=10, height=20>"


def test_str():
    canvas = pytc.Canvas(width=3, height=4)
    assert str(canvas) == '   \n   \n   \n   '

    canvas = pytc.Canvas(width=4, height=3)
    assert str(canvas) == '    \n    \n    '

def test_setitem_getitem_int_tuple_key():
    canvas = pytc.Canvas()

    # Basic write & read
    assert canvas[0, 0] == None # chars start as None
    canvas[0, 0] = 'A'
    assert canvas[0, 0] == 'A'
    canvas[1, 0] = 'B'
    assert canvas[1, 0] == 'B'

    # negative indexes
    canvas[-1, -1] = 'Z'
    canvas[-2, -1] = 'Y'
    assert canvas[-1, -1] == 'Z'
    assert canvas[-2, -1] == 'Y'
    assert canvas[79, 24] == 'Z'
    assert canvas[78, 24] == 'Y'

    with pytest.raises(pytc.PyTextCanvasException):
        canvas['invalid']

    with pytest.raises(pytc.PyTextCanvasException):
        canvas['invalid'] = 'A'

    with pytest.raises(pytc.PyTextCanvasException): # TODO - change this when we can store arbitrary values in canvas cells.
        canvas[0, 0] = 'too long string'


def test_setitem_slice():
    pass # TODO

def test_getitem_slice():
    pass # TODO returns a Canvas object


def test_setitem_getitem_keyerror():
    canvas = pytc.Canvas()

    for key in ((9999, 99999), (9999, 0), (0, 9999),
                (-9999, -9999), (-9999, 0), (0, -9999),
                (0.0, 0), (0, 0.0), (0.0, 0.0)):

        with pytest.raises(pytc.PyTextCanvasException):
            canvas[key] = 'X'

        with pytest.raises(pytc.PyTextCanvasException):
            canvas[key]


def test_getitem_setitem_slice():

    # copy entire canvas
    canvas = pytc.Canvas()
    canvas[0, 0] = 'A'
    canvas[1, 1] = 'B'
    canvas[-1, -1] = 'Z'
    assert canvas == canvas[(0,0):(pytc.DEFAULT_CANVAS_WIDTH, pytc.DEFAULT_CANVAS_HEIGHT)]
    assert canvas == canvas[None:(pytc.DEFAULT_CANVAS_WIDTH, pytc.DEFAULT_CANVAS_HEIGHT)]
    assert canvas == canvas[:(pytc.DEFAULT_CANVAS_WIDTH, pytc.DEFAULT_CANVAS_HEIGHT)]
    assert canvas == canvas[(0, 0):None]
    assert canvas == canvas[(0, 0):]
    assert canvas == canvas[None:None]
    assert canvas == canvas[:]
    assert canvas == canvas[(pytc.DEFAULT_CANVAS_WIDTH, pytc.DEFAULT_CANVAS_HEIGHT):(0,0)]

    subcanvas = pytc.Canvas(10, 1)
    subcanvas[0, 0] = 'A'
    assert subcanvas == canvas[(0,0):(10, 1)]
    assert subcanvas == canvas[(10, 1):(0,0)]

    subcanvas = pytc.Canvas(10, 2)
    subcanvas[0, 0] = 'A'
    subcanvas[1, 1] = 'B'
    assert subcanvas == canvas[(0,0):(10, 2)]
    assert subcanvas == canvas[(10, 2):(0,0)]

    # test steps
    canvas = pytc.Canvas(width=24, height=24)
    subcanvas = canvas[0,0]
    # TODO

def test_getitem_setitem_slice_errors():
    canvas = pytc.Canvas()

    with pytest.raises(pytc.PyTextCanvasException):
        canvas[(0.0, 0):]

    with pytest.raises(pytc.PyTextCanvasException):
        canvas[(0, 0.0):]

    with pytest.raises(pytc.PyTextCanvasException):
        canvas[:(0.0, 0)]

    with pytest.raises(pytc.PyTextCanvasException):
        canvas[:(0, 0.0)]


def test_equality():
    # different sizes and data types affect equality
    assert pytc.Canvas() == pytc.Canvas()
    assert pytc.Canvas() != 'hello'
    assert pytc.Canvas() != pytc.Canvas(width=81)
    assert pytc.Canvas() != pytc.Canvas(height=26)

    # cursor setting doesn't affect equality
    canvas = pytc.Canvas()
    canvas.cursor = (1, 1)
    assert canvas == pytc.Canvas()

    canvas[0, 0] = 'A'
    assert canvas, pytc.Canvas()

    canvas[0, 0] = None
    assert canvas == pytc.Canvas()


def test_shift():
    canvas = pytc.Canvas(loads='1234\n5678\nabcd\nefgh')
    canvas.shift(1, 0)
    shiftedCanvas = pytc.Canvas()
    # LEFT OFF

def test_copy():
    canvas = pytc.Canvas(4, 4)
    # LEFT OFF - uses slice to get new sub-Canvas object


def test_contains():
    canvas = pytc.Canvas(loads='hello\n world')
    assert 'hello' in canvas
    assert 'world' in canvas


def test_len():
    # TODO - tests len of string rep, not just width*height
    canvas = pytc.Canvas(10, 10)
    assert len(canvas) == 109

    canvas = pytc.Canvas(10, 1)
    assert len(canvas) == 10

    canvas = pytc.Canvas(1, 10)
    assert len(canvas) == 19

    canvas = pytc.Canvas(1, 1)
    assert len(canvas) == 1

    canvas = pytc.Canvas(10, 2)
    assert len(canvas) == 21

    canvas = pytc.Canvas(2, 10)
    assert len(canvas) == 29


def test_str_cache():
    pass # TODO
    # TODO - eventually, make it so that the strDirty bit is set only if an actual change is made.
    # TODO - set it so that the cache can be enabled or disabled


def test_slices_in_key():
    pass # TODO - tests _cehckForSlicesInKey()


def test_del():
    canvas = pytc.Canvas(10, 10)

    # Test that deleting an invalid key raises an exception
    with pytest.raises(pytc.PyTextCanvasException):
        del canvas['invalid']

    # Test that deleting a nonexistent key doesn't raise an exception
    del canvas[0, 0]
    del canvas[(0, 0):(10, 10)]

    # Test del operator
    canvas[0, 0] = 'x'
    del canvas[0, 0]
    assert canvas[0, 0] is None

    canvas[1, 0] = 'x'
    del canvas[1, 0]
    assert canvas[1, 0] is None

    canvas[0, 1] = 'x'
    del canvas[0, 1]
    assert canvas[0, 1] is None

    # Test setting to None
    canvas[0, 0] = 'x'
    canvas[0, 0] = None
    assert canvas[0, 0] is None

    canvas[1, 0] = 'x'
    canvas[1, 0] = None
    assert canvas[1, 0] is None

    canvas[0, 1] = 'x'
    canvas[0, 1] = None
    assert canvas[0, 1] is None

    # Can't delete cell by setting it to a blank string.
    with pytest.raises(pytc.PyTextCanvasException):
        canvas[0, 0] = ''

    # Delete multiple cells with a slice:
    canvas[(0, 0):(10, 10)] = 'x'
    del canvas[(0, 0):(10, 10)]
    for x in range(10):
        for y in range(10):
            assert canvas[x, y] is None

    # Delete using negative indexes
    # TODO

    # Delete using negative slices
    # TODO

    # Delete using slices with steps
    # TODO

def test_loads():
    # Test basic usage
    patternedCanvas = pytc.Canvas(3, 3)
    patternedCanvas[0, 0] = '1'
    patternedCanvas[1, 0] = '2'
    patternedCanvas[2, 0] = '3'
    patternedCanvas[0, 1] = '4'
    patternedCanvas[1, 1] = '5'
    patternedCanvas[2, 1] = '6'
    patternedCanvas[0, 2] = '7'
    patternedCanvas[1, 2] = '8'
    patternedCanvas[2, 2] = '9'

    canvas = pytc.Canvas(3, 3 , loads='123\n456\n789')
    assert canvas == patternedCanvas

    canvas = pytc.Canvas(loads='123\n456\n789')
    assert canvas == patternedCanvas

    canvas = pytc.Canvas(3, 3)
    canvas.loads('123\n456\n789')
    assert canvas == patternedCanvas
    canvas.loads('123\n456\n789')
    assert canvas == patternedCanvas

    # Test a too-large loads string
    canvas = pytc.Canvas(3, 3 , loads='123xxx\n456xx\n789x')
    assert canvas == patternedCanvas
    canvas = pytc.Canvas(3, 3 , loads='123xxx\n456xx\n789x\n')
    assert canvas == patternedCanvas

    canvas = pytc.Canvas(3, 3 , loads='123\n456\n789\nxxx')
    assert canvas == patternedCanvas
    canvas = pytc.Canvas(3, 3 , loads='123\n456\n789\nxxx\n')
    assert canvas == patternedCanvas

    canvas = pytc.Canvas(3, 3 , loads='123xxx\n456xx\n789x\nxxx')
    assert canvas == patternedCanvas
    canvas = pytc.Canvas(3, 3 , loads='123xxx\n456xx\n789x\nxxx\n')
    assert canvas == patternedCanvas

    # Test a too-small loads string
    biggerCanvas = pytc.Canvas(4, 4 , loads='123\n456\n789')
    for x in range(3):
        for y in range(3):
            assert biggerCanvas[x, y] == str((y*3) + x + 1)
    assert biggerCanvas[0, 3] is None
    assert biggerCanvas[3, 0] is None
    assert biggerCanvas[3, 3] is None

    # Test a sparse loads string
    patternedCanvas[0, 2] = None
    patternedCanvas[1, 2] = None
    patternedCanvas[2, 2] = None
    canvas = pytc.Canvas(3, 3 , loads='123\n456')
    assert canvas == patternedCanvas
    canvas = pytc.Canvas(3, 3 , loads='123\n456\n')
    assert canvas == patternedCanvas

def isOnCanvas():
    canvas = pytc.Canvas()
    assert canvas.isOnCanvas(0, 0)
    assert canvas.isOnCanvas(pytc.DEFAULT_CANVAS_WIDTH - 1, 0)
    assert canvas.isOnCanvas(0, pytc.DEFAULT_CANVAS_HEIGHT - 1)
    assert canvas.isOnCanvas(pytc.DEFAULT_CANVAS_WIDTH - 1, pytc.DEFAULT_CANVAS_HEIGHT - 1)

    assert not canvas.isOnCanvas(-1, -1)
    assert not canvas.isOnCanvas(-1, 0)
    assert not canvas.isOnCanvas(0, -1)
    assert not canvas.isOnCanvas(0, pytc.DEFAULT_CANVAS_HEIGHT)
    assert not canvas.isOnCanvas(pytc.DEFAULT_CANVAS_WIDTH, 0)
    assert not canvas.isOnCanvas(pytc.DEFAULT_CANVAS_WIDTH, pytc.DEFAULT_CANVAS_HEIGHT)


def test_rotate():
    pass

def test_scale():
    pass

def test_flip():
    pass

def test_vflip():
    pass

def test_hflip():
    pass

def test_box():
    pass

def test_fill():
    blankCanvas = pytc.Canvas(4, 4)
    canvas = pytc.Canvas(4, 4)
    assert canvas == blankCanvas

    canvas[1, 1] = 'x'
    canvas[2, 2] = 'x'
    canvas.clear()
    assert canvas == blankCanvas

    canvas.fill('x')
    assert str(canvas) == 'xxxx\nxxxx\nxxxx\nxxxx'

    canvas.fill(' ')
    assert str(canvas) == '    \n    \n    \n    '

    canvas.fill(None)
    assert str(canvas) == '    \n    \n    \n    '

    # Test argument being casted to a string
    canvas.fill(3)
    assert str(canvas) == '3333\n3333\n3333\n3333'

    # Test "char" keyword.
    canvas.fill(char='x')
    assert str(canvas) == 'xxxx\nxxxx\nxxxx\nxxxx'

    # Test exceptions
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.fill('xx')

def test_floodfill():
    pass

def test_blit():
    pass

def test_square():
    pass

def test_rect():
    pass

def test_diamond():
    pass

def test_hexagon():
    pass

def test_arrow():
    pass

def test_corner():
    pass # must be "horizontal" or "vertical"

def test_line():
    pass

def test_lines():
    pass

def test_polygon():
    pass

def test_ellipse():
    pass

def test_circle():
    pass

def test_arc():
    pass


"""
def test_forward():
    # TODO test forward and fd
    canvas = pytc.Canvas()
    assert canvas.position, (0.0, 0.0))
    assert canvas.cursor, (0, 0))

    canvas.forward(10)
    assert canvas.position, (10.0, 0.0))
    assert canvas.cursor, (10, 0))

    canvas.forward(-10)
    assert canvas.position, (0.0, 0.0))
    assert canvas.cursor, (0, 0))

    # TODO


def test_backward():
    # TODO test backward and back and bk
    canvas = pytc.Canvas()
    assert canvas.position, (0.0, 0.0))
    assert canvas.cursor, (0, 0))

    canvas.backward(-10)
    assert canvas.position, (10.0, 0.0))
    assert canvas.cursor, (10, 0))

    canvas.backward(10)
    assert canvas.position, (0.0, 0.0))
    assert canvas.cursor, (0, 0))
"""

def test_right():
    pass

def test_left():
    pass

def test_goto():
    pass

def test_setx():
    pass

def test_sety():
    pass

def test_towards():
    pass

def test_distance():
    pass

def test_degrees():
    pass

def test_radians():
    pass

def test_clear():
    blankCanvas = pytc.Canvas(4, 4)
    canvas = pytc.Canvas(4, 4)
    assert canvas == blankCanvas

    canvas[1, 1] = 'x'
    canvas[2, 2] = 'x'
    canvas.clear()
    assert canvas == blankCanvas


'''
# TODO - disable the turtle tests until we have that implementation started
def test_compass_functions():
    canvas = pytc.Canvas()
    turtle = pytc.Turtle(canvas)

    assert turtle.position == (0.0, 0.0)
    turtle.south()
    assert turtle.position == (0.0, 1.0)
    turtle.east()
    assert turtle.position == (1.0, 1.0)
    turtle.north()
    assert turtle.position == (1.0, 0.0)
    turtle.west()
    assert turtle.position == (0.0, 0.0)

    turtle.s()
    assert turtle.position == (0.0, 1.0)
    turtle.e()
    assert turtle.position == (1.0, 1.0)
    turtle.n()
    assert turtle.position == (1.0, 0.0)
    turtle.w()
    assert turtle.position == (0.0, 0.0)

    turtle.southeast()
    assert turtle.position == (1.0, 1.0)
    turtle.southwest()
    assert turtle.position == (0.0, 2.0)
    turtle.northeast()
    assert turtle.position == (1.0, 1.0)
    turtle.northwest()
    assert turtle.position == (0.0, 0.0)

    turtle.se()
    assert turtle.position == (1.0, 1.0)
    turtle.sw()
    assert turtle.position == (0.0, 2.0)
    turtle.ne()
    assert turtle.position == (1.0, 1.0)
    turtle.nw()
    assert turtle.position == (0.0, 0.0)


def test_penDown_penUp():
    blankCanvas = pytc.Canvas()
    canvas = pytc.Canvas()
    turtle = pytc.Turtle(canvas)

    assert turtle.pd == turtle.down == turtle.penDown
    assert turtle.pu == turtle.up == turtle.penUp

    turtle.penDown()
    assert turtle.isDown
    assert canvas != blankCanvas # Putting the pen down leaves a mark.
    assert canvas[0, 0] == pytc.DEFAULT_PEN_CHAR
    turtle.penUp()
    assert not turtle.isDown
    assert canvas != blankCanvas # Mark remains after lifting pen up.
    assert canvas[0, 0] == pytc.DEFAULT_PEN_CHAR

    # Test it again, just to make sure that putting the pen down and up again doesn't somehow clear the canvas.
    turtle.penDown()
    assert turtle.isDown
    assert canvas != blankCanvas # Putting the pen down leaves a mark.
    assert canvas[0, 0] == pytc.DEFAULT_PEN_CHAR
    turtle.penUp()
    assert not turtle.isDown
    assert canvas != blankCanvas # Mark remains after lifting pen up.
    assert canvas[0, 0] == pytc.DEFAULT_PEN_CHAR

    # Change the pen character, then see if the mark changes
    turtle.penChar = '+'
    assert turtle.penChar == '+'
    assert canvas[0, 0] == pytc.DEFAULT_PEN_CHAR # mark on canvas shouldn't change because pen is currently up
    turtle.penDown()
    assert turtle.isDown
    assert canvas != blankCanvas # Putting the pen down leaves a mark.
    assert canvas[0, 0] == '+'
    turtle.penUp()
    assert not turtle.isDown
    assert canvas != blankCanvas # Mark remains after lifting pen up.
    assert canvas[0, 0] == '+'

    turtle.penDown()
    turtle.penChar = 'x'
    # TODO - mark on canvas should change since pen is down


def test_accidentally_setting_penChar_on_canvas_objects():
    canvas = pytc.Canvas(10, 10)
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.penChar
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.penChar = 'A'
    with pytest.raises(pytc.PyTextCanvasException):
        del canvas.penChar

def test_setting_pen_char():
    canvas = pytc.Canvas()
    turtle = pytc.Turtle(canvas)

    assert turtle.penChar == pytc.DEFAULT_PEN_CHAR

    turtle.penChar = '+'
    assert turtle.penChar == '+'

    turtle.penChar = '#'
    assert turtle.penChar == '#'

    # Test setting pen to an invalid value
    with pytest.raises(pytc.PyTextCanvasException):
        turtle.penChar = None

    with pytest.raises(pytc.PyTextCanvasException):
        turtle.penChar = 'xx'

    with pytest.raises(pytc.PyTextCanvasException):
        turtle.penChar = ''



def test_home():
    canvas = pytc.Canvas()
    turtle = pytc.Turtle(canvas)


def test_penColor():
    pass


def test_fillColor():
    pass


def test_reset():
    pass


def test_showCursor():
    pass


def test_hideCursor():
    pass
'''

def test_isOnCanvas():
    canvas = pytc.Canvas(10, 10)
    assert canvas.isOnCanvas(0, 0)
    assert canvas.isOnCanvas(9, 9)
    assert canvas.isOnCanvas(0, 9)
    assert canvas.isOnCanvas(9, 0)
    assert not canvas.isOnCanvas(10, 0)
    assert not canvas.isOnCanvas(0, 10)
    assert not canvas.isOnCanvas(10, 10)
    assert not canvas.isOnCanvas(-1, 0)
    assert not canvas.isOnCanvas(0, -1)
    assert not canvas.isOnCanvas(-1, -1)


def test_isInside():
    assert pytc.isInside(0, 0, 0, 0, 10, 10)
    assert pytc.isInside(5, 5, 4, 4, 4, 4)
    assert not pytc.isInside(10, 0, 0, 0, 10, 10)
    assert not pytc.isInside(0, 1, 0, 0, 1, 1)
    assert not pytc.isInside(1, 1, 0, 0, 1, 1)
    assert not pytc.isInside(8, 8, 4, 4, 4, 4)
    assert not pytc.isInside(10, 10, 4, 4, 4, 4)


def test__checkForIntOrFloat():
    # int and float values don't raise an exception:
    pytc._checkForIntOrFloat(1)
    pytc._checkForIntOrFloat(1.0)

    with pytest.raises(pytc.PyTextCanvasException):
        pytc._checkForIntOrFloat('invalid')


def test_getTerminalSize():
    # This test can't reliably run, since the terminal size will be different
    # depending on the terminal that runs these tests. Let's just make sure
    # it runs without raising an exception.
    pass
    #pytc.getTerminalSize()


def test_clearScreen():
    # This test can't reliably run, since the terminal size will be different
    # depending on the terminal that runs these tests. Let's just make sure
    # it runs without raising an exception.
    pass
    #pytc.clearScreen()


def test_cursor():
    canvas = pytc.Canvas(10, 10)

    # Test reading the cursor value.
    assert canvas.cursor == (0, 0)
    assert canvas.cursorx == 0
    assert canvas.cursory == 0

    # Test writing the cursor value.
    canvas.cursor = (3, 4)
    assert canvas.cursorx == 3
    assert canvas.cursory == 4
    canvas.cursorx = 5
    assert canvas.cursorx == 5
    canvas.cursory = 6
    assert canvas.cursory == 6

    # Test negative indexes for the cursor.
    canvas.cursor = (1, -1)
    assert canvas.cursor == (1, 9)

    canvas.cursor = (-2, 1)
    assert canvas.cursor == (8, 1)

    canvas.cursorx = -3
    assert canvas.cursor == (7, 1)

    canvas.cursory = -4
    assert canvas.cursor == (7, 6)


    # Test to make sure invalid values raise an exception.
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursor = 'invalid'
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursor = (0,)
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursor = (0, 1, 2)
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursor = []
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursor = (1.1, 1)
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursor = (1, 1.1)
    with pytest.raises(AttributeError):
        del canvas.cursor

    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursorx = 'invalid'
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursorx = 1.1
    with pytest.raises(AttributeError):
        del canvas.cursorx

    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursory = 'invalid'
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursory = 1.1
    with pytest.raises(AttributeError):
        del canvas.cursory

    # Test to make sure coordinates are within the canvas.
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursor = (1, 9999)
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursor = (9999, 1)
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursor = (1, canvas.height)
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursor = (canvas.width, 1)

    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursory = 9999
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursory = canvas.height

    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursorx = 9999
    with pytest.raises(pytc.PyTextCanvasException):
        canvas.cursorx = canvas.width




if __name__ == '__main__':
    pytest.main()
