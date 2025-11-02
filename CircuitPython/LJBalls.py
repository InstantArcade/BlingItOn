from random import randrange
import math
from hsv565 import HSV565
import bitmaptools

class Ball:
    x = 0
    y = 0
    s1 = 0.5#1
    s2 = 0.75#1.5
    a1 = 0
    a2 = 0
    color = 65535

class LJBalls:
    """ Lissajous Balls """


    MAX_NUM_BALLS = 40
    all_balls = []

    speed = 5#3.5
    hue_offset = 0

    separation = 0.3#0.4

    visWidth = 32
    visHeight = 32
    visWidthHalf = 16
    visHeighthalf = 16

    def __init__(self, WIDTH,HEIGHT):
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        self.visWidthHalf = int(WIDTH/2)
        self.visHeighthalf = int(HEIGHT/2)
        print( f"LJBalls initialized - Width {WIDTH}, Height {HEIGHT}")


    hsv = HSV565()

    def safe_plot( self, bitmap, x, y, color ):
        if x >= 0 and x < self.visWidth and y >= 0 and y <self.visHeight:
                bitmap[int(x),int(y)] = color

    def reset( self ):
        for i in range(self.MAX_NUM_BALLS):
            b = Ball()
#             b.s1 = 1
#             b.s2 = 1.5
            b.a1 = ((math.pi*2)/self.MAX_NUM_BALLS*self.separation)*i
            b.a2 = ((math.pi*2)/self.MAX_NUM_BALLS*self.separation)*2.5*i
            b.color = self.hsv.getHSV( i*10 )

            self.all_balls.append(b)

        
    def move( self, delta, accel ):
        for i in range(self.MAX_NUM_BALLS):
            b = self.all_balls[i]
            b.x = self.visWidth/2 + math.sin(b.a1)*self.visWidthHalf
            b.y = self.visHeight/2 + math.cos(b.a2)*self.visHeighthalf

            b.a1 += b.s1*delta*self.speed
            if b.a1 > math.pi*2:
                b.a1 -= math.pi*2

            b.a2 += b.s2*delta*self.speed
            if b.a2 > math.pi*2:
                b.a2 -= math.pi*2

        self.hue_offset += 1
        self.hue_offset %= 360

    def render( self, bitmap ):
        # draw all the balls onto the bitmap
        for i in range( len(self.all_balls) ):
            s = self.all_balls[i]
            c = self.hsv.getHSV(i*5+self.hue_offset)
#             print(hex(c))
            # Draw each ball

            bitmaptools.draw_circle(bitmap, int(s.x), int(s.y), 1, c)
            
            # cross type
#            self.safe_plot( bitmap, s.x, s.y, c )
#            self.safe_plot( bitmap, s.x, s.y-1, c )
#            self.safe_plot( bitmap, s.x, s.y+1, c )
#            self.safe_plot( bitmap, s.x-1, s.y, c )
#            self.safe_plot( bitmap, s.x+1, s.y, c )

            #cube type
#             self.safe_plot( bitmap, s.x, s.y, c )
#             self.safe_plot( bitmap, s.x+1, s.y, c )
#             self.safe_plot( bitmap, s.x, s.y+1, c )
#             self.safe_plot( bitmap, s.x+1, s.y+1, c )

            # small ball
            # everything above, plus...
#             self.safe_plot( bitmap, s.x, s.y-1, c ) # top
#             self.safe_plot( bitmap, s.x+1, s.y-1, c )
#             self.safe_plot( bitmap, s.x-1, s.y, c ) # left
#             self.safe_plot( bitmap, s.x-1, s.y+1, c )
#             self.safe_plot( bitmap, s.x+2, s.y, c ) # right
#             self.safe_plot( bitmap, s.x+2, s.y+1, c )
#             self.safe_plot( bitmap, s.x, s.y+2, c ) # bottom
#             self.safe_plot( bitmap, s.x+1, s.y+2, c )

            # if s.tx >= 0 and s.tx < 32 and s.ty >= 0 and s.ty <32:
            #     bitmap[int(s.tx),int(s.ty)] = s.color

    def update( self, delta, bitmap, accel ):
        self.move( delta, accel )
        self.render( bitmap )
