from __future__ import division, print_function

import pytest
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytextcanvas


def test_constants():
    # Test values
    assert pytextcanvas.NORTH == 90.0
    assert pytextcanvas.SOUTH == 270.0
    assert pytextcanvas.EAST == 0.0
    assert pytextcanvas.WEST == 180.0
    assert pytextcanvas.DEFAULT_CANVAS_WIDTH == 80
    assert pytextcanvas.DEFAULT_CANVAS_HEIGHT == 25
    assert pytextcanvas.DEFAULT_PEN_CHAR == '#'

    # Test data types
    assert isinstance(pytextcanvas.NORTH, float)
    assert isinstance(pytextcanvas.SOUTH, float)
    assert isinstance(pytextcanvas.EAST, float)
    assert isinstance(pytextcanvas.WEST, float)
    assert isinstance(pytextcanvas.DEFAULT_CANVAS_WIDTH, int)
    assert isinstance(pytextcanvas.DEFAULT_CANVAS_HEIGHT, int)
    assert isinstance(pytextcanvas.DEFAULT_PEN_CHAR, str)


def test_ctor():
    canvas = pytextcanvas.Canvas()
    assert canvas.width, pytextcanvas.DEFAULT_CANVAS_WIDTH
    assert canvas.height, pytextcanvas.DEFAULT_CANVAS_HEIGHT
    assert repr(canvas), "<'Canvas' object, width=%s, height=%s>" % (pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT)

    assert canvas.cursor == (0, 0)

    for canvas in (pytextcanvas.Canvas(width=20, height=10),
                   pytextcanvas.Canvas(20, 10, 'Alice')):
        assert canvas.width == 20
        assert canvas.height == 10
        assert canvas.size == 200
        assert repr(canvas) == "<'Canvas' object, width=20, height=10>"


    with pytest.raises(pytextcanvas.PyTextCanvasTypeError):
        pytextcanvas.Canvas(width='invalid')

    with pytest.raises(pytextcanvas.PyTextCanvasValueError):
        pytextcanvas.Canvas(width=-1)

    with pytest.raises(pytextcanvas.PyTextCanvasValueError):
        pytextcanvas.Canvas(width=0)

    with pytest.raises(pytextcanvas.PyTextCanvasTypeError):
        pytextcanvas.Canvas(height='invalid')

    with pytest.raises(pytextcanvas.PyTextCanvasValueError):
        pytextcanvas.Canvas(height=-1)

    with pytest.raises(pytextcanvas.PyTextCanvasValueError):
        pytextcanvas.Canvas(height=0)


def test_width_height():
    for attrName in ('width', 'height'):
        canvas = pytextcanvas.Canvas(width=4)
        assert canvas.width ==  4

        canvas = pytextcanvas.Canvas(height=4)
        assert canvas.height ==  4

        # Test invalid settings
        with pytest.raises(pytextcanvas.PyTextCanvasTypeError):
            pytextcanvas.Canvas(width=3.0)
        with pytest.raises(pytextcanvas.PyTextCanvasTypeError):
            pytextcanvas.Canvas(width='invalid')
        with pytest.raises(pytextcanvas.PyTextCanvasValueError):
            pytextcanvas.Canvas(width=0)
        with pytest.raises(pytextcanvas.PyTextCanvasValueError):
            pytextcanvas.Canvas(width=-1)
        with pytest.raises(pytextcanvas.PyTextCanvasAttributeError):
            canvas = pytextcanvas.Canvas()
            canvas.__setattr__(attrName, 10)


def test_repr():
    canvas = pytextcanvas.Canvas()
    assert repr(canvas) == "<'Canvas' object, width=%s, height=%s>" % (pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT)

    canvas = pytextcanvas.Canvas(10, 20, 'Alice')
    assert repr(canvas) == "<'Canvas' object, width=10, height=20>"


def test_str():
    canvas = pytextcanvas.Canvas(width=3, height=4)
    assert str(canvas) == '   \n   \n   \n   '

    canvas = pytextcanvas.Canvas(width=4, height=3)
    assert str(canvas) == '    \n    \n    '

