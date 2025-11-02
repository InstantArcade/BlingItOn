import bitmaptools
from random import randrange
import math
import rgbmatrix
from hsv565 import HSV565

hsv = HSV565()
gravity = 0.3
restitution = 0.5
MASS_MUL = 2

class GravBall:
    pos = [31,31]
    velocity = [0,0]
    acceleration = [0,0]
    color = 0
    radius = 5
    mass = radius*MASS_MUL

    def move( self, delta, accel ):
        self.velocity = [accel[0],accel[1]]
        self.pos[0] += self.velocity[0] * self.mass * delta * 1
        self.pos[1] += self.velocity[1] * self.mass * delta * 1
        
#         if self.pos[0] < self.radius:
#             self.pos[0] -= self.velocity[0]
#         if self.pos[0] > 63-self.radius:
#             self.pos[0] -= self.velocity[0]
#             
#         if self.pos[1] < self.radius:
#             self.pos[1] -= self.velocity[1]
#         if self.pos[1] > 63-self.radius:
#             self.pos[1] -= self.velocity[1]

        if self.pos[0] < self.radius:
            self.pos[0] = self.radius
            self.velocity[0] = 0#*= -restitution
        if self.pos[0] > 63-self.radius:
            self.pos[0] = 63 - self.radius
            self.velocity[0] =0#*= -restitution
            
        if self.pos[1] < self.radius:
            self.pos[1] = self.radius
            self.velocity[1] =0#*= -restitution
        if self.pos[1] > 63-self.radius:
            self.pos[1] = 63 - self.radius
            self.velocity[1] =0#*= -restitution


    def collide(self, other):
        # get delta from other ball to us as a vector
        distAB = [other.pos[0]-self.pos[0],
                  other.pos[1]-self.pos[1]]
        distMag = math.sqrt(distAB[0]*distAB[0] + distAB[1]*distAB[1])
        radSum = self.radius + other.radius
        
        if distMag > 0 and radSum > distMag: #collided
            # correct positions
            overlap_half = ((radSum - distMag)/2)#*1.1
            # normalize the distance
            normal = [ distAB[0] / distMag, distAB[1] / distMag ]
            correction = [ normal[0]*overlap_half, normal[1]*overlap_half ]
            self.pos[0] -= correction[0]
            self.pos[1] -= correction[1]
            self.velocity[0] *= -restitution
            self.velocity[1] *= -restitution
            
            other.pos[0] += correction[0]
            other.pos[1] += correction[1]
            other.velocity[0] *= -restitution
            other.velocity[1] *= -restitution
            
    def render( self, bitmap ):
        if self.pos[0] >= 0 and self.pos[1] >= 0 and self.pos[0] <= 63 and self.pos[1] <= 63:
            bitmaptools.draw_circle(bitmap, int(self.pos[0]), int(self.pos[1]), self.radius, self.color)
    
class GravBallVis:
    MAX_BALLS = 10
    the_balls = []
    
    def reset( self ):
        #print( "GravBallVis resetting" )
        self.the_balls.clear()
        for i in range( self.MAX_BALLS ):
            gb = GravBall()
            gb.radius = randrange(2,12)
            gb.pos = [randrange(gb.radius,63-gb.radius), randrange(gb.radius,63-gb.radius)]
            gb.veloctiy = [0,0]
            gb.color = hsv.getHSV(randrange(0,360))
            gb.mass = gb.radius*MASS_MUL
            self.the_balls.append(gb)   
    
    def __init__(self, WIDTH, HEIGHT):
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        self.visWidthHalf = WIDTH//2
        self.visHeighthalf = HEIGHT//2
        
        self.reset()
        
        print( f"GravBallsVis initialized - Width {WIDTH}, Height {HEIGHT}")
        
    def update( self, delta, bitmap, accel ):
        # collide with the main circle (and bounce)
        # move all the_balls according to gravity
        for b in self.the_balls:
            b.move(delta, accel)
        # resolve a couple of times
        for c in range(0,2):
            # collide with each other (and bounce)
            for i in range(0,self.MAX_BALLS):
                for j in range(1,self.MAX_BALLS):
                    self.the_balls[i].collide(self.the_balls[j])
        
        # draw containing circle
        for b in self.the_balls:
            b.render( bitmap )
        
