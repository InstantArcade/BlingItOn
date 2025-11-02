from random import randrange
import math
from hsv565 import HSV565


class Vertex:
    """ represents a vertex object """
    x = 0
    y = 0
    z = 0
    tx = 0 #translated/rotated/scaled x position
    ty = 0
    color = 0xFFFF

class CubeVis():
    """ A simple 3D rotating Cube visulaization """

    def __init__(self, WIDTH,HEIGHT):
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        print( f"CubeVis initialized - Width {WIDTH}, Height {HEIGHT}")

    x_rot = 0
    y_rot = 0
    z_rot = 0

    x_rot_speed = 1     * 2
    y_rot_speed = 1.01   * 2
    z_rot_speed = -0.02   * 2

    zoom = 3 #16

    MAX_NUM_VERTS = 140
    all_verts = []

    cube_size = 16
    x_off = 16
    y_off = 16

    size_wave = 0
    size_wave_speed = 10

    xo_wave = 0
    yo_wave = 0
    xo_speed = 10
    yo_speed = 2

    hue_offset = 0
    hsv = HSV565()

    last_print = 0

    #                   x,y,z per vert
    cube_vert_defs = [
        [-0.5,-0.5,-0.5],
        [ 0.5,-0.5,-0.5],
        [ 0.5,-0.5, 0.5],
        [-0.5,-0.5, 0.5],
        [-0.5, 0.5,-0.5],
        [ 0.5, 0.5,-0.5],
        [ 0.5, 0.5, 0.5],
        [-0.5, 0.5, 0.5],
        ]

    cube_face_defs = [
            [0,1,2,3,0],
            [4,5,6,7,4],
            [0,4],
            [1,5],
            [2,6],
            [3,7],
        ]

    #                   x,y,z per vert
    pyramid_vert_defs = [
        [0,-0.5,0],
        [-0.5, 0.5,-0.5],
        [ 0.5, 0.5,-0.5],
        [ 0.5, 0.5, 0.5],
        [-0.5, 0.5, 0.5],
        ]

    pyramid_face_defs = [
            [1,2,3,4,1],
            [0,1],
            [0,2],
            [0,3],
            [0,4],
        ]


    name_vert_defs = [
        [0,0,0], # small o
        [ 2,0,0],
        [ 2,2,0],
        [0,2,0],

        [-4,-2,0], # big B
        [-2,-2,0],
        [-2,0,0],
        [-4,0,0],
        [-1,0,0],
        [-1,2,0],
        [-4,2,0],

        [3,-2,0], # small b
        [3,0,0],
        [5,0,0],
        [5,2,0],
        [3,2,0],

        ]

    name_face_defs = [
            [0,1,2,3,0], # small o
            [4,5,6], # top of big b
            [7,8,9,10,4], # rest of big b
            [12,13,14,15,11], # small b
        ]

    xverts = [
        [-4.5,-4.5,0],#0
        [-4.5,4.5,0],#1
        [-1.5,4.5,0],#2
        [-0.5,3.5,0],#3
        [-0.5,2.5,0],#4
        [-1.5,1.5,0],#5
        [-1.5,-0.5,0],#6
        [-0.5,-1.5,0],#7
        [-0.5,-2.5,0],#8
        [-1.5,-4.5,0],#9
        [-3.5,-3.5,0],#10
        [-3.5,-0.5,0],#11
        [-1.5,-1.5,0],#12
        [-2.5,-3.5,0],#13
        [-3.5,3.5,0],#14
        [-1.5,3.5,0],#15
        [-2.5,1.5,0],#16
        [-3.5,0.5,0],#17
        [0.5,-4.5,0],#18
        [0.5,4.5,0],#19
        [1.5,4.5,0],#20
        [1.5,0.5,0],#21
        [3.5,0.5,0],#22
        [3.5,4.5,0],#23
        [4.5,4.5,0],#24
        [4.5,-4.5,0],#25
        [3.5,-4.5,0],#26
        [3.5,-1.5,0],#27
        [1.5,-1.5,0],#28
        [1.5,-4.5,0],#29
        ]

    xfaces = [
        [0,1,2,3,4,5,6,7,8,9,0],
        [10,11,12,13,10],
        [14,15,16,17,14],
        [18,19,20,21,22,23,24,25,26,27,28,29,18],
        ]

    sm_verts = [
        [-0.5,-5.5,0.625],#0
        [-3.5,-5.5,0.625],#1
    	[-4.5,-4.5,0.625],#2
    	[-5.5,-3.5,0.625],#3
    	[-5.5,-2.5,0.625],#4
    	[-4.5,-1.5,0.625],#5
    	[-2.5,-0.5,0.625],#6
    	[-1.5,0.5,0.625],#7
    	[-1.5,1.5,0.625],#8
    	[-2.5,2.5,0.625],#9
    	[-3.5,3.5,0.625],#10
    	[-5.5,3.5,0.625],#11
    	[-5.5,4.5,0.625],#12
    	[-2.5,4.5,0.625],#13
    	[-1.5,3.5,0.625],#14
    	[-0.5,2.5,0.625],#15
    	[-0.5,1.5,0.625],#16
    	[-0.5,-0.5,0.625],#17
    	[-1.5,-1.5,0.625],#18
    	[-3.5,-2.5,0.625],#19
    	[-3.5,-3.5,0.625],#20
    	[-2.5,-4.5,0.625],#21
    	[-0.5,-4.5,0.625],#22
    	[0.5,4.5,0.625],#23
    	[0.5,-5.5,0.625],#24
    	[1.5,-5.5,0.625],#25
    	[2.5,-2.5,0.625],#26
    	[3.5,-2.5,0.625],#27
    	[4.5,-5.5,0.625],#28
    	[5.5,-5.5,0.625],#29
    	[5.5,4.5,0.625],#30
    	[4.5,4.5,0.625],#31
    	[4.5,-1.5,0.625],#32
    	[3.5,0.5,0.625],#33
    	[2.5,0.5,0.625],#34
    	[1.5,-1.5,0.625],#35
    	[1.5,4.5,0.625],#36
    	]

    sm_faces = [
    	[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,0],
        [23,24,25,26,27,28,29,30,31,32,33,34,35,36,23],
        ]

    OFFSET = 15

    def BresenhamLine( self, bitmap, x0, y0, x1, y1, color ):
        x0 = int(x0)
        x1 = int(x1)
        y0 = int(y0)
        y1 = int(y1)

        dx =  int(abs(x1-x0))#; // delta x
        sx = 0
        if x0 < x1:
            sx = 1
        else: 
            sx = -1 #; // s direction
  
        dy = int(-abs(y1-y0))#; // delta y
        sy = 0
        if  y0 < y1:
            sy = 1
        else: 
            sy = -1 #; // y direction
  
        err = dx+dy #;  // error value e_xy
  
        while True: #   // loop
            # bound check
            if ( x0 >= 0 and x0 < self.visWidth and y0 >=0 and y0 < self.visHeight ):
                bitmap[int(x0),int(y0)] = color

            if (x0 == x1 and y0 == y1):
                 break  #; // we reached the destination - stop now
            
            e2 = 2*err
            if (e2 >= dy): # // e_xy + e_x > 0
                err += dy
                x0 += sx    #; // move along the x direction

            if (e2 <= dx): # // e_xy + e_y < 0
                err += dx
                y0 += sy    # // move along the y direction
    
    def reset( self ):

        self.x_off = self.visWidth/2
        self.y_off = self.visHeight/2