def test_setitem_getitem_int_tuple_key():
    canvas = pytextcanvas.Canvas()

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

def test_setitem_slice():
    pass # TODO

def test_getitem_slice():
    pass # TODO returns a Canvas object


def test_setitem_getitem_keyerror():
    canvas = pytextcanvas.Canvas()

    for key in ((9999, 99999), (9999, 0), (0, 9999),
                (-9999, -9999), (-9999, 0), (0, -9999),
                (0.0, 0), (0, 0.0), (0.0, 0.0)):

        with pytest.raises(pytextcanvas.PyTextCanvasKeyError):
            canvas[key] = 'X'

        with pytest.raises(pytextcanvas.PyTextCanvasKeyError):
            canvas[key]


def test_getitem_setitem_slice():

    # copy entire canvas
    canvas = pytextcanvas.Canvas()
    canvas[0, 0] = 'A'
    canvas[1, 1] = 'B'
    canvas[-1, -1] = 'Z'
    assert canvas == canvas[(0,0):(pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT)]
    assert canvas == canvas[None:(pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT)]
    assert canvas == canvas[:(pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT)]
    assert canvas == canvas[(0, 0):None]
    assert canvas == canvas[(0, 0):]
    assert canvas == canvas[None:None]
    assert canvas == canvas[:]
    assert canvas == canvas[(pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT):(0,0)]

    subcanvas = pytextcanvas.Canvas(10, 1)
    subcanvas[0, 0] = 'A'
    assert subcanvas == canvas[(0,0):(10, 1)]
    assert subcanvas == canvas[(10, 1):(0,0)]

    subcanvas = pytextcanvas.Canvas(10, 2)
    subcanvas[0, 0] = 'A'
    subcanvas[1, 1] = 'B'
    assert subcanvas == canvas[(0,0):(10, 2)]
    assert subcanvas == canvas[(10, 2):(0,0)]

    # test steps
    canvas = pytextcanvas.Canvas(width=24, height=24)
    subcanvas = canvas[0,0]
    # TODO

def test_getitem_setitem_slice_errors():
    canvas = pytextcanvas.Canvas()

    with pytest.raises(pytextcanvas.PyTextCanvasKeyError):
        canvas[(0.0, 0):]

    with pytest.raises(pytextcanvas.PyTextCanvasKeyError):
        canvas[(0, 0.0):]

    with pytest.raises(pytextcanvas.PyTextCanvasKeyError):
        canvas[:(0.0, 0)]

    with pytest.raises(pytextcanvas.PyTextCanvasKeyError):
        canvas[:(0, 0.0)]


def test_equality():
    # different sizes and data types affect equality
    assert pytextcanvas.Canvas() == pytextcanvas.Canvas()
    assert pytextcanvas.Canvas() != 'hello'
    assert pytextcanvas.Canvas() != pytextcanvas.Canvas(width=81)
    assert pytextcanvas.Canvas() != pytextcanvas.Canvas(height=26)

    # cursor setting doesn't affect equality
    canvas = pytextcanvas.Canvas()
    canvas.cursor = (1, 1)
    assert canvas == pytextcanvas.Canvas()

    canvas[0, 0] = 'A'
    assert canvas, pytextcanvas.Canvas()

    canvas[0, 0] = None
    assert canvas == pytextcanvas.Canvas()


def test_shift():
    canvas = pytextcanvas.Canvas(loads='1234\n5678\nabcd\nefgh')
    canvas.shift(1, 0)
    shiftedCanvas = pytextcanvas.Canvas()
    # LEFT OFF

def test_copy():
    canvas = pytextcanvas.Canvas(4, 4)
    # LEFT OFF - uses slice to get new sub-Canvas object


def test_contains():
    canvas = pytextcanvas.Canvas(4, 4)
    for x in range(4):
        for y in range(4):
            assert (x, y) not in canvas

    canvas[1, 1] = 'x'
    canvas[2, 2] = 'x'
    assert (1, 1) in canvas
    assert (2, 2) in canvas

    del canvas[1, 1]
    assert (1, 1) not in canvas

    canvas[2, 2] = None
    assert (2, 2) not in canvas


