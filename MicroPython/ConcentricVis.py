from random import randrange
import math
from hsv import hsv_to_rgb_255
from fastcircle import bresenhams_circle

num_master_rings = 2

num_rings = 4
ring_spacing = 9

class CCircle:
    """ Represents a concentric circle """
    x = 0
    y = 0
    color = [0,0,0]
    ang_x = 0
    ang_y = 0
    speed_x = 0
    speed_y = 0

    def move( self, delta ):
        #increment the angles
        self.ang_x += self.speed_x * delta
        self.ang_y += self.speed_y * delta

        # constrain angles to maintain precision
        self.ang_x = math.fmod(self.ang_x, math.pi*2)
        self.ang_y = math.fmod(self.ang_y, math.pi*2)
        
        # we will apply these wave values in our draw function

    def draw( self, display ):
        for i in range(0,num_rings):
            size = int(ring_spacing + i*ring_spacing)
            pen = display.create_pen(self.color[0],self.color[1],self.color[2])
            display.set_pen( pen )
            bresenhams_circle( display, int(self.x + math.sin(self.ang_x) * 20),
                            int(self.y + math.sin(self.ang_y) * 20), size)
            
class ConcentricVis:
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
        from interstate75 import Interstate75
        hstep = 360//num_master_rings
        hue_start = randrange(0,359)
        for i in range(num_master_rings):
            a_shape= CCircle()

            a_shape.x = self.visWidthHalf
            a_shape.y = self.visHeighthalf
            a_shape.color = hsv_to_rgb_255((hue_start+i*hstep)%360,255,255)
            a_shape.ang_x = i*2.3
            a_shape.ang_y = i*3.4
            a_shape.speed_x = 4.3
            a_shape.speed_y = 6.16
            self.all_cc.append(a_shape)
    
    def update( self, delta, display, accel ):
        for i in range(num_master_rings):
            self.all_cc[i].move(delta)
            self.all_cc[i].draw(display)
