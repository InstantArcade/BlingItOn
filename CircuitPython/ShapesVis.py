import bitmaptools
from random import randrange
import math
from hsv565 import HSV565

hue_base = 0
hue_speed = 20
hue_base_int = 0
hue_spread_percent = 50

class CShape:
    """ Represents a shape """
    x = 0
    y = 0
    size = 10
    color = 0
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
        pi2 = math.pi*2
        if self.ang_x >= pi2:
            self.ang_x -= pi2
        if self.ang_y >= pi2:
            self.ang_y -= pi2
        if self.ang_z >= pi2:
            self.ang_z -= pi2
        
        # we will apply these wave values in our draw function

    def draw( self, bitmap ):
        if self.shape == 0: # Circle? - add more types to expand this vis
            size = int(self.size + math.sin(self.ang_z) * 10)
            if size < 2:
                size = 2
            bitmaptools.draw_circle(bitmap,
                                    int(self.x + math.sin(self.ang_x) * 20),
                                    int(self.y + math.sin(self.ang_y) * 20),
                                    size, 
                                    self.color)

class ShapesVis:
    hsv = HSV565()
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
            a_shape.color = self.hsv.getHSV(int((hue_base_int+i*hue_step)%360))
            a_shape.ang_x = i*0.3
            a_shape.ang_y = i*0.4
            a_shape.ang_z = i*0.5
            a_shape.speed_x = 3
            a_shape.speed_y = 4
            a_shape.speed_z = -3

            a_shape.shape = 0

            self.all_shapes.append(a_shape)
    
    def update( self, delta, bitmap, accel ):
        global hue_base, hue_base_int, hue_speed
        # Animate colors
        hue_base += hue_speed * delta
        if int(hue_base) != hue_base_int:
            hue_base_int = int(hue_base)
            
        global hue_base_int, hue_spread_percent
        hue_step = (360*(hue_spread_percent/100))//self.num_shapes

        for i in range(self.num_shapes):
            self.all_shapes[i].move(delta)
            self.all_shapes[i].color = self.hsv.getHSV(int((hue_base_int+i*hue_step)%360))
            self.all_shapes[i].draw(bitmap)
