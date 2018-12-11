# This test checks what FPS we can get using PyTextCanvas. Drawing to consoles is usually slow.
# On my Windows 10 machine, I was getting about 10 fps (with really bad flickering). Obviously
# drawing areas smaller than 80 x 25 will result in faster drawing.

import sys
import time
import pytextcanvas as pytc

FRAMES_TO_TEST = 100

canvas = pytc.Canvas(80, 25)

pytc.clearScreen()

startTime = time.time()
for i in range(FRAMES_TO_TEST // 2):
    canvas.fg = pytc.RED
    canvas.bg = pytc.BLUE
    canvas.fill('*')
    canvas.print()
    pytc.clearScreen()

    canvas.fg = pytc.BLUE
    canvas.bg = pytc.RED
    canvas.fill('+')
    canvas.print()
    pytc.clearScreen()

runtime = time.time() - startTime
print(sys.platform, sys.version)
print('%s frames in %s seconds, %s fps' % (FRAMES_TO_TEST, runtime, round(FRAMES_TO_TEST / runtime, 2)))