#         for i in (self.sm_verts):
        for i in (self.name_vert_defs):
            z = 0.12#0.15
            v = Vertex()
            v.x = i[0] * z
            v.y = i[1] * z
            v.z = i[2] * z
            v.color = 0xffff
            self.all_verts.append(v)


    def constrain2pi2( self, value ):
        if value > math.pi*2:
            value -= math.pi*2
        if value < 0:
            value += math.pi*2
        return value

    def update( self, delta, bitmap, accel ):
        self.hue_offset += 1
        self.hue_offset %= 360

        # we move the rotator for all the verts
        self.x_rot += self.x_rot_speed * delta
        self.y_rot += self.y_rot_speed * delta
        self.z_rot += self.z_rot_speed * delta

        self.size_wave += (math.pi/self.size_wave_speed)  * delta
        self.xo_wave += (math.pi/self.xo_speed) * delta
        self.yo_wave += (math.pi/self.yo_speed) * delta

        # constrain angles to maintain precision
        self.x_rot = self.constrain2pi2(self.x_rot)
        self.y_rot = self.constrain2pi2(self.y_rot)
        self.z_rot = self.constrain2pi2(self.z_rot)
        self.size_wave = self.constrain2pi2(self.size_wave)
        self.xo_wave = self.constrain2pi2(self.xo_wave)
        self.yo_wave = self.constrain2pi2(self.yo_wave)

        self.last_print += delta
        if self.last_print >= 1.0:
            self.last_print -= 1.0
            #print( f"Rot x:{self.x_rot},y:{self.y_rot},Z:{self.z_rot}")
            #print( f"Waves x:{self.xo_wave},y:{self.yo_wave},Size:{self.size_wave}")

        self.cube_size = 18 + math.sin(self.size_wave)*7
        self.x_off = self.visWidth/2 + math.cos(self.xo_wave) *self.visWidth/3
        self.y_off = self.visHeight/2 + math.sin(self.yo_wave) *self.visHeight/3

        # buffer some calculations for multiple use
        sin_x = math.sin(self.x_rot)
        cos_x = math.cos(self.x_rot)
        sin_y = math.sin(self.y_rot)
        cos_y = math.cos(self.y_rot)
        sin_z = math.sin(self.z_rot)
        cos_z = math.cos(self.z_rot)

        focal = 300

        # move all the verts
        for i in range(len(self.all_verts)):
            vert = self.all_verts[i]
            #scale
            lfx = vert.x * self.cube_size
            lfy = vert.y * self.cube_size
            lfz = vert.z * self.cube_size

            # print( f"v{i}: x{lfx}, y{lfy}, z{lfz}" )

            #x rot
            fxy = cos_x * lfy - sin_x * lfz
            fxz = sin_x * lfy + cos_x * lfz

            #yrot
            fyz = cos_y * fxz - sin_z * lfx
            fyx = sin_y * fxz + cos_y * lfx

            #zrot
            fzx = cos_z * fyx - sin_z * fxy
            fzy = sin_z * fyx + cos_z * fxy

            #perspective
            scale_factor = focal / (focal+fyz)
            lfx = fzx * scale_factor
            lfy = fzy * scale_factor

            #translate to center
            vert.tx = lfx + self.x_off
            vert.ty = lfy + self.y_off


        c = self.hsv.getHSV(self.hue_offset)
#         c=16505
#        for faces in( self.sm_faces ):
        for faces in( self.name_face_defs ):
            draw_from = -1
            for f in( faces ):
                if draw_from == -1:
                    draw_from = f
                else:
                    # we have a from point, f is the new to
                    self.BresenhamLine( bitmap, 
                        self.all_verts[draw_from].tx, self.all_verts[draw_from].ty, 
                        self.all_verts[f].tx, self.all_verts[f].ty, c )
                    draw_from = f