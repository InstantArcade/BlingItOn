from random import randrange
import math
from hsv import hsv_to_rgb_255

hue_base = 0
hue_speed = 20
hue_base_int = 0
hue_spread_percent = 50

debug_timer = 0


class CShape:
    """ Represents a shape """
    x = 0
    y = 0
    size = 10
    color = 0
    ci = 0
    ang_x = 0 # controls x position
    ang_y = 0 # controls y position
    ang_z = 0 # controls size
    speed_x = 0
    speed_y = 0
    speed_z = 0
    shape = 0 # shape type (only circle so far)

    def move( self, delta ):
        #increment the angles
        self.ang_x += self.speed_x * delta
        self.ang_y += self.speed_y * delta
        self.ang_z += self.speed_z * delta

        # constrain angles to maintain precision
        self.ang_x = math.fmod(self.ang_x, math.pi*2)
        self.ang_y = math.fmod(self.ang_y, math.pi*2)
        self.ang_z = math.fmod(self.ang_z, math.pi*2)
        
        # we will apply these wave values in our draw function

    def draw( self, display ):
        if self.shape == 0: # Circle? - add more types to expand this vis
            p = display.create_pen(self.color[0],self.color[1],self.color[2])
#            p = display.create_pen_hsv(self.ci/360.0,1.0,1.0)
            display.set_pen(p)
            size = int(self.size + math.sin(self.ang_z) * 10)
            if size < 2:
                size = 2
            display.circle( int(self.x + math.sin(self.ang_x) * 20),
                            int(self.y + math.sin(self.ang_y) * 20), size)

class ShapesVis:
    num_shapes = 10

    visWidth = 64
    visHeight = 64
    visWidthHalf = 32
    visHeighthalf = 32
    
    def __init__(self, WIDTH,HEIGHT):
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        self.visWidthHalf = WIDTH//2
        self.visHeighthalf = HEIGHT//2
        print( f"ShapesVis initialized - Width {WIDTH}, Height {HEIGHT}")

    all_shapes = []

    def reset( self ):
        global huse_base_int, hue_spread_percent
        hue_step = (360*(hue_spread_percent/100))//self.num_shapes
        self.all_shapes = [] # Clear shapes array
        for i in range(self.num_shapes):
            a_shape= CShape()

            a_shape.x = self.visWidthHalf
            a_shape.y = self.visHeighthalf
            a_shape.z = 0
            a_shape.ci = int((hue_base_int+i*hue_step)%360)
            a_shape.color = hsv_to_rgb_255(int((hue_base_int+i*hue_step)%360),255,255)
            a_shape.ang_x = i * 0.3
            a_shape.ang_y = i * 0.4
            a_shape.ang_z = i * 0.5
            a_shape.speed_x = 3
            a_shape.speed_y = 4
            a_shape.speed_z = -3

            a_shape.shape = 0

            self.all_shapes.append(a_shape)
    
    def update( self, delta, display, accel ):
        global hue_base, hue_base_int, hue_speed, debug_timer
        # Animate colors
        hue_base += hue_speed * delta
        if int(hue_base) != hue_base_int:
            hue_base_int = int(hue_base)
            
        global hue_base_int, hue_spread_percent
        hue_step = (360*(hue_spread_percent/100))//self.num_shapes
        
#         debug_timer += delta
#         if debug_timer > 1:
#             debug_timer = 0
#             print( f"Angle Z is {self.all_shapes[0].ang_z}" )

        for i in range(self.num_shapes):
            self.all_shapes[i].move(delta)
            self.all_shapes[i].ci = int((hue_base_int+i*hue_step)%360)
            self.all_shapes[i].color = hsv_to_rgb_255(int((hue_base_int+i*hue_step)%360),255,255)
            self.all_shapes[i].draw(display)
