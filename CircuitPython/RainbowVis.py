import bitmaptools
from random import randrange
import math
import rgbmatrix
from hsv565 import HSV565

hsv = HSV565()

NUM_SHAPES = 15
all_shapes=[]
MOVE_SPEED = 120#64
follow_mode = True
LINE_SPACING = 1
POINT_BUFFER_LENGTH = NUM_SHAPES * LINE_SPACING*4
point_buffer = [0]*POINT_BUFFER_LENGTH
point_buffer_head = 0

hue_offset = 0

class RainbowShape:
    point_pos=[]
    point_vel=[]
    color = 0
    shape = 0
    active = False
    
    def move( self, delta, accel ):
        if self.active:
            if self.shape == 0:
                for i in range(0,4):
                    self.point_pos[i] += delta * MOVE_SPEED * self.point_vel[i]
                    if self.point_pos[i] < 0 or self.point_pos[i] > 63:
                        self.point_vel[i] *= -1 # reverese direction
                        self.point_pos[i] += delta * MOVE_SPEED * self.point_vel[i] # move in new direction
        
    def render( self, bitmap ):
        if self.active:
            if self.shape == 0:
                bitmaptools.draw_line(bitmap,
                                       int(self.point_pos[0]), int(self.point_pos[1]),
                                       int(self.point_pos[2]), int(self.point_pos[3]),
                                       self.color );

class RainbowVis:
    def reset( self ):
        global first_point_pos, first_point_vel
        all_shapes.clear()
        first_shape = True
        for i in range( NUM_SHAPES ):
            rs = RainbowShape()
            rs.shape = 0 # 0 is regular line
            rs.point_pos=[0]*4
            rs.point_vel = [0]*4
            for j in range(0,4):
                rs.point_pos[j] = randrange(0,64)
                # pick a random x,y direction for the points
                rs.point_vel[j] = randrange(60,140)/100
                if randrange(0,100) < 50:
                    rs.point_vel[j] *= -1
            if follow_mode:
                hue_step = 360//(NUM_SHAPES)
                rs.color = hsv.getHSV(int(i*hue_step))
            else:
                rs.color = hsv.getHSV(randrange(0,360))
            rs.active = True
            all_shapes.append(rs)

    def __init__(self, WIDTH, HEIGHT):
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        self.visWidthHalf = WIDTH//2
        self.visHeighthalf = HEIGHT//2
        
        self.reset()
        
        print( f"RainbowVis initialized - Width {WIDTH}, Height {HEIGHT}")
        
    def update( self, delta, bitmap, accel ):
        global point_buffer, point_buffer_head, LINE_SPACING, POINT_BUFFER_LENGTH, hue_offset
        hue_offset = (hue_offset + delta*1)%360
        
        if follow_mode:
            idx = point_buffer_head
            for i in range(0,4):
                point_buffer[idx+i] = all_shapes[0].point_pos[i]
                
            for i in range(NUM_SHAPES-1,0,-1):
                if all_shapes[i].shape == 0: # handling line only at this point
                    idx = (point_buffer_head+0+i*LINE_SPACING*4)%POINT_BUFFER_LENGTH
                    for j in range(0,4):
                        all_shapes[i].point_pos[j] = point_buffer[idx+j]
                    
            all_shapes[0].move(delta, accel)
            # move buffer head
            point_buffer_head = (point_buffer_head+4)%POINT_BUFFER_LENGTH
            
        else: # independent movement
            for s in all_shapes:
                s.move(delta, accel)
        
        global hue_offset
        i = 0
        for s in all_shapes:
#             hue_step = 360//(NUM_SHAPES*3)
#             s.color = hsv.getHSV((int(hue_offset*i*hue_step)%360))
            s.render(bitmap)
            i+=1
#         for i in range(NUM_SHAPES-1,0,-1): # draw in reverse so leading shape is always at the front
#             all_shapes[i].render(bitmap)
        
