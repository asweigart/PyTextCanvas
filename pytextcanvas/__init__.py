# PyTextCanvas by Al Sweigart al@inventwithpython.com

import doctest
import textwrap

def print(*args, default=' '):
    # draw multiple layers of Canvas objects, print to stdout
    pass

def format(*args, default=' '):
    # draw multiple layers of Canvas objects, return as string
    pass


# Based off of the CSS3 standard names. Data from James Bennett's webcolors module: https://github.com/ubernostrum/webcolors
COLOR_NAMES_TO_HEX = {'aliceblue': '#f0f8ff','antiquewhite': '#faebd7','aqua': '#00ffff','aquamarine': '#7fffd4','azure': '#f0ffff','beige': '#f5f5dc','bisque': '#ffe4c4','black': '#000000','blanchedalmond': '#ffebcd','blue': '#0000ff','blueviolet': '#8a2be2','brown': '#a52a2a','burlywood': '#deb887','cadetblue': '#5f9ea0','chartreuse': '#7fff00','chocolate': '#d2691e','coral': '#ff7f50','cornflowerblue': '#6495ed','cornsilk': '#fff8dc','crimson': '#dc143c','cyan': '#00ffff','darkblue': '#00008b','darkcyan': '#008b8b','darkgoldenrod': '#b8860b','darkgray': '#a9a9a9','darkgrey': '#a9a9a9','darkgreen': '#006400','darkkhaki': '#bdb76b','darkmagenta': '#8b008b','darkolivegreen': '#556b2f','darkorange': '#ff8c00','darkorchid': '#9932cc','darkred': '#8b0000','darksalmon': '#e9967a','darkseagreen': '#8fbc8f','darkslateblue': '#483d8b','darkslategray': '#2f4f4f','darkslategrey': '#2f4f4f','darkturquoise': '#00ced1','darkviolet': '#9400d3','deeppink': '#ff1493','deepskyblue': '#00bfff','dimgray': '#696969','dimgrey': '#696969','dodgerblue': '#1e90ff','firebrick': '#b22222','floralwhite': '#fffaf0','forestgreen': '#228b22','fuchsia': '#ff00ff','gainsboro': '#dcdcdc','ghostwhite': '#f8f8ff','gold': '#ffd700','goldenrod': '#daa520','gray': '#808080','grey': '#808080','green': '#008000','greenyellow': '#adff2f','honeydew': '#f0fff0','hotpink': '#ff69b4','indianred': '#cd5c5c','indigo': '#4b0082','ivory': '#fffff0','khaki': '#f0e68c','lavender': '#e6e6fa','lavenderblush': '#fff0f5','lawngreen': '#7cfc00','lemonchiffon': '#fffacd','lightblue': '#add8e6','lightcoral': '#f08080','lightcyan': '#e0ffff','lightgoldenrodyellow': '#fafad2','lightgray': '#d3d3d3','lightgrey': '#d3d3d3','lightgreen': '#90ee90','lightpink': '#ffb6c1','lightsalmon': '#ffa07a','lightseagreen': '#20b2aa','lightskyblue': '#87cefa','lightslategray': '#778899','lightslategrey': '#778899','lightsteelblue': '#b0c4de','lightyellow': '#ffffe0','lime': '#00ff00','limegreen': '#32cd32','linen': '#faf0e6','magenta': '#ff00ff','maroon': '#800000','mediumaquamarine': '#66cdaa','mediumblue': '#0000cd','mediumorchid': '#ba55d3','mediumpurple': '#9370db','mediumseagreen': '#3cb371','mediumslateblue': '#7b68ee','mediumspringgreen': '#00fa9a','mediumturquoise': '#48d1cc','mediumvioletred': '#c71585','midnightblue': '#191970','mintcream': '#f5fffa','mistyrose': '#ffe4e1','moccasin': '#ffe4b5','navajowhite': '#ffdead','navy': '#000080','oldlace': '#fdf5e6','olive': '#808000','olivedrab': '#6b8e23','orange': '#ffa500','orangered': '#ff4500','orchid': '#da70d6','palegoldenrod': '#eee8aa','palegreen': '#98fb98','paleturquoise': '#afeeee','palevioletred': '#db7093','papayawhip': '#ffefd5','peachpuff': '#ffdab9','per': '#cd853f','pink': '#ffc0cb','plum': '#dda0dd','powderblue': '#b0e0e6','purple': '#800080','red': '#ff0000','rosybrown': '#bc8f8f','royalblue': '#4169e1','saddlebrown': '#8b4513','salmon': '#fa8072','sandybrown': '#f4a460','seagreen': '#2e8b57','seashell': '#fff5ee','sienna': '#a0522d','silver': '#c0c0c0','skyblue': '#87ceeb','slateblue': '#6a5acd','slategray': '#708090','slategrey': '#708090','snow': '#fffafa','springgreen': '#00ff7f','steelblue': '#4682b4','tan': '#d2b48c','teal': '#008080','thistle': '#d8bfd8','tomato': '#ff6347','turquoise': '#40e0d0','violet': '#ee82ee','wheat': '#f5deb3','white': '#ffffff','whitesmoke': '#f5f5f5','yellow': '#ffff00','yellowgreen': '#9acd32',}

