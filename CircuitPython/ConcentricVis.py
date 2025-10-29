import bitmaptools
from random import randrange
import math
from hsv565 import HSV565

num_master_rings = 3

num_rings = 5
ring_spacing = 9

class CCircle:
    """ Represents a concentric circle """
    x = 0
    y = 0
    color = 0
    ang_x = 0
    ang_y = 0
    speed_x = 0
    speed_y = 0

    def move( self, delta ):
        #increment the angles
        self.ang_x += self.speed_x * delta
        self.ang_y += self.speed_y * delta

        # constrain angles to maintain precision
        pi2 = math.pi*2
        if self.ang_x >= pi2:
            self.ang_x -= pi2
        if self.ang_y >= pi2:
            self.ang_y -= pi2
        
        # we will apply these wave values in our draw function

    def draw( self, bitmap ):
        for i in range(0,num_rings):
            size = int(ring_spacing + i*ring_spacing)
            bitmaptools.draw_circle(bitmap,
                                    int(self.x + math.sin(self.ang_x) * 20),
                                    int(self.y + math.sin(self.ang_y) * 20),
                                    size, 
                                    self.color)
class ConcentricVis:
    hsv = HSV565()

    visWidth = 64
    visHeight = 64
    visWidthHalf = 32
    visHeighthalf = 32

    def __init__(self, WIDTH,HEIGHT):
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        self.visWidthHalf = WIDTH//2
        self.visHeighthalf = HEIGHT//2
        print( f"ConcentricVis initialized - Width {WIDTH}, Height {HEIGHT}")

    all_cc = []

    def reset( self ):
        hstep = 360//num_master_rings
        hue_start = randrange(0,359)
        for i in range(num_master_rings):
            a_shape= CCircle()

            a_shape.x = self.visWidthHalf
            a_shape.y = self.visHeighthalf
            a_shape.color = self.hsv.hsv2rgb565((hue_start+i*hstep)%360,1,1)
            a_shape.ang_x = i*2.3
            a_shape.ang_y = i*3.4
            a_shape.speed_x = 4.3
            a_shape.speed_y = 6.16
            self.all_cc.append(a_shape)
    
    def update( self, delta, bitmap, accel ):
        for i in range(num_master_rings):
            self.all_cc[i].move(delta)
            self.all_cc[i].draw(bitmap)
