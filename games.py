import pygame, pygame.image, pygame.mixer, pygame.font, pygame.transform 
import pygame.draw 
from pygame.locals import * 

pygame.init() 
 

 
class GamesError(Exception): pass


class Mouse(object):

    def get_position(self):
        return pygame.mouse.get_pos()
    
    def set_position(self, new_position):
        pygame.mouse.set_pos(new_position)
    
    position = property(get_position, set_position)


    def get_x(self):
        return pygame.mouse.get_pos()[0]
    
    def set_x(self, new_x):
        current_y = pygame.mouse.get_pos()[1]
        pygame.mouse.set_pos( (new_x, current_y) )
        
    x = property(get_x, set_x)


    def get_y(self):
        return pygame.mouse.get_pos()[1]
    
    def set_y(self, new_y):
        current_mouse_x = pygame.mouse.get_pos()[0]
        pygame.mouse.set_pos( (current_x, new_y) )

    y = property(get_y, set_y)

    def set_is_visible(self, new_visibility):
        pygame.mouse.set_visible(new_visibility)
    is_visible = property(fset = set_is_visible)

    def is_pressed(self, button_number):
        return pygame.mouse.get_pressed()[button_number] == 1


class Keyboard(object):
    def is_pressed(self, key):
        return pygame.key.get_pressed()[key] == 1


class Music(object):
    def load(self, filename):
        pygame.mixer.music.load(filename)

    def play(self, loop=0):
        pygame.mixer.music.play(loop)

    def fadeout(self, millisec):
        pygame.mixer.music.fadeout(millisec)

    def stop(self):
        pygame.mixer.music.stop()

class Screen(object): 
 
    initialized = 0 
 
    def __init__ (self, width = 640, height = 480, fps = 50): 
        # Bomb if you try this more than once
        if Screen.initialized: 
            raise GamesError("Cannot have more than on Screen object")
         
        Screen.initialized = 1

        # Create the pygame display
        #self._display = pygame.display.set_mode ((width, height), HWSURFACE)
        self._display = pygame.display.set_mode ((width, height))
        self._width = width  
        self._height = height
        self._background = self._display.convert()
 
        # Initialize a list of objects in play 
        self._objects = [] 
        # Initialize list dirty rectangles to be repainted 
        self._dirtyrects = [] 
 
        # Time when we should draw the next frame 
        self._next_tick = 0

        # Frames per second screen will be updated
        self._fps = fps
 

    def get_width(self):
        return self._width
    
    width = property(get_width)

    def get_height(self):
        return self._height
    
    height = property(get_height)

 
    def get_fps(self):
        return self._fps
    
    fps = property(get_fps)


    def get_background(self):
        return self._background
    
    def set_background(self, new_background): 
        """ 
        Set the background to the surface provided. Note that the  
        surface should not have transparency set, or weird things 
        will happen. 
        """
        self._background = pygame.Surface((self._width, self._height)) 
        for x in range(0, self._width, new_background.get_width()): 
            for y in range(0, self._height, new_background.get_height()): 
                self._background.blit(new_background, (x, y)) 
                 
        self._display.blit(self._background, (0,0)) 
        pygame.display.update()

    background = property(get_background, set_background)

    def get_all_objects(self): 
        """ 
        Returns a list of all the Sprites on the Screen. 
        """ 
        return self._objects[:]
    all_objects = property(get_all_objects)

    def get_event_grab(self):
        return pygame.event.get_grab()
    
    def set_event_grab(self, new_status):
        pygame.event.set_grab(new_status)
        
    event_grab = property(get_event_grab, set_event_grab)
        
    def tick(self): 
        pass

    def keypress(self, key):
        pass

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                self.quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.quit()
                else:
                    self.keypress(event.key)
 
    def quit(self): 
        self._exit = 1 
 
    def clear(self):
        for object in self._objects[:]:
            object.destroy()
        self._objects = []
 
    def _update_display(self):
        pygame.display.update(self._dirtyrects)
        self._dirtyrects = []

    def mainloop(self): 
        self._exit = 0 
 
        while not self._exit: 
            self._wait_frame()

            for object in self._objects: 
                object._erase()

            for object in self._objects[:]: 
                if object._tickable:
                    object._tick() 
 
            self.tick() 
 
            for object in self._objects: 
                object._draw()

            self._update_display()
            pygame.display.flip()

            self.handle_events() 
 
        pygame.event.get()
 
    def _wait_frame (self): 
        this_tick = pygame.time.get_ticks() 
        if this_tick < self._next_tick: 
            pygame.time.delay(int(self._next_tick+0.5) - this_tick) 
        self._next_tick = this_tick + (1000./self._fps) 

    def overlapping_objects(self, rectangle): 
        rect = pygame.Rect (rectangle)

        rect_list = []
        for obj in self._objects:
            rect_list.append (obj._rect)

        indices = rect.collidelistall (rect_list)

        over_objects = [] 
        for index in indices:
            if (self._objects[index]).is_collideable:
                over_objects.append (self._objects [index]) 

        return over_objects

    def _elevate(self, it, above=None):
        objects = self._objects[:]
        objects.remove(it)
        if above == None:
            objects.append(it)
        else:
            idx = 1 + objects.index(above)
            objects[idx:idx] = [it]
        self._objects = objects

    def _lower(self, object, below = None):
        objects = self._objects[:]
        objects.remove(it)
        if below == None:
            self._objects = [it] + objects
        else:
            idx = objects.index(below)
            objects[idx:idx] = [it]
            self._objects = objects

    def add(self, sprite):
        self._objects.append(sprite)
      
    def remove(self, sprite):
        try:
            self._objects.remove(sprite)
        except ValueError:
            pass

    def blit_and_dirty (self, source_surf, dest_pos):
        rect = self._display.blit(source_surf, dest_pos) 
        self._dirtyrects.append(rect)


    def blit_background(self, rect):
        rect = self._display.blit(self._background, rect, rect)
        self._dirtyrects.append(rect)
         

