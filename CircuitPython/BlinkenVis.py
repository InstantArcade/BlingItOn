import bitmaptools
from random import randrange, random, uniform
import math
from hsv565 import HSV565

# math helpers
PI = 3.1415926535
PIx2 = PI*2.0

blinken_speed = 1 # overall speed multiplier
blinken_block_size = 8 # Size of block (8x8)

hsv = HSV565()

palette = [] 			# To store the pre-caclucated colors and brightness variations
fade_levels = 32 		# Number of brightness variations for each color
color_variations = 15 	# Number of different colors

class BlinkenBlock:
    x = 0 # Pixel positions of this block
    y = 0
    brightness_wave = 0
    speed_mul = 1
    palette_index = 0
    
    def __init__(self,x,y):
        self.x = x
        self.y = y
        
    def reset( self ):
        self.brightness_wave = random()*PIx2
        self.speed_mul = 0.8 + random()*0.4
        self.palette_index = randrange(0,color_variations)
        
        
    def move(self, delta):
        self.brightness_wave += delta * PIx2 * blinken_speed * self.speed_mul # Update the controlling wave
        if self.brightness_wave > PIx2: # Reset speed and wave once we've completed the cycle
            self.brightness_wave = 0
            self.speed_mul = 0.8 + random()*0.4
            
    def render(self, bitmap):
        x = self.x*blinken_block_size
        y = self.y*blinken_block_size
        x2 = x + blinken_block_size-1 # -1 on the width & height so we have a grid bwteeen the blocks
        y2 = y + blinken_block_size-1
        bright = math.sin(self.brightness_wave)*0.5+0.5 # Convert brightness wave to a 0-1 value
        fade_offset = int((fade_levels-1)*bright) # Caclulatte the closes brightness offset 
        if bright < 0.01: # have we faded out completely
            self.palette_index = randrange(0,color_variations) # pick a new color
        bitmaptools.fill_region(bitmap,
                                x,y,x2,y2,
                                palette[self.palette_index][fade_offset])
                                
class BlinkenVis:
    visWidth = 64
    visHeight = 64
    all_blocks=[] # Holds all the individual block objects
        
    def __init__(self,WIDTH,HEIGHT):
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        print( f"BlinkenVis initialized - Width {WIDTH}, Height {HEIGHT}")

    def reset( self ):
        # generate a palette with fades
        global palette
        palette = [] # Clear any existing palette
        fade_step = 1.0/fade_levels # Brightness diffence between brightness variations
        
        
        # Use cv_step and cv_offset to control the color start point and range of hues
        # e.g. step = 35, offset = 235 will select blue tones
        # step = 35, offset = 95 will be greens/yellows
        # step =360, offset = 0 wil be all colors
        # experiment with these settings
        cv_step = 360//color_variations # Range up/down from offset point in the hue table
#         cv_step = 360//color_variations # Include all the colors
        #   0 = Red
        #  25 = Orange
        #  55 = Yellow
        #  75 = Lime Green
        # 110 = Green
        # 155 = Aquamarine
        # 195 = Cyan
        # 230 = Blue
        # 280 = Magenta
        # 305 = Pink
        # 359 = Red
        cv_offset = 0 - (color_variations*cv_step)//2 # Start on low side of range
        saturation = 1 # range 0 to 1,  set this value lower to reduce the color strength (make it whiter) - 1 is full saturation
        for i in range(0,color_variations):
            cv = []
            for j in range(0,fade_levels):
                cv.append( hsv.hsv2rgb565((cv_offset + i*cv_step)%360, saturation, j*fade_step) )
            palette.append(cv)
                
        self.all_blocks=[]
        # initialize all the blocks
        nx = self.visWidth//blinken_block_size
        ny = self.visWidth//blinken_block_size
        for y in range(ny):
            for x in range(nx):
                b = BlinkenBlock(x,y)
                b.reset()
                self.all_blocks.append( b )
    
    def update( self, delta, bitmap, accel ):
        for i in self.all_blocks:
            i.move( delta )
            i.render( bitmap )
