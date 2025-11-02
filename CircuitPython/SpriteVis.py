import bitmaptools
from random import randrange
import math
import rgbmatrix
from hsv565 import HSV565
import displayio # General drawing tools
import adafruit_imageload

# some handy index aliases
SRC_X = 0
SRC_Y = 1
SRC_W = 2
SRC_H = 3
SRC_FRAME_TIME = 4

class AnimatedSprite:
    width = 16
    height = 16
    x = 31
    y = 31
    cur_frame = 0
    frame_time = 0
    
    # frames [x,y,w,h,delay] for each
    frames = [
        # Ms-Pac
        [160, 16, 16, 16, 0.2],
        [160, 32, 16, 16, 0.2],
        [160, 16, 16, 16, 0.2],
        [160,  0, 16, 16, 0.2],
        ]
    
class SpriteVis:
    hsv = HSV565()

    visWidth = 64
    visHeight = 64
    visWidthHalf = 32
    visHeighthalf = 32
    
    source_bitmap = None
    source_palette = None
    
    wave = 0
    
    all_sprites = []
    
    def __init__(self, WIDTH,HEIGHT, palette = displayio.Palette(256) ):
        
#        print( f"SpriteVis initializing - Width {WIDTH}, Height {HEIGHT}")
#        self.source_palette = displayio.Palette(256)
        
#         self.source_bitmap, self.source_palette = adafruit_imageload.load("/msspr.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        #self.source_palette = displayio.Palette(256)
        self.source_bitmap, self.source_palette = adafruit_imageload.load("/msspr.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        
#         for i in range(0,256):
#             print( f"{self.source_palette[i]:#x}")

        # Create sprites/animations
        self.all_sprites = []
        # Ms-Pac
        s = AnimatedSprite()
        s.frames = [
            [160, 16, 16, 16, 0.1],
            [160, 32, 16, 16, 0.1],
            [160, 16, 16, 16, 0.1],
            [160,  0, 16, 16, 0.1] ]
        self.all_sprites.append(s)

        # Orange Ghost
        s = AnimatedSprite()
        s.frames = [
            [192,  0, 16, 16, 0.2],
            [192, 16, 16, 16, 0.2]
            ]
        self.all_sprites.append(s)
        

        # Pink Ghost
        s = AnimatedSprite()
        s.frames = [
            [208,  0, 16, 16, 0.2],
            [208, 16, 16, 16, 0.2]
            ]
        self.all_sprites.append(s)
        

        # Cyan Ghost
        s = AnimatedSprite()
        s.frames = [
            [224,  0, 16, 16, 0.2],
            [224, 16, 16, 16, 0.2]
            ]
        self.all_sprites.append(s)
        
        # Red Ghost
        s = AnimatedSprite()
        s.frames = [
            [240,  0, 16, 16, 0.2],
            [240, 16, 16, 16, 0.2]
            ]
        self.all_sprites.append(s)
        

        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        self.visWidthHalf = WIDTH//2
        self.visHeighthalf = HEIGHT//2
        print( f"SpriteVis initialized - Width {WIDTH}, Height {HEIGHT}")
    
    def reset(self):
        pass
    
    def update( self, delta, bitmap, palettized_bitmap, accel ):
        self.wave += delta * 3.5
        self.wave = math.fmod(self.wave,3.14159265*2)
        
        # Update animations
        for i in range(0, len(self.all_sprites)):
            s = self.all_sprites[i]
            num_frames = len(s.frames)
            s.frame_time += delta
            if s.frame_time > s.frames[s.cur_frame][SRC_FRAME_TIME]:
                s.frame_time -= s.frames[s.cur_frame][SRC_FRAME_TIME]
                s.cur_frame += 1
                s.cur_frame %= num_frames
        
        palettized_bitmap.fill(0)
        num_sprites = len(self.all_sprites)
        ang_step = 6.242/num_sprites
        
        for i in range(0, len(self.all_sprites)):
            s = self.all_sprites[i]
            anim_data = s.frames[s.cur_frame]
            
            bitmaptools.blit(
                palettized_bitmap,
                self.source_bitmap,
                int(31-8+math.sin(self.wave+ang_step*i)*20), int(31-8+math.cos(self.wave+ang_step*i)*20),
                anim_data[SRC_X], anim_data[SRC_Y],
                anim_data[SRC_X]+anim_data[SRC_W], anim_data[SRC_Y]+anim_data[SRC_H], skip_source_index=0)