def test_len():
    # TODO - tests len of string rep, not just width*height
    canvas = pytextcanvas.Canvas(10, 10)
    assert len(canvas) == 109

    canvas = pytextcanvas.Canvas(10, 1)
    assert len(canvas) == 10

    canvas = pytextcanvas.Canvas(1, 10)
    assert len(canvas) == 19

    canvas = pytextcanvas.Canvas(1, 1)
    assert len(canvas) == 1

    canvas = pytextcanvas.Canvas(10, 2)
    assert len(canvas) == 21

    canvas = pytextcanvas.Canvas(2, 10)
    assert len(canvas) == 29


def test_str_cache():
    pass # TODO
    # TODO - eventually, make it so that the strDirty bit is set only if an actual change is made.
    # TODO - set it so that the cache can be enabled or disabled


def test_slices_in_key():
    pass # TODO - tests _cehckForSlicesInKey()


def test_del():
    canvas = pytextcanvas.Canvas(10, 10)

    # Test that deleting an invalid key raises an exception
    with pytest.raises(pytextcanvas.PyTextCanvasKeyError):
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
    with pytest.raises(pytextcanvas.PyTextCanvasValueError):
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
    patternedCanvas = pytextcanvas.Canvas(3, 3)
    patternedCanvas[0, 0] = '1'
    patternedCanvas[1, 0] = '2'
    patternedCanvas[2, 0] = '3'
    patternedCanvas[0, 1] = '4'
    patternedCanvas[1, 1] = '5'
    patternedCanvas[2, 1] = '6'
    patternedCanvas[0, 2] = '7'
    patternedCanvas[1, 2] = '8'
    patternedCanvas[2, 2] = '9'

    canvas = pytextcanvas.Canvas(3, 3 , loads='123\n456\n789')
    assert canvas == patternedCanvas

    canvas = pytextcanvas.Canvas(loads='123\n456\n789')
    assert canvas == patternedCanvas

    canvas = pytextcanvas.Canvas(3, 3)
    canvas.loads('123\n456\n789')
    assert canvas == patternedCanvas
    canvas.loads('123\n456\n789')
    assert canvas == patternedCanvas

    # Test a too-large loads string
    canvas = pytextcanvas.Canvas(3, 3 , loads='123xxx\n456xx\n789x')
    assert canvas == patternedCanvas
    canvas = pytextcanvas.Canvas(3, 3 , loads='123xxx\n456xx\n789x\n')
    assert canvas == patternedCanvas

    canvas = pytextcanvas.Canvas(3, 3 , loads='123\n456\n789\nxxx')
    assert canvas == patternedCanvas
    canvas = pytextcanvas.Canvas(3, 3 , loads='123\n456\n789\nxxx\n')
    assert canvas == patternedCanvas

    canvas = pytextcanvas.Canvas(3, 3 , loads='123xxx\n456xx\n789x\nxxx')
    assert canvas == patternedCanvas
    canvas = pytextcanvas.Canvas(3, 3 , loads='123xxx\n456xx\n789x\nxxx\n')
    assert canvas == patternedCanvas

    # Test a too-small loads string
    biggerCanvas = pytextcanvas.Canvas(4, 4 , loads='123\n456\n789')
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
    canvas = pytextcanvas.Canvas(3, 3 , loads='123\n456')
    assert canvas == patternedCanvas
    canvas = pytextcanvas.Canvas(3, 3 , loads='123\n456\n')
    assert canvas == patternedCanvas

