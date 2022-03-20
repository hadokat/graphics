# PPM Picture I/O
# Skye Rhomberg

import numpy as np

def _read_ppm(fname):
    '''
    Read a ppm file into a numpy array
    '''
    with open(fname, 'rb') as f:
        mn = f.readline().decode().strip() # 'Magic Number' -- expected to be P6
        shape = tuple(int(n) for n in f.readline().split()) + (3,) # (width, height, 3)
        c_max = int(f.readline()) # Max Colors -- usually 255
        r_data = np.frombuffer(f.read(),dtype=np.uint8) # Rest of file is pixels
    try:
        data = r_data.reshape((shape[1], shape[0], 3))
    except ValueError:
        # Some ppm encodings put a newline at the end of the file
        # Take the appropriate number of bytes from the beginning to produce the image
        data = r_data[:np.product(shape)].reshape((shape[1], shape[0], 3))

    return mn, shape[:-1], c_max, data

def _write_ppm(mn, shape, c_max, data, fname):
    '''
    Write an array to the given file location
    '''
    with open(fname, 'wb') as f:
        # Write Header
        f.write(f'{mn}\n{shape[0]} {shape[1]}\n{c_max}\n'.encode())
        # Write array
        f.write(data.tobytes())
        # Trailing newline
        f.write('\n'.encode())

class Picture:
    def __init__(self, src, size=(0,0), anchor=(0,0)):
        '''
        Picture: PPM Image handler
        Input:
        src: str or (int, int int). either filename or rgb triple -- if filename,
            image and metadata are read in from file. if rgb triple, image is created
            from scratch as solid-color of given size
        size: (int, int). width and height of image. only used when creating new
            solid-color image. when loading from file, shape is read from header
        anchor: (int, int). xy-coords of location to place image in canvas -- expressed
            as offsets in px from the top-left corner of the canvas
        '''
        # If filename, read-in
        if isinstance(src, str):
            self.mn, self.shape, self.c_max, self.data = _read_ppm(src)
        # Otherwise, create solid-color image
        else:
            self.mn = 'P6'
            self.shape = size
            self.c_max = 255
            self.data = np.array([[src for c in range(self.shape[0])]\
                    for r in range(self.shape[1])], dtype=np.uint8)

        # Location to place image in canvas (top-left corner)
        self.anchor = anchor

    def save(self, fname):
        '''
        Write Picture to file <fname>
        Input:
        fname: str. filename destination for Picture
        '''
        _write_ppm(self.mn, self.shape, self.c_max, self.data, fname)

    def get_px(self, x, y):
        '''
        Get the color of pixel at location (x,y)
        Input:
        x: int. x-coordinate (col) of target pixel
        y: int. y-coordinate (row) of target pixel
        Output:
        (int, int, int). rgb triple of color at pixel (x,y)
        '''
        return tuple(c for c in self.data[y, x])

    def set_px(self, x, y, color):
        '''
        Set pixel (x,y) to given color
        Input:
        x: int. x-coordinate (col) of target pixel
        y: int. y-coordinate (row) of target pixel
        color: (int, int, int). rgb triple of color
        '''
        self.data[y, x] = color

    def move(self, dx, dy):
        '''
        Move the anchor of the picture by the given offset
        Input:
        dx: int. change in x direction
        dy: int. change in y direction
        '''
        self.anchor[0] += dx
        self.anchor[1] += dy
