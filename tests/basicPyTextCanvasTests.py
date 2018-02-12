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
        self.assertEqual(canvas.fg, '#daa520')
        self.assertEqual(canvas.bg, '#000000')
        self.assertEqual(repr(canvas), "<'Canvas' object, width=80, height=25, name=''>")

        self.assertEqual(canvas.cursor, (0, 0))
        self.assertEqual(canvas.heading, pytextcanvas.EAST)
        self.assertEqual(canvas.penIsDown, True)

        for canvas in (pytextcanvas.Canvas(width=20, height=10, name='Alice', fg='#ffffff', bg='#eeeeee'),
                       pytextcanvas.Canvas(20, 10, 'Alice', '#ffffff', '#eeeeee')):
            self.assertEqual(canvas.width, 20)
            self.assertEqual(canvas.height, 10)
            self.assertEqual(canvas.name, 'Alice')
            self.assertEqual(canvas.fg, '#ffffff')
            self.assertEqual(canvas.bg, '#eeeeee')
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


    def test_fg_bg(self):
        for attrName in ('fg', 'bg'):
            canvas = pytextcanvas.Canvas()
            canvas.__setattr__(attrName, 'black')
            self.assertEqual(canvas.__getattribute__(attrName), 'black')

            canvas.__setattr__(attrName, '#000000')
            self.assertEqual(canvas.__getattribute__(attrName), '#000000')

            canvas.__setattr__(attrName, '#eee')
            self.assertEqual(canvas.__getattribute__(attrName), '#eeeeee')

            canvas.__setattr__(attrName, 'dddddd')
            self.assertEqual(canvas.__getattribute__(attrName), '#dddddd')

            canvas.__setattr__(attrName, 'bbb')
            self.assertEqual(canvas.__getattribute__(attrName), '#bbbbbb')

            canvas.__setattr__(attrName, '#FFFFFF')
            self.assertEqual(canvas.__getattribute__(attrName), '#ffffff')

            with self.assertRaises(ValueError):
                canvas.__setattr__(attrName, 'invalid')

            with self.assertRaises(ValueError):
                canvas.__setattr__(attrName, '#invalid')

    def test_repr(self):
        canvas = pytextcanvas.Canvas()
        self.assertEqual(repr(canvas), "<'Canvas' object, width=80, height=25, name=''>")

        canvas = pytextcanvas.Canvas(10, 20, 'Alice')
        self.assertEqual(repr(canvas), "<'Canvas' object, width=10, height=20, name='Alice'>")

        canvas.name = None
        self.assertEqual(repr(canvas), "<'Canvas' object, width=10, height=20, name=None>")

        canvas.fg = 'black'
        canvas.bg = 'white'
        self.assertEqual(repr(canvas), "<'Canvas' object, width=10, height=20, name=None>")

    def test_str(self):
        canvas = pytextcanvas.Canvas(width=3, height=4)
        self.assertEqual(str(canvas), '   \n   \n   \n   ')

        canvas = pytextcanvas.Canvas(width=4, height=3)
        self.assertEqual(str(canvas), '    \n    \n    ')

    def test_setitem_getitem_int_tuple_key(self):
        canvas = pytextcanvas.Canvas()

        # Basic write & read
        self.assertEqual(canvas[0], None) # chars start as None
        canvas[0] = 'A'
        self.assertEqual(canvas[0], 'A')
        canvas[1] = 'B'
        self.assertEqual(canvas[1], 'B')


        # negative indexes
        canvas[-1] = 'Z'
        canvas[-2] = 'Y'
        self.assertEqual(canvas[-1], 'Z')
        self.assertEqual(canvas[-2], 'Y')
        self.assertEqual(canvas[1999], 'Z')
        self.assertEqual(canvas[1998], 'Y')

        # tuple keys
        self.assertEqual(canvas[(0, 0)], 'A')
        self.assertEqual(canvas[(1, 0)], 'B')
        self.assertEqual(canvas[(79, 24)], 'Z')
        self.assertEqual(canvas[(78, 24)], 'Y')

    def test_setitem_getitem_keyerror(self):
        canvas = pytextcanvas.Canvas()

        # integer key errors
        with self.assertRaises(KeyError):
            canvas[9999]

        with self.assertRaises(KeyError):
            canvas[0.0]

        with self.assertRaises(KeyError):
            canvas[9999] = 'A'

        with self.assertRaises(KeyError):
            canvas[0.0] = 'A'

        # tuple key errors
        with self.assertRaises(KeyError):
            canvas[(9999, 9999)] = 'X'

        with self.assertRaises(KeyError):
            canvas[(9999, 0)] = 'X'

        with self.assertRaises(KeyError):
            canvas[(0, 9999)] = 'X'

        with self.assertRaises(KeyError):
            canvas[(9999, 9999)]

        with self.assertRaises(KeyError):
            canvas[(9999, 0)]

        with self.assertRaises(KeyError):
            canvas[(0, 9999)]

        with self.assertRaises(KeyError):
            canvas[(0.0, 0.0)]

        with self.assertRaises(KeyError):
            canvas[(0.0, 0)]

        with self.assertRaises(KeyError):
            canvas[(0, 0.0)]

        with self.assertRaises(KeyError):
            canvas[(0.0, 0.0)] = 'A'

        with self.assertRaises(KeyError):
            canvas[(0.0, 0)] = 'A'

        with self.assertRaises(KeyError):
            canvas[(0, 0.0)] = 'A'

    def test_getitem_setitem_slice(self):
        canvas = pytextcanvas.Canvas()
        # TODO

if __name__ == '__main__':
    unittest.main()