def isOnCanvas():
    canvas = pytextcanvas.Canvas()
    assert canvas.isOnCanvas(0, 0)
    assert canvas.isOnCanvas(pytextcanvas.DEFAULT_CANVAS_WIDTH - 1, 0)
    assert canvas.isOnCanvas(0, pytextcanvas.DEFAULT_CANVAS_HEIGHT - 1)
    assert canvas.isOnCanvas(pytextcanvas.DEFAULT_CANVAS_WIDTH - 1, pytextcanvas.DEFAULT_CANVAS_HEIGHT - 1)

    assert not canvas.isOnCanvas(-1, -1)
    assert not canvas.isOnCanvas(-1, 0)
    assert not canvas.isOnCanvas(0, -1)
    assert not canvas.isOnCanvas(0, pytextcanvas.DEFAULT_CANVAS_HEIGHT)
    assert not canvas.isOnCanvas(pytextcanvas.DEFAULT_CANVAS_WIDTH, 0)
    assert not canvas.isOnCanvas(pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT)


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
    blankCanvas = pytextcanvas.Canvas(4, 4)
    canvas = pytextcanvas.Canvas(4, 4)
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
    with pytest.raises(pytextcanvas.PyTextCanvasValueError):
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
    canvas = pytextcanvas.Canvas()
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
    canvas = pytextcanvas.Canvas()
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
    blankCanvas = pytextcanvas.Canvas(4, 4)
    canvas = pytextcanvas.Canvas(4, 4)
    assert canvas == blankCanvas

    canvas[1, 1] = 'x'
    canvas[2, 2] = 'x'
    canvas.clear()
    assert canvas == blankCanvas



def test_compass_functions():
    canvas = pytextcanvas.Canvas()
    turtle = pytextcanvas.Turtle(canvas)

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
    canvas1 = pytextcanvas.Canvas()
    canvas2 = pytextcanvas.Canvas()
    canvas3 = pytextcanvas.Canvas()
    blankCanvas = pytextcanvas.Canvas()

    for canvas, downFunc, upFunc in ((canvas1, canvas1.penDown, canvas1.penUp),
                                     (canvas2, canvas2.down, canvas2.up),
                                     (canvas3, canvas3.pd, canvas3.pu)):
        assert canvas == blankCanvas

        downFunc()
        assert canvas.isDown
        assert canvas != blankCanvas # Putting the pen down leaves a mark.
        assert canvas[0, 0] == pytextcanvas.DEFAULT_PEN_CHAR
        upFunc()
        assert not canvas.isDown
        assert canvas != blankCanvas # Mark remains after lifting pen up.
        assert canvas[0, 0] == pytextcanvas.DEFAULT_PEN_CHAR

        # Test it again, just to make sure that putting the pen down and up again doesn't somehow clear the canvas.
        downFunc()
        assert canvas.isDown
        assert canvas != blankCanvas # Putting the pen down leaves a mark.
        assert canvas[0, 0] == pytextcanvas.DEFAULT_PEN_CHAR
        upFunc()
        assert not canvas.isDown
        assert canvas != blankCanvas # Mark remains after lifting pen up.
        assert canvas[0, 0] == pytextcanvas.DEFAULT_PEN_CHAR

        # Change the pen character, then see if the mark changes
        canvas.pen = '+'
        # TODO - mark on canvas should not change
        downFunc()
        assert canvas.isDown
        assert canvas != blankCanvas # Putting the pen down leaves a mark.
        assert canvas[0, 0] == '+'
        upFunc()
        assert not canvas.isDown
        assert canvas != blankCanvas # Mark remains after lifting pen up.
        assert canvas[0, 0] == '+'

        downFunc()
        canvas.pen = 'x'
        # TODO - mark on canvas should change since pen is down

def test_setting_pen_char():
    canvas = pytextcanvas.Canvas()
    assert canvas.pen == pytextcanvas.DEFAULT_PEN_CHAR

    canvas.pen = '+'
    assert canvas.pen == '+'

    canvas.pen = '#'
    assert canvas.pen == '#'

    # Test setting pen to an invalid value
    with pytest.raises(pytextcanvas.PyTextCanvasValueError):
        canvas.pen = None

    with pytest.raises(pytextcanvas.PyTextCanvasValueError):
        canvas.pen = 'xx'

    with pytest.raises(pytextcanvas.PyTextCanvasValueError):
        canvas.pen = ''



def test_home():
    canvas = pytextcanvas.Canvas()
    turtle = pytextcanvas.Turtle()

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

def test_isOnCanvas():
    canvas = pytextcanvas.Canvas(10, 10)

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


if __name__ == '__main__':
    pytest.main()
