from __future__ import division, print_function

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytextcanvas

runningOnPython2 = sys.version_info[0] == 2

if runningOnPython2:
    INPUT_FUNC = raw_input
else:
    INPUT_FUNC = input


class TestBasics(unittest.TestCase):
    def test_ctor(self):
        canvas = pytextcanvas.Canvas()
        self.assertEqual(canvas.width, 80)
        self.assertEqual(canvas.height, 25)
        self.assertEqual(canvas.name, '')
        self.assertEqual(repr(canvas), "<'Canvas' object, width=80, height=25, name=''>")

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

        with self.assertRaises(TypeError):
            pytextcanvas.Canvas(height='invalid')

        with self.assertRaises(ValueError):
            pytextcanvas.Canvas(height=-1)


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
        self.assertEqual(repr(canvas), "<'Canvas' object, width=80, height=25, name=''>")

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
        self.assertEqual(canvas[(0,0):(80, 25)], canvas)
        self.assertEqual(canvas[None:(80, 25)], canvas)
        self.assertEqual(canvas[:(80, 25)], canvas)
        self.assertEqual(canvas[(0, 0):None], canvas)
        self.assertEqual(canvas[(0, 0):], canvas)
        self.assertEqual(canvas[None:None], canvas)
        self.assertEqual(canvas[:], canvas)
        self.assertEqual(canvas[(80, 25):(0,0)], canvas)

        subcanvas = pytextcanvas.Canvas(10, 1)
        canvas[0, 0] = 'A'
        canvas[-1, -1] = 'Z'
        self.assertEqual(canvas[(0,0):(10, 1)], subcanvas)
        self.assertEqual(canvas[(10, 1):(0,0)], subcanvas)

        subcanvas = pytextcanvas.Canvas(10, 2)
        canvas[0, 0] = 'A'
        canvas[1, 1] = 'B'
        canvas[-1, -1] = 'Z'
        self.assertEqual(canvas[(0,0):(10, 2)], subcanvas)
        self.assertEqual(canvas[(10, 2):(0,0)], subcanvas)

        # test steps
        canvas = pytextcanvas.Canvas(width=24, height=24)
        subcanvas = canvas[0,0]

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
        pass

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
        pass

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
        pass

    def test_showCursor(self):
        pass

    def test_hideCursor(self):
        pass



if __name__ == '__main__':
    unittest.main()