def hex_color(color):
    """
    Converts the `color` parameter to a standard '#ffffff' color string of a # followed by six hexadecimal digits. The `color` parameter can formatted as a CSS3 name, #ffffff, ffffff, #fff, or fff.

    TODO: Expand to include rgb triplet integers, and three percentages?

    >>> hex_color('white')
    '#ffffff'
    >>> hex_color('#ffffff')
    '#ffffff'
    >>> hex_color('#fff')
    '#ffffff'
    >>> hex_color('ffffff')
    '#ffffff'
    >>> hex_color('fff')
    '#ffffff'
    >>> hex_color('#abc')
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


# from http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm#Python
def get_line_points(x1, y1, x2, y2):
    """Returns a list of (x, y) tuples of every point on a line between
    (x1, y1) and (x2, y2). The x and y values inside the tuple are integers.

    Line generated with the Bresenham algorithm.

    Args:
      x1 (int, float): The x coordinate of the line's start point.
      y1 (int, float): The y coordinate of the line's start point.
      x2 (int, float): The x coordinate of the line's end point.
      y2 (int, float): The y coordiante of the line's end point.

    Returns:
      [(x1, y1), (x2, y2), (x3, y3), ...]

    Example:
    >>> get_line_points(0, 0, 6, 6)
    [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]
    >>> get_line_points(0, 0, 3, 6)
    [(0, 0), (0, 1), (1, 2), (1, 3), (2, 4), (2, 5), (3, 6)]
    >>> get_line_points(3, 3, -3, -3)
    [(3, 3), (2, 2), (1, 1), (0, 0), (-1, -1), (-2, -2), (-3, -3)]
    """
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    points = []
    issteep = abs(y2-y1) > abs(x2-x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2-y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points


def is_inside(point_x, point_y, area_left, area_top, area_width, area_height):
    '''
    Returns True if the point of point_x, point_y is inside the area described.

    >>> is_inside(0, 0, 0, 0, 1, 1)
    True
    >>> is_inside(1, 0, 0, 0, 1, 1)
    False
    >>> is_inside(0, 1, 0, 0, 1, 1)
    False
    >>> is_inside(1, 1, 0, 0, 1, 1)
    False
    >>> is_inside(5, 5, 4, 4, 4, 4)
    True
    >>> is_inside(8, 8, 4, 4, 4, 4)
    False
    >>> is_inside(10, 10, 4, 4, 4, 4)
    False
    '''
    return (area_left <= point_x < area_left + area_width) and (area_top <= point_y < area_top + area_height)


class Canvas:
    def __init__(self):
        pass

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def __len__(self):
        pass

    def __add__(self):
        pass

    def __iadd__(self):
        pass

    def __radd__(self):
        pass

    def translate(self):
        pass

    def setview(self):
        pass # like __str__() but for a subsection

        # TODO - by default, canvases have infinite dimensions.
        # Their "view" is what determines what gets printed. This acts as a
        # basic camera system.

    def htmlstr(self):
        pass

    def copy(self):
        pass

    def fill(self):
        pass

    def floodfill(self):
        pass

    def blit(self, dstCanvas):
        pass

    def square(self):
        pass

    def rect(self, *args):
        pass

    def line(self):
        pass

    def lines(self):
        pass

    def polygon(self):
        pass

    def ellipse(self):
        pass

    def circle(self):
        pass

    def arc(self):
        pass

# TODO - should I use camelcase? I want to match the original Turtle module, but it uses, well, just lowercase.

class Cursor:
    def __init__(self):
        # passed in one or more canvases to draw on, and optionall a starting coord on each.
        pass

    def print(self):
        pass

    # Methods dervied from turtle module:

    def forward(self):
        pass

    fd = forward

    def backward(self):
        pass

    bk = back = backward

    def right(self):
        pass

    rt = right

    def left(self):
        pass

    lt = left

    def goto(self):
        pass

    setpost = setposition = goto

    def setx(self):
        pass

    def sety(self):
        pass

    def setheading(self):
        pass

    seth = setheading

    def home(self):
        pass

    def circle(self):
        pass

    def dot(self):
        pass

    def stamp(self):
        pass

    def clearstamp(self):
        pass

    def clearstamps(self):
        pass

    def undo(self):
        pass

    def speed(self):
        pass

    def position(self):
        pass

    pos = position

    def towards(self):
        pass

    def xcor(self):
        pass

    def ycor(self):
        pass

    def heading(self):
        pass

    def distance(self):
        pass

    def degrees(self):
        pass

    def radians(self):
        pass

    def pendown(self):
        pass

    pd = down = pendown

    def penup(self):
        pass

    pu = up = penup

    def pensize(self):
        pass

    width = pensize

    def pen(self):
        pass

    def isdown(self):
        pass

    def color(self):
        pass

    def pencolor(self):
        pass

    def fillcolor(self):
        pass

    def filling(self):
        pass

    def begin_fill(self):
        pass

    def end_fill(self):
        pass

    def reset(self):
        pass

    def clear(self):
        pass

    def write(self):
        pass

    def showturtle(self):
        pass

    st = showturtle

    def hideturtle(self):
        pass

    ht = hideturtle

    def isvisible(self):
        pass
