from random import randrange
import math
from hsv import hsv_to_rgb_255

num_grids = 5
change_colors_every_seconds = 20

class GridLayer:
    """ Represents a grid layer """
    x = 0
    y = 0
    color = [0,0,0]
    target_color = [0,0,0]
    blend = 0
    grid_spacing = 9
    
    speed_x = 0
    speed_y = 0

    def move( self, delta, accel ):
        #increment the position
        self.x += self.speed_x * accel[0] * 1.3 * delta
        self.y += self.speed_y * accel[1] * 1.3 * delta
            
        # constrain x/y
        self.x = self.x%64
        self.y = self.y%64
        
        # Blend to target color?
        if self.blend > 0.0001:
            # Blend
            self.blend += delta

    def draw( self, display ):
        # draw vertical and horizontal lines with grid_spacing
        # with offset on the x & y

        # Draw lines
        num_lines = 64//self.grid_spacing
        for off in range(num_lines):
            c = self.color.copy()
            if self.blend > 0.0001:
                if self.blend < 1:
                    c[0] = int(self.color*self.blend + self.target_color[0]*(1-self.blend))
                    c[1] = int(self.color*self.blend + self.target_color[1]*(1-self.blend))
                    c[2] = int(self.color*self.blend + self.target_color[2]*(1-self.blend))
                else:
                    self.blend = 0
                    c = self.target_color.copy()
                    self.color = self.target_color.copy()
            pen = display.create_pen(c[0],c[1],c[2])
            display.set_pen(pen)
            display.line(    int((self.x + off*self.grid_spacing))%64,
                                  0,
                                  int((self.x + off*self.grid_spacing))%64,
                                  63)
            display.line(0,
                                  int((self.y + off*self.grid_spacing))%64,
                                  63,
                                  int((self.y + off*self.grid_spacing))%64)
            
class GridVis:

    visWidth = 64
    visHeight = 64
    visWidthHalf = 32
    visHeighthalf = 32
    
    color_reset_timer = 0

    def __init__(self, WIDTH,HEIGHT):
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        self.visWidthHalf = WIDTH//2
        self.visHeighthalf = HEIGHT//2
        print( f"ConcentricVis initialized - Width {WIDTH}, Height {HEIGHT}")

    all_grids = []

    def reset_colors( self ):
        hue_start = randrange(0,359)
        for i in range(num_grids):
            a_grid = self.all_grids[i]
            a_grid.color = hsv_to_rgb_255((hue_start+i*1)%360,
                                               (0.5+(0.5/num_grids)*i)*255,
                                               (0.1+(0.9/num_grids)*i)*255)
        
    def reset( self ):
        self.all_grids = []
        hstep = 360//num_grids
        hue_start = randrange(0,359)
#         print( f"grid resetting, new hue index is {hue_start}")
        for i in range(num_grids):
            a_grid = GridLayer()
            a_grid.grid_spacing = 10+i*5.5
            a_grid.x = self.visWidthHalf
            a_grid.y = self.visHeighthalf
#             a_grid.color = self.hsv.hsv2rgb565((hue_start+i*1)%360,
#                                                0.5+(0.5/num_grids)*i,
#                                                0.1+(0.9/num_grids)*i)
            a_grid.ang_x = i*2.3
            a_grid.ang_y = i*3.4
            a_grid.speed_x = 26+i*10
            a_grid.speed_y = 26+i*10
            self.all_grids.append(a_grid)
        self.reset_colors()
    
    def update( self, delta, display, accel ):
        
        self.color_reset_timer += delta
        if self.color_reset_timer > change_colors_every_seconds:
            self.color_reset_timer = 0
            self.reset_colors()
            
        
        for i in range(num_grids):
            self.all_grids[i].move(delta, accel)
    
        for i in range(num_grids):
            self.all_grids[i].draw(display)