class Sprite(object): 
    def __init__(self, image, angle = 0,
                 x = 0, y = 0,
                 top = None, bottom = None, left = None, right = None,
                 dx = 0, dy = 0,
                 interval = 1, is_collideable = True):
        
        if not Screen.initialized: 
            raise GamesError("Screen object must be intialized before any Sprite object") 
 
        self._surface = image 
        self._orig_surface = image
        self._rect = self._surface.get_rect() 

        self.position = (x, y)

        if top != None:
            self.top = top
        if bottom != None:
            self.bottom = bottom
        if left != None:
            self.left = left
        if right != None:
            self.right = right

        self.velocity = (dx, dy) 

        self._angle = angle % 360
        if self._angle != 0:
            self._rotate() 

        self.is_collideable = is_collideable

        self._interval = interval 
        self._tickable = 1 
        self._next = 0

        self._gone = 0

    def __del__(self):
        if screen and not self._gone:
            self.destroy()

    def _draw(self): 
        screen.blit_and_dirty(self._surface, self._rect)

    def _erase(self): 
        screen.blit_background(self._rect)
 
    def _replace(self, new_surface): 
        x, y = self.position 
        self._surface = new_surface 
        self._rect = self._surface.get_rect() 
        self.position = (x, y)

    def _rotate(self): 
        self._replace(pygame.transform.rotate(self._orig_surface, -self._angle))

    def _tick(self):
        self._next = self._next + 1 
        if self._next >= self._interval: 
            self._next = 0  
            self.tick()
        if self._dx or self._dy:
            self.position = ( (self._x + self._dx), (self._y + self._dy) )
        self.update()

    def start (self): 
        self._tickable = 1 
        self._next = 0 

    def stop (self): 
        self._tickable = 0 

    def update(self):
        pass

    def tick(self):
        pass
 
    def overlaps(self, other):
        if not self.is_collideable or not other.is_collideable:
            return False
        else:
            return self._rect.colliderect(other._rect) 
     
    def elevate(self, above = None):
        screen._elevate(self, above)
     
    def lower(self, below = None):
        screen._lower(self, below)

    def destroy(self): 
        self._erase()
        screen.remove(self) 
        self._gone = 1

    def get_x(self):
        return self._x
    def set_x(self, new_x):
        self._x = new_x
        self._rect.centerx = int(self._x)
    x = property(get_x, set_x)

    def get_y(self):
        return self._y
    def set_y(self, new_y):
        self._y = new_y
        self._rect.centery = int(self._y)
    y = property(get_y, set_y)

    def get_position(self):
        return ( (self.x, self.y) )
    def set_position(self, new_position):
        self.x, self.y = new_position
    position = property(get_position, set_position)

    def get_dx(self):
        return self._dx
    def set_dx(self, new_dx):
        self._dx = new_dx
    dx = property(get_dx, set_dx)

    def get_dy(self):
        return self._dy
    def set_dy(self, new_dy):
        self._dy = new_dy
    dy = property(get_dy, set_dy)

    def get_velocity(self):
        return ( (self.dx, self.dy) )
    def set_velocity (self, new_velocity): 
        self.dx, self.dy = new_velocity
    velocity = property(get_velocity, set_velocity)

    def get_left(self):
        return self._rect.left
    def set_left(self, new_left):
        self._rect.left = new_left
        self._x = self._rect.centerx
    left = property(get_left, set_left)

    def get_right(self):
        return self._rect.right
    def set_right(self, new_right):
        self._rect.right = new_right
        self._x = self._rect.centerx
    right = property(get_right, set_right)

    def get_top(self):
        return self._rect.top
    def set_top(self, new_top):
        self._rect.top = new_top
        self._y = self._rect.centery
    top = property(get_top, set_top)

    def get_bottom(self):
        return self._rect.bottom
    def set_bottom(self, new_bottom):
        self._rect.bottom = new_bottom
        self._y = self._rect.centery
    bottom = property(get_bottom, set_bottom)

    def get_angle(self):
        return self._angle
    def set_angle(self, new_angle):
        self._angle = new_angle % 360 
        self._rotate() 
    angle = property(get_angle, set_angle)

    def get_image(self):
        return self._orig_surface
    def set_image(self, new_image): 
        self._orig_surface = new_image 
        if self._angle != 0: 
            self._rotate() 
        else: 
            self._replace(new_image) 
    image = property(get_image, set_image)

    def get_height(self):
        return self._surface.get_height()
    height = property(get_height)

    def get_width(self):
        return self._surface.get_width()
    width = property(get_width)

    def get_is_collideable(self):
        return self._is_collideable
    def set_is_collideable(self, new_status):
        self._is_collideable = new_status
    is_collideable = property(get_is_collideable, set_is_collideable)


    def get_overlapping_sprites(self): 
        overlapping = screen.overlapping_objects(self._rect)
        if self in overlapping:
            overlapping.remove(self)
        return overlapping
    overlapping_sprites = property(get_overlapping_sprites)

    def get_interval(self):
        return self._interval
    def set_interval(self, new_interval):
        self._interval = new_interval
    interval = property(get_interval, set_interval)


