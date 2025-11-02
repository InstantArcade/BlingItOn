import bitmaptools
from random import randrange
import math
import rgbmatrix
from hsv565 import HSV565

class WaveVis:
    
    visWidth = 64
    visHeight = 64
    visWidthHalf = 32
    visHeighthalf = 32
    
    wave_levels = [0]*64
    
    wave = 0
    wave_speed = 10
    
    hsv = HSV565()
    
    decay_time = 0
    
    accumulation_position = 31

    def __init__(self, WIDTH,HEIGHT):
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        self.visWidthHalf = WIDTH//2
        self.visHeighthalf = HEIGHT//2
        print( f"WaveVis initialized - Width {WIDTH}, Height {HEIGHT}")

    def reset( self ):
        for i in range(0,64):
            self.wave_levels[i] = 0
            
    def update( self, delta, bitmap, accel ):
#         self.wave += self.wave_speed * delta
#         self.wave = math.fmod(self.wave,math.pi*2)
        
        # move the position of the accumulator
        if math.fabs(accel[0]) > 2: # Overcome the dead zone
            self.accumulation_position += accel[0]*delta*8
            if self.accumulation_position < 0:
                self.accumulation_position = 0
            if self.accumulation_position > 63:
                self.accumulation_position = 63
            
            # add to levels (only if we're moving)
            for i in range(0,5):
                ap1 = int(self.accumulation_position) + i
                ap2 = int(self.accumulation_position) - i
                if ap1 < 0:
                    ap1 = 0
                if ap1 > 63:
                    ap1 = 63
                if ap2 < 0:
                    ap2 = 0
                if ap2 > 63:
                    ap2 = 63
                amount = (5-i)*0.005*delta
                self.wave_levels[ap1] += amount
                self.wave_levels[ap2] += amount
                
                # cap levels
                if self.wave_levels[ap1] < 21:
                    self.wave_levels[ap1] = 21
                if self.wave_levels[ap2] < 21:
                    self.wave_levels[ap2] = 21
                if self.wave_levels[ap1] > 41:
                    self.wave_levels[ap1] = 41
                if self.wave_levels[ap2] > 41:
                    self.wave_levels[ap2] = 41
        
        # decay levels
        self.decay_time += delta
        fixed_timeslice = 1/100
        if self.decay_time > fixed_timeslice:
            self.decay_time -= fixed_timeslice
            
            for i in range(0,64):
                self.wave_levels[i] *= 0.9
    
        color = self.hsv.getHSV(130)
        for x in range(0,64):
#             bitmaptools.draw_line(bitmap,x,32,x,63,0xFF00)
            bitmaptools.draw_line(bitmap,x,32-int(self.wave_levels[x]),x,63,color)
