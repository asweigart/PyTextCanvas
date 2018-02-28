from __future__ import division, print_function

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytextcanvas


class TestBasics(unittest.TestCase):
    def test_ctor(self):
        canvas = pytextcanvas.Canvas()
        self.assertEqual(canvas.width, pytextcanvas.DEFAULT_CANVAS_WIDTH)
        self.assertEqual(canvas.height, pytextcanvas.DEFAULT_CANVAS_HEIGHT)
        self.assertEqual(canvas.name, '')
        self.assertEqual(repr(canvas), "<'Canvas' object, width=%s, height=%s, name=''>" % (pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT))

        self.assertEqual(canvas.cursor, (0, 0))
        self.assertEqual(canvas.heading, pytextcanvas.EAST)
        self.assertEqual(canvas.penIsDown, False)


        for canvas in (pytextcanvas.Canvas(width=20, height=10, name='Alice'),
                       pytextcanvas.Canvas(20, 10, 'Alice')):
            self.assertEqual(canvas.width, 20)
            self.assertEqual(canvas.height, 10)
            self.assertEqual(canvas.name, 'Alice')
            self.assertEqual(repr(canvas), "<'Canvas' object, width=20, height=10, name='Alice'>")


        with self.assertRaises(TypeError):
            pytextcanvas.Canvas(width='invalid')

        with self.assertRaises(ValueError):
            pytextcanvas.Canvas(width=-1)

        with self.assertRaises(ValueError):
            pytextcanvas.Canvas(width=0)

        with self.assertRaises(TypeError):
            pytextcanvas.Canvas(height='invalid')

        with self.assertRaises(ValueError):
            pytextcanvas.Canvas(height=-1)

        with self.assertRaises(ValueError):
            pytextcanvas.Canvas(height=0)


    def test_width_height(self):
        for attrName in ('width', 'height'):
            canvas = pytextcanvas.Canvas(**{attrName: 4})
            self.assertEqual(canvas.__getattribute__(attrName), 4)

            canvas = pytextcanvas.Canvas(**{attrName: 3.0})
            self.assertEqual(canvas.__getattribute__(attrName), 3)

            with self.assertRaises(TypeError):
                pytextcanvas.Canvas(**{attrName: 'invalid'})

            with self.assertRaises(ValueError):
                pytextcanvas.Canvas(**{attrName: 0})

            with self.assertRaises(ValueError):
                pytextcanvas.Canvas(**{attrName: -1})

            with self.assertRaises(TypeError):
                canvas = pytextcanvas.Canvas()
                canvas.__setattr__(attrName, 10)


    def test_name(self):
        canvas = pytextcanvas.Canvas()

        self.assertEqual(canvas.name, '')

        canvas.name = 'Alice'
        self.assertEqual(canvas.name, 'Alice')

        canvas.name = ''
        self.assertEqual(canvas.name, '')



    def test_repr(self):
        canvas = pytextcanvas.Canvas()
        self.assertEqual(repr(canvas), "<'Canvas' object, width=%s, height=%s, name=''>" % (pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT))

        canvas = pytextcanvas.Canvas(10, 20, 'Alice')
        self.assertEqual(repr(canvas), "<'Canvas' object, width=10, height=20, name='Alice'>")

        canvas.name = None
        self.assertEqual(repr(canvas), "<'Canvas' object, width=10, height=20, name=None>")


    def test_str(self):
        canvas = pytextcanvas.Canvas(width=3, height=4)
        self.assertEqual(str(canvas), '   \n   \n   \n   ')

        canvas = pytextcanvas.Canvas(width=4, height=3)
        self.assertEqual(str(canvas), '    \n    \n    ')

    def test_setitem_getitem_int_tuple_key(self):
        canvas = pytextcanvas.Canvas()

        # Basic write & read
        self.assertEqual(canvas[0, 0], None) # chars start as None
        canvas[0, 0] = 'A'
        self.assertEqual(canvas[0, 0], 'A')
        canvas[1, 0] = 'B'
        self.assertEqual(canvas[1, 0], 'B')

        # negative indexes
        canvas[-1, -1] = 'Z'
        canvas[-2, -1] = 'Y'
        self.assertEqual(canvas[-1, -1], 'Z')
        self.assertEqual(canvas[-2, -1], 'Y')
        self.assertEqual(canvas[79, 24], 'Z')
        self.assertEqual(canvas[78, 24], 'Y')

    def test_setitem_slice(self):
        pass # TODO

    def test_getitem_slice(self):
        pass # TODO returns a Canvas object


    def test_setitem_getitem_keyerror(self):
        canvas = pytextcanvas.Canvas()

        for key in ((9999, 99999), (9999, 0), (0, 9999),
                    (-9999, -9999), (-9999, 0), (0, -9999),
                    (0.0, 0), (0, 0.0), (0.0, 0.0)):

            with self.assertRaises(KeyError):
                canvas[key] = 'X'

            with self.assertRaises(KeyError):
                canvas[key]


    def test_getitem_setitem_slice(self):

        # copy entire canvas
        canvas = pytextcanvas.Canvas()
        canvas[0, 0] = 'A'
        canvas[1, 1] = 'B'
        canvas[-1, -1] = 'Z'
        self.assertEqual(canvas[(0,0):(pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT)], canvas)
        self.assertEqual(canvas[None:(pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT)], canvas)
        self.assertEqual(canvas[:(pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT)], canvas)
        self.assertEqual(canvas[(0, 0):None], canvas)
        self.assertEqual(canvas[(0, 0):], canvas)
        self.assertEqual(canvas[None:None], canvas)
        self.assertEqual(canvas[:], canvas)
        self.assertEqual(canvas[(pytextcanvas.DEFAULT_CANVAS_WIDTH, pytextcanvas.DEFAULT_CANVAS_HEIGHT):(0,0)], canvas)

        subcanvas = pytextcanvas.Canvas(10, 1)
        subcanvas[0, 0] = 'A'
        self.assertEqual(canvas[(0,0):(10, 1)], subcanvas)
        self.assertEqual(canvas[(10, 1):(0,0)], subcanvas)

        subcanvas = pytextcanvas.Canvas(10, 2)
        subcanvas[0, 0] = 'A'
        subcanvas[1, 1] = 'B'
        self.assertEqual(canvas[(0,0):(10, 2)], subcanvas)
        self.assertEqual(canvas[(10, 2):(0,0)], subcanvas)

        # test steps
        canvas = pytextcanvas.Canvas(width=24, height=24)
        subcanvas = canvas[0,0]
        # TODO

    def test_getitem_setitem_slice_errors(self):
        canvas = pytextcanvas.Canvas()

        with self.assertRaises(KeyError):
            canvas[(0.0, 0):]

        with self.assertRaises(KeyError):
            canvas[(0, 0.0):]

        with self.assertRaises(KeyError):
            canvas[:(0.0, 0)]

        with self.assertRaises(KeyError):
            canvas[:(0, 0.0)]


    def test_equality(self):
        # different sizes and data types affect equality
        self.assertEqual(pytextcanvas.Canvas(), pytextcanvas.Canvas())
        self.assertNotEqual(pytextcanvas.Canvas(), 'hello')
        self.assertNotEqual(pytextcanvas.Canvas(), pytextcanvas.Canvas(width=81))
        self.assertNotEqual(pytextcanvas.Canvas(), pytextcanvas.Canvas(height=26))

        # cursor setting doesn't affect equality
        canvas = pytextcanvas.Canvas()
        canvas.cursor = (1, 1)
        self.assertEqual(canvas, pytextcanvas.Canvas())

        canvas[0, 0] = 'A'
        self.assertNotEqual(canvas, pytextcanvas.Canvas())

        canvas[0, 0] = None
        self.assertEqual(canvas, pytextcanvas.Canvas())


    def test_shift(self):
        pass

    def test_copy(self):
        canvas = pytextcanvas.Canvas(4, 4)
        # LEFT OFF - uses slice to get new sub-Canvas object

    def test_contains(self):
        canvas = pytextcanvas.Canvas(4, 4)
        for x in range(4):
            for y in range(4):
                self.assertFalse((x, y) in canvas)

        canvas[1, 1] = 'x'
        canvas[2, 2] = 'x'
        self.assertTrue((1, 1) in canvas)
        self.assertTrue((2, 2) in canvas)

        del canvas[1, 1]
        self.assertFalse((1, 1) in canvas)

        canvas[2, 2] = None
        self.assertFalse((2, 2) in canvas)


    def test_len(self):

        # TODO - tests len of string rep, not just width*height
        canvas = pytextcanvas.Canvas(10, 10)
        self.assertEqual(len(canvas), 109)

        canvas = pytextcanvas.Canvas(10, 1)
        self.assertEqual(len(canvas), 10)

        canvas = pytextcanvas.Canvas(1, 10)
        self.assertEqual(len(canvas), 19)

        canvas = pytextcanvas.Canvas(1, 1)
        self.assertEqual(len(canvas), 1)

        canvas = pytextcanvas.Canvas(10, 2)
        self.assertEqual(len(canvas), 21)

        canvas = pytextcanvas.Canvas(2, 10)
        self.assertEqual(len(canvas), 29)

    def test_str_cache(self):
        pass # TODO
        # TODO - eventually, make it so that the strDirty bit is set only if an actual change is made.
        # TODO - set it so that the cache can be enabled or disabled

    def test_slices_in_key(self):
        pass # TODO - tests _cehckForSlicesInKey()

    def test_del(self):
        canvas = pytextcanvas.Canvas(10, 10)

        # Test that deleting an invalid key raises an exception
        with self.assertRaises(KeyError):
            del canvas['invalid']

        # Test that deleting a nonexistent key doesn't raise an exception
        del canvas[0, 0]
        del canvas[(0, 0):(10, 10)]

        # Test del operator
        canvas[0, 0] = 'x'
        del canvas[0, 0]
        self.assertEqual(canvas[0, 0], None)

        canvas[1, 0] = 'x'
        del canvas[1, 0]
        self.assertEqual(canvas[1, 0], None)

        canvas[0, 1] = 'x'
        del canvas[0, 1]
        self.assertEqual(canvas[0, 1], None)

        # Test setting to None
        canvas[0, 0] = 'x'
        canvas[0, 0] = None
        self.assertEqual(canvas[0, 0], None)

        canvas[1, 0] = 'x'
        canvas[1, 0] = None
        self.assertEqual(canvas[1, 0], None)

        canvas[0, 1] = 'x'
        canvas[0, 1] = None
        self.assertEqual(canvas[0, 1], None)

        # Can't delete cell by setting it to a blank string.
        with self.assertRaises(ValueError):
            canvas[0, 0] = ''

        # Delete multiple cells with a slice:
        canvas[(0, 0):(10, 10)] = 'x'
        del canvas[(0, 0):(10, 10)]
        for x in range(10):
            for y in range(10):
                self.assertEqual(canvas[x, y], None)

        # Delete using negative indexes
        # TODO

        # Delete using negative slices
        # TODO

        # Delete using slices with steps
        # TODO

    def test_loads(self):
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
        self.assertEqual(canvas, patternedCanvas)

        canvas = pytextcanvas.Canvas(loads='123\n456\n789')
        self.assertEqual(canvas, patternedCanvas)

        canvas = pytextcanvas.Canvas(3, 3)
        canvas.loads('123\n456\n789')
        self.assertEqual(canvas, patternedCanvas)

        # Test a too-large loads string
        canvas = pytextcanvas.Canvas(3, 3 , loads='123xxx\n456xx\n789x')
        self.assertEqual(canvas, patternedCanvas)

        canvas = pytextcanvas.Canvas(3, 3 , loads='123\n456\n789\nxxx')
        self.assertEqual(canvas, patternedCanvas)

        canvas = pytextcanvas.Canvas(3, 3 , loads='123xxx\n456xx\n789x\nxxx')
        self.assertEqual(canvas, patternedCanvas)

        # Test a too-small loads string


        # Test a sparse loads string
        patternedCanvas[0, 2] = None
        patternedCanvas[1, 2] = None
        patternedCanvas[2, 2] = None


    def test_rotate(self):
        pass

    def test_scale(self):
        pass

    def test_flip(self):
        pass

    def test_vflip(self):
        pass

    def test_hflip(self):
        pass

    def test_box(self):
        pass

    def test_fill(self):
        blankCanvas = pytextcanvas.Canvas(4, 4)
        canvas = pytextcanvas.Canvas(4, 4)
        self.assertEqual(canvas, blankCanvas)

        canvas[1, 1] = 'x'
        canvas[2, 2] = 'x'
        canvas.clear()
        self.assertEqual(canvas, blankCanvas)

        canvas.fill('x')
        self.assertEqual(str(canvas), 'xxxx\nxxxx\nxxxx\nxxxx')

        canvas.fill(' ')
        self.assertEqual(str(canvas), '    \n    \n    \n    ')

        canvas.fill(None)
        self.assertEqual(str(canvas), '    \n    \n    \n    ')

        # Test argument being casted to a string
        canvas.fill(3)
        self.assertEqual(str(canvas), '3333\n3333\n3333\n3333')

        # Test "char" keyword.
        canvas.fill(char='x')
        self.assertEqual(str(canvas), 'xxxx\nxxxx\nxxxx\nxxxx')

        # Test exceptions
        with self.assertRaises(ValueError):
            canvas.fill('xx')

    def test_floodfill(self):
        pass

    def test_blit(self):
        pass

    def test_square(self):
        pass

    def test_rect(self):
        pass

    def test_diamond(self):
        pass

    def test_hexagon(self):
        pass

    def test_arrow(self):
        pass

    def test_corner(self):
        pass # must be "horizontal" or "vertical"

    def test_line(self):
        pass

    def test_lines(self):
        pass

    def test_polygon(self):
        pass

    def test_ellipse(self):
        pass

    def test_circle(self):
        pass

    def test_arc(self):
        pass

    def test_print(self):
        pass

    def test_forward(self):
        pass

    def test_backward(self):
        pass

    def test_right(self):
        pass

    def test_left(self):
        pass

    def test_goto(self):
        pass

    def test_setx(self):
        pass

    def test_sety(self):
        pass

    def test_towards(self):
        pass

    def test_distance(self):
        pass

    def test_degrees(self):
        pass

    def test_radians(self):
        pass

    def test_penDown(self):
        pass

    def test_penColor(self):
        pass

    def test_fillColor(self):
        pass

    def test_reset(self):
        pass

    def test_clear(self):
        blankCanvas = pytextcanvas.Canvas(4, 4)
        canvas = pytextcanvas.Canvas(4, 4)
        self.assertEqual(canvas, blankCanvas)

        canvas[1, 1] = 'x'
        canvas[2, 2] = 'x'
        canvas.clear()
        self.assertEqual(canvas, blankCanvas)



    def test_showCursor(self):
        pass

    def test_hideCursor(self):
        pass



if __name__ == '__main__':
    unittest.main()
