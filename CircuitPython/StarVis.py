from random import randrange
import math
from hsv565 import HSV565

# ~ 48 FPS with 100 stars on MatrixPortal M4
# ~ 78 FPS with 50 stars
# ~ 120 FPS with 20 stars

class Star:
    """ represents a star object """
    x = 0
    y = 0
    z = 0
    tx = 0 #translated/rotated/scaled x position
    ty = 0
    tz = 0
    color = 0

class StarVis:
    """ A simple rotating Starfield visulaization """
    hsv = HSV565()
    zmin = 100
    zmax = -100

    x_rot = 0
    y_rot = 0
    z_rot = 0

    x_rot_speed = 1
    y_rot_speed = 1.1
    z_rot_speed = 1.02#1.2

    zoom = 16

    visWidth = 32
    visHeight = 32
    visWidthHalf = 16
    visHeighthalf = 16

    def __init__(self, WIDTH,HEIGHT):
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        self.visWidthHalf = WIDTH//2
        self.visHeighthalf = HEIGHT//2
        print( f"StarVis initialized - Width {WIDTH}, Height {HEIGHT}")


    MAX_NUM_STARS = 75
    all_stars = []

    def reset( self ):
        for i in range(self.MAX_NUM_STARS):
            a_star = Star()

            a_star.x = randrange(-self.visWidthHalf,self.visWidthHalf)
            a_star.y = randrange(-self.visHeighthalf,self.visHeighthalf)
            a_star.z = randrange(-self.visWidthHalf,self.visWidthHalf)
            a_star.color = randrange(0,360)#randrange(0,65535)

            self.all_stars.append(a_star)

    def starcmp( s1, s2 ):
        if s1.tz < s2.tz:
            return -1
        elif s1.tz > s2.tz:
            return 1
        else:
            return 0

    def update( self, delta, bitmap, accel ):
        self.zmin = 100
        self.zmax = -100
        # we move the rotator for all the stars
        #self.x_rot += accel[1]*delta #self.x_rot_speed * delta
        #self.y_rot += accel[0]*delta #self.y_rot_speed * delta
        #self.z_rot += accel[2]*delta #self.z_rot_speed * delta
        self.x_rot += self.x_rot_speed * delta
        #self.y_rot += self.y_rot_speed * delta
        self.z_rot += self.z_rot_speed * delta

        # constrain angles to maintain precision
        self.x_rot = math.fmod(self.x_rot,math.pi*2)
        self.y_rot = math.fmod(self.y_rot,math.pi*2)
        self.z_rot = math.fmod(self.z_rot,math.pi*2)
#         if self.x_rot >= math.pi*2:
#             self.x_rot -= math.pi*2
#         if self.y_rot >= math.pi*2:
#             self.y_rot -= math.pi*2
#         if self.z_rot >= math.pi*2:
#             self.z_rot -= math.pi*2

        # buffer some calculations for multiple use
        sin_x = math.sin(self.x_rot)
        cos_x = math.cos(self.x_rot)
        sin_y = math.sin(self.y_rot)
        cos_y = math.cos(self.y_rot)
        sin_z = math.sin(self.z_rot)
        cos_z = math.cos(self.z_rot)

        focal = 300

        # move all the stars
        for i in range(len(self.all_stars)):
            star = self.all_stars[i]
            #scale
            lfx = star.x * 1
            lfy = star.y * 1
            lfz = star.z * 1

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

            # save rotated z position
            star.tz =  fyz
            if( star.tz < self.zmin ):
                self.zmin = star.tz
            if( star.tz > self.zmax ):
                self.zmax = star.tz

            #translate to center
            star.tx = lfx + self.visWidthHalf
            star.ty = lfy + self.visHeighthalf


        # draw all the stars onto the bitmap
        sorted_stars = sorted(self.all_stars, key=lambda s: s.tz, reverse=True)
        for i in range( len(sorted_stars) ):#len(self.all_stars) ):
            s = sorted_stars[i]#all_stars[i]

            if s.tx >= 0 and s.tx < self.visWidth and s.ty >= 0 and s.ty < self.visHeight:
                # put z in range 0-1
#                 print( self.zmin )
#                 print( self.zmax )
#                 print( s.tz )
#                 s.tz /= (self.zmax-self.zmin)
#                 s.tz -= self.zmin
#                 print( s.tz )
#                 c = int(self.hsv.hsv2rgb565(1,1,s.tz))
#                 print(c)
                s.tz = ((s.tz - self.zmin) / (self.zmax-self.zmin)*0.9)+0.1
                if s.tz > 1:
                    s.tz = 1
                if s.tz < 0:
                    s.tz = 0
#                 print( s.tz )
#                 c = self.hsv.hsv2rgb565(s.color,s.tz,1)
                c = self.hsv.hsv2rgb565(0,s.tz,1)
#                 print(c)
                bitmap[int(s.tx),int(s.ty)] = c
#                 bitmap[int(s.tx),int(s.ty)] = (int)(s.z*0xff)&65535#s.color