# Simple Python Graphics Primitives
# Interfaces with PIL Images
# Skye Rhomberg

def _prop(name):
    '''
    Generate Given Property Name
    Input:
    name: str. property name
    Output:
    property object. This encapsulates the getter and setter method for the 
        private variable _name, so that it can be accessed and modified with
        <Class>.name or <Class>.name = value
    '''
    @property
    def prop(self):
        return getattr(self, f'_{name}')

    @prop.setter
    def prop(self, v):
        setattr(self, f'_{name}', v)

    return prop

class Shape:
    def __init__(self, properties, draw_str):
        '''
        Shape Base Class
        Input:
        properties: dict {property:value}. Property names should be strings, values can
            be anything. For each property, Shape will generate the getter and setter
            functions so that Shape.property will return the value and 
            Shape.property = value will update it
        draw: list of str. first element is the name of the PIL ImageDraw method to call
            to draw this object. The rest of the elements are the names of instance
            variables to pass as arguments to the ImageDraw method
        '''
        for p in properties:
            setattr(self, f'_{p}', properties[p])
            setattr(Shape, p, _prop(p))

        self.draw = lambda: [draw_str[0]] + [getattr(self,p) for p in draw_str[1:]]

class PolyLine(Shape):
    def __init__(self, xy, color=None, width=0, joint=None):
        '''
        Polyline: lines connecting a series of points
        Input:
        xy: list of (int, int) tuples. (x,y) coordinates for each point
        color: tuple (int, int, int). rgb triple for line color
        width: int. line width
        joint: str. 'curve' for curved connectors, None for straight corners
        '''
        Shape.__init__(self, {'xy': xy, 'color': color, 'width': width, 'joint': joint},\
                ['line','xy','color','width','joint'])

class Line(PolyLine):
    def __init__(self, xy0, xy1, color=None, width=0):
        '''
        Line: single line between two points
        Input:
        xy0: tuple (int, int). coordinates of first point
        xy1: tuple (int, int). coordinates of second point
        color: tuple (int, int, int). rgb triple for line color
        width: int. line width
        '''
        PolyLine.__init__(self, [xy0, xy1], color, width, None)

    # Make xy0 and xy1 accessible as instance variables
    # self.xy0 and self.xy1 can be used as aliases for self.xy[0], self.xy[1]
    @property
    def xy0(self):
        return self._xy[0]

    @xy0.setter
    def xy0(self, v):
        self._xy[0] = v

    @property
    def xy1(self):
        return self._xy[1]

    @xy1.setter
    def xy1(self, v):
        self._xy[1] = v

class _PieSlice(Shape):
    def __init__(self, xy, start, end, fill=None, outline=None, width=1):
        '''
        Pie Slice: Internal Use Class
        Draws a portion of the ellipse in the bounding box given by xy
        Input:
        xy: [(x0, y0), (x1, y1)]. coordinates of upper-left and lower-right corners
            of the bounding box containing the pie slice
        start: int. starting angle in degrees (0 is 3 o'clock)
        end: int. ending angle in degrees (360 is again 3 o'clock)
        fill: tuple (int, int, int). rgb triple for fill color
        outline: tuple (int, int, int). rgb triple for line color
        width: int. line width
        '''
        Shape.__init__(self, {'xy': xy, 'start': start, 'end': end, 'fill': fill,\
                'outline': outline, 'width': width},\
                ['pieslice', 'xy', 'start', 'end', 'fill', 'outline', 'width'])

class Ellipse(_PieSlice):
    def __init__(self, c, r, start=0, end=360, fill=None, outline=None, width=1):
        '''
        Ellipse (Easy-to-use version)
        Draws a portion of the ellipse given by center c and radius tuple r
        Input:
        c: (int, int). xy-coords of ellipse center
        r: (int, int). x-radius and y-radius of ellipse
        start: int. starting angle in degrees (0 is 3 o'clock)
        end: int. ending angle in degrees (360 is again 3 o'clock)
        fill: tuple (int, int, int). rgb triple for fill color
        outline: tuple (int, int, int). rgb triple for line color
        width: int. line width
        '''
        _PieSlice.__init__(self, [(c[0]-r[0],c[1]-r[1]),(c[0]+r[0],c[1]+r[1])],\
                start, end, fill, outline, width)
        self._c = c
        self._r = r

    def _update(self):
        '''
        Update internal bounding-box coordinates based on self.c and self.r
        '''
        self.xy = [(self.c[0]-self.r[0], self.c[1]-self.r[1]),\
                (self.c[0]+self.r[0], self.c[1]+self.r[1])]

    # Make self.c and self.r usable instance variables
    # Continue to update the internal coordinates
    @property
    def c(self):
        return self._c

    @c.setter
    def c(self, v):
        self._c = v
        self._update()
    
    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, v):
        self._r = r
        self._update()

class Polygon(Shape):
    def __init__(self, xy, fill=None, outline=None):
        '''
        Polygon: arbitrary filled closed shapes
        xy: list of (int, int) xy-coords of each point. Lines will be drawn between
            each consecutive point, as well as the first and last point to close the shape
        fill: tuple (int, int, int). rgb triple for fill color
        outline: tuple (int, int, int). rgb triple for line color
        '''
        Shape.__init__(self, {'xy': xy, 'fill': fill, 'outline': outline},\
                ['polygon','xy','fill','outline'])