class Text(Sprite): 
    def __init__(self, value, size, color, angle = 0,
                 x = 0, y = 0,
                 top = None, bottom = None, left = None, right = None,
                 dx = 0, dy = 0,
                 interval = 1, is_collideable = True):
        self._size = size 
        self._color = color 
        self._value = value
        self._font = pygame.font.Font(None, self._size)
        Sprite.__init__(self, self._create_surface(), angle,
                        x, y,
                        top, bottom, left, right,
                        dx, dy,
                        interval, is_collideable)

    def _create_surface(self):
        return self._font.render(str(self._value), 1, self._color) 

    def get_value(self): 
        return self._value
    
    def set_value(self, new_value):
        if new_value != self._value: 
            self._value = new_value
            self.image = self._create_surface() 
            
    value = property(get_value, set_value)
 
    def get_color(self): 
        return self._color
    
    def set_color(self, new_color): 
        if new_color != self._color: 
            self._color = new_color 
            surface = self._create_surface() 
            self.image = surface
            
    color = property(get_color, set_color)

    def get_size(self): 
        return self._size
    
    def set_size(self, new_size): 
        if new_size != self._size: 
            self._size = new_size
            self._font = pygame.font.Font(None, self._size)
            surface = self._create_surface() 
            self.image = surface

    size = property(get_size, set_size) 


