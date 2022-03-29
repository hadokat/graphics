# Image I/O
# Skye Rhomberg

from tkinter import Tk, Label, Button
from PIL import Image, ImageTk, ImageSequence, ImageDraw
import ppmIO as ppm

########################################################################################
# Top-Level I/O

def view(fname):
    '''
    View image from file -- supports both still and GIF
    Input:
    fname: str. filename of image to view
    '''
    # Open image to PIL, then show it in Tk window
    _show_img(_open_img(fname))

def draw(shapes, canvas, bg_color=(255, 255, 255)):
    '''
    Draw and open image from given list of shapes
    Input:
    shapes: list of graphics objects or ppm pictures
    canvas: (int, int). width, height of canvas
    bg_color: tuple (int, int, int). background color as RGB triple
    '''
    _show_img(_draw_img(canvas[0], canvas[1], shapes, bg_color))

def draw_seq(shape_frames, canvas, duration=100, bg_color=(255, 255, 255)):
    '''
    Draw and open GIF from given LIST OF LISTS of shapes
    Input:
    shape_frames: LIST OF LISTS of graphics objects or ppm pictures
    canvas: (int, int). width, height of canvas
    duration: int. delay between GIF frames
    bg_color: tuple (int, int, int). background color as RGB triple
    '''
    _show_img([_draw_img(canvas[0], canvas[1], s, bg_color)\
            for s in shape_frames], duration)

def save(fname, shapes, canvas, bg_color=(255, 255, 255)):
    '''
    Save shapes to given filename
    Input:
    fname: str. filename to save image
    shapes: list of graphics objects or ppm pictures
    canvas: (int, int). width, height of canvas
    bg_color: tuple (int, int, int). background color as RGB triple
    '''
    _save_img(_draw_img(canvas[0], canvas[1], shapes, bg_color), fname)

def save_seq(fname, shape_frames, canvas, duration, bg_color=(255, 255, 255)):
    '''
    Save SEQUENCE of shapes to given filename
    Input:
    fname: str. filename to save image
    shape_frames: LIST OF LISTS of graphics objects or ppm pictures
    canvas: (int, int). width, height of canvas
    duration: int. delay between GIF frames
    bg_color: tuple (int, int, int). background color as RGB triple
    '''
    _save_img([_draw_img(canvas[0], canvas[1], s, bg_color) for s in shape_frames],\
            fname, duration)

########################################################################################
# Internal Image I/O Functions

def _open_img(fname):
    '''
    Open the given filename and return a PIL object to handle it
    Input:
    fname: str. filename of image to open
    Output:
    PIL Image or list of PIL Image. image or frames of GIF
    '''
    # Get the file extension by taking the characters after the last '.' in fname
    ext = lambda s: s.split('.')[-1]

    # Open the image
    with Image.open(fname) as im:
        # If it's a gif, return a list of its frames as PIL Images
        if ext(fname) == 'gif':
            return [frame.copy() for frame in ImageSequence.Iterator(im)]

        # Otherwise, return the image as a PIL Image
        return im.copy()

def _show_img(frames, duration = None):
    '''
    Display an image or GIF with a stop button if applicable
    Input:
    frames: list of PIL Image. for a still image, use a list of a single frame
    duration: int. time in ms between frames of GIF
    '''
    # Create a new Tkinter object
    _root = Tk()
    # Create and pack the player with the frames
    p = Player(_root, frames, duration)
    p.pack()
    # If this is a GIF, add a stop button
    if isinstance(frames, list) and len(frames) > 1:
        Button(_root, text='stop', command=lambda: p.after_cancel(p.cancel)).pack()
    _root.mainloop()

def _save_img(frames, fname, duration=100):
    '''
    Save the given image or frames to PPM or GIF
    Input:
    frames: PIL Image or list of PIL Image. image or frames to save
    fname: str. filename to save image as. MUST INCLUDE EXTENSION
    duration: int. time in ms between frames of GIF
    '''
    # If this is a GIF, safe it as such
    if isinstance(frames, list):
        frames[0].save(fname, save_all=True, append_images=frames[1:],\
                optimize=False, duration=duration, loop=0)
    # Otherwise, just save it as an image
    else:
        frames.save(fname)

