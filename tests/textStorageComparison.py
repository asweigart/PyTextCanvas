"""
This script tests the speed of different ways of storing a 2D field of text.
- list of lists, using [x][y] to access the 2D point
- one long list, using y*width+x to access the 2D point
- dictionary, using [(x, y)] to access the 2D point

These tests show that the list-of-lists approach is faster and uses much less memory.
"""

import cProfile
import random

WIDTH = 80
HEIGHT = 25
TRIALS = 1000000



def listOfListsStorage():
    global storage
    storage = [[None] * HEIGHT for i in range(WIDTH)]
    cProfile.run('testListsOfListsStorage()')


def testListsOfListsStorage():
    random.seed(42)
    for t in range(TRIALS):
        x, y = random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)
        storage[x][y] = 'X'
        x = storage[x][y]


def dictionaryStorage():
    global storage
    storage = {}
    cProfile.run('testDictionaryStorage()')


def testDictionaryStorage():
    random.seed(42)
    for t in range(TRIALS):
        x, y = random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)
        storage[x, y] = 'X'
        x = storage[x, y]


def oneLongList():
    global storage
    storage = [None] * (WIDTH * HEIGHT)
    cProfile.run('testOneLongList()')

def testOneLongList():
    random.seed(42)
    for t in range(TRIALS):
        x, y = random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)
        storage[(y * WIDTH) + x] = 'X'
        x = storage[(y * WIDTH) + y]

print('SPEED TEST')
print('List of lists storage method:')
listOfListsStorage()
print('Dictionary storage method:')
dictionaryStorage()
print('One long list storage method:')
oneLongList()






# =========================================================

from pympler import asizeof
import random


width = 80
height = 25

grid = [[None] * height for i in range(width)]
d = {}


random.seed(42)
for i in range(800):
    x = random.randint(0, width-1)
    y = random.randint(0, height-1)
    grid[x][y] = 'X'
    d[x, y] = 'X'


print('MEMORY TEST')
print('List of list storage method (sparse):')
print(asizeof.asizeof(grid))
print('Dictionary storage method (sparse):')
print(asizeof.asizeof(d))
print()


for x in range(width):
    for y in range(height):
        grid[x][y] = 'X'
        d[x, y] = 'X'

print('List of list storage method (completed):')
print(asizeof.asizeof(grid))
print('Dictionary storage method (completed):')
print(asizeof.asizeof(d))