class Question(Text):
    def __init__(self, value, size, color, angle = 0,
                 x = 0, y = 0,
                 top = None, bottom = None, left = None, right = None,
                 dx = 0, dy = 0,
                 interval = 1, is_collideable = True, responses = ()):
        Text.__init__(self, value, size, color, angle,
                      x, y,
                      top, bottom, left, right,
                      dx, dy,
                      interval, is_collideable)    
        self.responses = responses

    def tick(self):
        for key, action in self.responses:
            if keyboard.is_pressed(key):
                action()


class Message(Text):
    def __init__(self, value, size, color, angle = 0,
                 x = 0, y = 0,
                 top = None, bottom = None, left = None, right = None,
                 dx = 0, dy = 0,
                 lifetime = 0, is_collideable = True, after_death = None):
        Text.__init__(self, value, size, color, angle,
                      x, y,
                      top, bottom, left, right,
                      dx, dy,
                      lifetime, is_collideable) 
        self._after_death = after_death

    def tick(self):
        if self._after_death:
            self._after_death()
        self.stop()
        self.destroy()


class Animation(Sprite):
    def __init__(self, images, angle = 0,
                 x = 0, y = 0,
                 top = None, bottom = None, left = None, right = None,
                 dx = 0, dy = 0,
                 repeat_interval = 1, n_repeats = 0, is_collideable = True):
                 
        if images and type(images[0]) is type(""):
            images = load_animation(images)
	    
        self.images = images
        if self.images == []:
            raise GamesError("An animation with no images is illegal.")

        self.n_repeats = n_repeats or -1
        if self.n_repeats > 0:
            self.n_repeats = (self.n_repeats * len(self.images))
            
        first_image = self.next_image()
        
        Sprite.__init__(self, self.next_image(), angle,
                        x, y,
                        top, bottom, left, right,
                        dx, dy,
                        repeat_interval, is_collideable)

    def next_image(self):
        if self.n_repeats == 0: return None
        if self.n_repeats > 0: self.n_repeats -= 1
        new_image = self.images[0]
        self.images = self.images[1:] + [self.images[0]]
        return new_image

    def tick(self):
        new_image = self.next_image()
        if new_image is None:
            self.destroy()
        else:
            self.image = new_image

def load_image(filename, transparent = True): 
    try: 
        surface = pygame.image.load(filename) 
    except pygame.error: 
        raise GamesError( 'Could not load image "%s" %s'%(filename, pygame.get_error()) )
    if transparent: 
        corner = surface.get_at((0, 0)) 
        surface.set_colorkey(corner, RLEACCEL) 
    return surface.convert()

def scale_image(image, x_scale, y_scale = None):
    if y_scale is None: y_scale = x_scale
    (x_size, y_size) = image.get_size()
    x_size = x_size * x_scale
    y_size = y_size * y_scale
    return pygame.transform.scale(image, (x_size, y_size))

def load_animation(filenames, transparent = 1):
    def _(name, transparent = transparent):
        try: surface = pygame.image.load(name)
        except pygame.error:
            raise GamesError( 'Could not load animation frame "%s": %s' % (name, pygame.get_error()) )
        if transparent:
            surface.set_colorkey(surface.get_at((0,0)), RLEACCEL)
        return surface.convert()
    files = list(map(_, filenames))
    return files
 
def load_sound(filename): 
    return pygame.mixer.Sound(filename)


def init(screen_width = 640, screen_height = 480, fps = 50):
    global screen
    screen = Screen(screen_width, screen_height, fps)

mouse = Mouse()
keyboard = Keyboard()
music = Music()