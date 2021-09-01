PyTextCanvas
============

PyTextCanvas is a module for writing text and ascii art to a 2D string "canvas" in Python.

PyTextCanvas has a Canvas class, which is a data structure for a "2D string", where characters can be "drawn" to the canvas using x, y coordinates. The canvas can be exported as a basic Python string or HTML.

Runs on Windows, macOS, and Linux.

This module could be used in curses-like or urwid-like modules.


Installation
------------


    ``pip install pytextcanvas``


Example Usage
-------------

    >>> import pytextcanvas as pytc
    >>> canvas = pytc.Canvas(20, 4)
    >>> canvas.fill('.')
    >>> print(canvas)
    ....................
    ....................
    ....................
    ....................
    >>> canvas.write('Hello, world!')
    >>> print(canvas)
    Hello, world!.......
    ....................
    ....................
    ....................
    >>> canvas.cursor = (10, 2)
    >>> canvas.write('Howdy!!!')
    >>> print(canvas)
    Hello, world!.......
    ....................
    ..........Howdy!!!..
    ....................
    >>> str(canvas)
    'Hello, world!.......\n....................\n..........Howdy!!!..\n....................'
    >>> canvas.rectangle('*', 0, 0, 20, 4)
    >>> print(canvas)
    ********************
    *..................*
    *.........Howdy!!!.*
    ********************

Support
-------

If you find this project helpful and would like to support its development, [consider donating to its creator on Patreon](https://www.patreon.com/AlSweigart).