def _draw_img(width, height, shapes, bg_color=(255, 255, 255)):
    '''
    Create a PIL Image from given list of graphics objects
    Input:
    width: int. canvas width
    height: int. canvas height
    shapes: list of graphics objects or ppm pictures
    bg_color: tuple (int, int, int). background color as RGB triple
    Output:
    PIL Image. composite image of bg_color and shapes, with first element drawn first
    '''
    # Create background canvase
    im = Image.new('RGB', (width, height), bg_color)
    # PIL graphics primitive drawing handler
    d = ImageDraw.Draw(im)
    for s in shapes:
        # If shape is a ppm Picture, paste it according to its anchor
        if isinstance(s, ppm.Picture):
            im.paste(Image.fromarray(s.data), s.anchor)
        # Otherwise, its a Shape from shapes.py
        # Use its draw() arg-list to call correct ImageDraw method
        else:
            getattr(d, s.draw()[0])(*s.draw()[1:])
    return im

########################################################################################
# GIF Player / Image Viewer Class

class Player(Label):
    def __init__(self, master, frames, duration = None):
        '''
        Player Constructor
        Input:
        master: tk object. parent of this instance
        frames: single PIL Image or non-empty list of PIL Images
        duration: int. time in ms between frames of GIF
        '''
        # If frames is just one image, turn it into a list 
        if not isinstance(frames, list):
            frames = [frames]

        # Initialize Frames List
        self.frames = [ImageTk.PhotoImage(f) for f in frames]

        # Initialize with the first frame showing
        Label.__init__(self, master, image=self.frames[0])

        # If duration is provided (e.g. in a gif) use it
        # Default to 100ms
        try:
            self.delay = frames[0].info['duration']
        except KeyError:
            self.delay = 100

        if duration:
            self.delay = duration

        # Loop idx
        self.idx = 0
        # If this is a GIF, begin playing after <delay> ms
        if len(self.frames) > 1:
            self.cancel = self.after(self.delay, self.play)

    def play(self):
        '''
        Animate a GIF
        Update the image to the current frame and update the frame idx
        '''
        # Update label image to current frame
        self.config(image=self.frames[self.idx])
        # Iterate the frame, come back around to zero if at end of sequence
        self.idx = (self.idx + 1) % len(self.frames)
        # After <delay> ms, recurse
        self.cancel = self.after(self.delay, self.play)

########################################################################################
# Game Player Class

class Game(Label):
    def __init__(self, master, width, height,\
            shapes = [], bg_color = (255, 255, 255), frame_delay = 20):
        '''
        Game Constructor
        Input:
        master: tk object. parent of this instance
        width, height: int. width and height of game window in px
        shapes: list of graphics objects or ppmIO pictures. contents of current frame
        bg_color: tuple (int, int int). RGB background color of frame
        frame_delay: int. time in ms between frames of game
        '''
        # Set width, height, bg_color, frame_delay
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.frame_delay = frame_delay

        # Draw initial frame from shapes given
        self.update(shapes)

        # Call parent constructor -- self.img generated by update()
        Label.__init__(self, master, image = self.img)

        # Begin Animation
        self.cancel = self.after(self.frame_delay, self.play)

    def play(self):
        '''
        Animate the game
        Put the game's image into the Label for drawing
        '''
        # Update the label to the latest image
        self.config(image = self.img)
        # Recurse after <frame_delay> ms
        self.cancel = self.after(self.frame_delay, self.play)

    def update(self, shapes):
        '''
        Update img from given shapes
        Input:
        shapes: list of graphics objects or ppmIO pictures. contents of current frame
        '''
        # Use _img_draw to make PIL Image
        im = _draw_img(self.width, self.height, shapes, self.bg_color)
        # Convert to Tk PhotoImage and update
        self.img = ImageTk.PhotoImage(im)

########################################################################################
# Examples

def example_game():
    '''
    Create a game
    This game can only update on user input
    '''
    # The root Tk object is a container for everything else
    _root = Tk()

    # The Game object itself is created inside it, with width and height 500
    g = Game(_root, 500, 500)

    # Key and Mouse Events can be bound like this: the functions should always
    # a single input 'event' -- the handler for the Tk event
    # The actual handler functions should always finish by calling the game's
    # update() method with some shapes to create a change on-screen
    g.bind('<Button-1>', lambda event: print(f'Clicked {event.x}, {event.y}'))
    g.bind('<Key>', lambda event: print(f'pressed {repr(event.char)}'))

    # Pack the elements to properly create them inside root
    g.pack()

    # Claim focus for game window so keyboard events work
    g.focus_set()

    # Run the widget
    _root.mainloop()
