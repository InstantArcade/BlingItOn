# Board related imports
import board # Infor about the board
import terminalio
import rgbmatrix # For controlling the RGB LED Panel
import framebufferio
import adafruit_lis3dh # Accelerometer
import busio
import digitalio

# Graphic imports
import adafruit_imageload
import displayio # General drawing tools
import bitmaptools # Faster drawing to bitmap helpers
from adafruit_display_text import label, outlined_label # Efficient text on bitmaps
from adafruit_bitmap_font import bitmap_font # Custom bitmap fonts (from FontForge BDF files)

# General imports
import math # general math helpers (sin/cos/etc)
from random import randrange # random numbers
import os

# Time related imports
import supervisor
import time
import adafruit_datetime
import rtc

# WiFi imports
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests

# The visualization imports
import BlinkenVis
import ConcentricVis
import CubeVis
import GravBallVis
import GridVis
import RainbowVis
import ShapesVis
import SpriteVis
import StarVis
import WaveVis
import WolframVis

PI = 3.1415926535
PIx2 = PI*2.0

WIDTH = 64
HEIGHT = 64

# Change demo every 3 seconds
demo_length_sec = 3

# Realtime clock
local_rtc = rtc.RTC()

# Hardware button setup
down_button = digitalio.DigitalInOut(board.BUTTON_DOWN)
down_button.direction = digitalio.Direction.INPUT
down_button.pull = digitalio.Pull.UP # Value False when button presed

up_button = digitalio.DigitalInOut(board.BUTTON_UP)
up_button.direction = digitalio.Direction.INPUT
up_button.pull = digitalio.Pull.UP # Value False when button presed

# Helper for centering a text_area
def center_text( text_area ):
    tabb = text_area.bounding_box
    print(f"centering text in bounding box {tabb}")
    text_area.x = 32-(max(tabb[0],tabb[2])-min(tabb[0],tabb[2]))//2
    half_height = (max(tabb[1],tabb[3])-min(tabb[1],tabb[3]))//2
    text_area.y = 5+half_height//2 # Might need to change this offset with different fonts
    print(f"New X {text_area.x}, Y {text_area.y}")
    return text_area

# I2C and Accelerometer setup
def rotate_accel( accel_data, degrees ): # Rotates accel data [x,y,z] list by rotation amount (fixed to 0,90,180,270)
    if degrees == 0:
        return accel_data
    if degrees == 180:
        return [accel_data.x, -accel_data.y, accel_data.z]
    if degrees == 90:
        return [accel_data.y, -accel_data.x, accel_data.z]
    else:
        return [-accel_data.x, accel_data.y, accel_data.z]
i2c = busio.I2C(board.SCL,board.SDA)
acc_int = digitalio.DigitalInOut(board.ACCELEROMETER_INTERRUPT)
accelerometer = adafruit_lis3dh.LIS3DH_I2C(i2c,address=0x19,int1=acc_int)
accelerometer.range = adafruit_lis3dh.RANGE_8_G
accelerometer.set_tap(2,60) # Tap detection

ACC_BUFFER_LEN = 120
acc_buffer = [] # Buffer for accelerometer data so we can detect shaking
acc_buffer_head = 0 # where in the buffer we are writing data
acc_buffer_tail = 0 # where the end of the data is (we set this to head when we've triggered
acc_buff_min_size = ACC_BUFFER_LEN//2 # we want a whole second of data before
# for i in range(0,ACC_BUFFER_LEN):
#     acc_buffer.append([0,0,0])

def reset_shake_buffer():
    global acc_buffer, acc_buffer_head, acc_buffer_tail
    acc_buffer = [] # Buffer for accelerometer data so we can detect shaking
    acc_buffer_head = 0 # where in the buffer we are writing data
    acc_buffer_tail = 0 # where the end of the data is (we set this to head when we've triggered
    for i in range(0,ACC_BUFFER_LEN):
        acc_buffer.append([0,0,0])
        
reset_shake_buffer()    

time_since_last_shake = 0

def shaken( threshold_g ):
    global acc_buffer_head, acc_buffer_tail, acc_buffer, acc_buff_min_size, time_since_last_shake
    
    EXTENT = 99999
    
    # difference between head and tail positions needs to be at least acc_buffer_min_size
    bdiff = 0
    
    if acc_buffer_head < acc_buffer_tail:
        bdiff = acc_buffer_head+ACC_BUFFER_LEN - acc_buffer_tail
    else:
        bdiff = acc_buffer_head - acc_buffer_tail

    if bdiff < acc_buff_min_size:
        return False # not enough data so no shake
    
    xmin = EXTENT
    xmax = -EXTENT
    ymin = EXTENT
    ymax = -EXTENT
    zmin = EXTENT
    zmax = -EXTENT
    # go through buffer and detect min/max in all directions
    t = acc_buffer_tail
    while t != acc_buffer_head:
        a = acc_buffer[t]
        
        if a[0] < xmin:
            xmin = a[0]
        elif a[0] > xmax:
            xmax = a[0]
            
        if a[1] < ymin:
            ymin = a[1]
        elif a[1] > ymax:
            ymax = a[1]
            
        if a[2] < zmin:
            zmin = a[2]
        elif a[2] > zmax:
            zmax = a[2]
            
        t += 1
        t %= ACC_BUFFER_LEN
    
    xt = False
    yt = False
    zt = False
    if xmax-xmin > threshold_g:
        xt = True
    if ymax-ymin > threshold_g:
        yt = True
    if zmax-zmin > threshold_g:
        zt = True

    if (xt and yt) or (xt and zt) or (yt and zt) and time_since_last_shake > 3.0:
        print(f" Thresh {threshold_g} - X {xmin},{xmax} {xmax-xmin}- Y {ymin},{ymax} {ymax-ymin} - Z {zmin},{zmax} {zmax-zmin} - Head {acc_buffer_head}, Tail {acc_buffer_tail}")
        reset_shake_buffer()
        return True
        
    return False

def update_shake( accel, delta ):
    global acc_buffer_head, acc_buffer_tail, acc_buffer, time_since_last_shake
    
    time_since_last_shake += delta
    
    acc_buffer[acc_buffer_head] = accel
    #increment pointer(s)
    acc_buffer_head += 1
    
    if acc_buffer_head == acc_buffer_tail:
        acc_buffer_tail += 1
    
    acc_buffer_head %= ACC_BUFFER_LEN
    acc_buffer_tail %= ACC_BUFFER_LEN


# --- Display Setup --- #
displayio.release_displays()
# RGB Matrix initialization
matrix = rgbmatrix.RGBMatrix(
    width=WIDTH, height=HEIGHT, bit_depth=5,
    rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1,
              board.MTX_R2, board.MTX_G2, board.MTX_B2],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC,
               board.MTX_ADDRD, board.MTX_ADDRE],
    clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT, output_enable_pin=board.MTX_OE,
    doublebuffer=False)

display = framebufferio.FramebufferDisplay(matrix,auto_refresh=False, rotation=90) # Rotate 90 degrees so PCB pokes out of the top
display.brightness = 1 # Current implementation is 0 = off anything non-zero value = full brightness
# don't display code.py on the RGBPanel display
main_group = displayio.Group()
display.root_group = main_group 
display.refresh() 


# Main "Full color" bitmap we use for drawing onto
bitmap = displayio.Bitmap(WIDTH,HEIGHT,65535)
cc = displayio.ColorConverter(input_colorspace=displayio.Colorspace.RGB565)
tg1 = displayio.TileGrid(bitmap,pixel_shader=cc)
g1 = displayio.Group(scale=1)
g1.append(tg1)

# Default palette for sprite mode - may get overwritten in special initialization
palette = displayio.Palette(256)
palette[0] = 0x0
palette[1] = 0xf80000
palette[2] = 0xf8f8f8
palette[3] = 0xf8
palette[4] = 0xf8f8
palette[5] = 0xf8c8e0
palette[6] = 0xf89800
palette[7] = 0xf8f800
palette[8] = 0x983800
palette[9] = 0xf800
palette[10] = 0xf8e0c0
palette[11] = 0xf8e860
palette[12] = 0xffff80
palette[13] = 0xff0000
palette[14] = 0xf8e0f8
palette.make_transparent(0)

# Palettized bitmap layer for sprite mode - in front of regular bitmap layer
palettized_bitmap = displayio.Bitmap(WIDTH,HEIGHT,256)
tg2 = displayio.TileGrid(palettized_bitmap,pixel_shader=palette)
#g1.append(tg2) # Comment this line out if not using this layer (for faster updates)

# Text area on its own layer
text = "BLING\nIT ON"
font = bitmap_font.load_font("/ArcadeNormal-8.bdf")

color = 0x773300#0xFF7777#0xe5d8#0x3fe0
text_area = outlined_label.OutlinedLabel(font, text=text, color=color, outline_color=0) #Takes RGB888 as color
center_text(text_area)
g1.append(text_area)

# Set root display object
display.root_group = g1
display.refresh()

# Perfomance tracking
fps_sum = 0
fps_samples = 0
fps_start = -1
time_ticks = 0
last_print_time = 0
last_fps = 0

vis_ctr = 0

# Pick the visualization(s)
vis_list = [
    BlinkenVis.BlinkenVis(WIDTH,HEIGHT), # Blinkenlights suarees
    ConcentricVis.ConcentricVis(WIDTH,HEIGHT),  # Concentric circles that move around
    CubeVis.CubeVis(WIDTH,HEIGHT),  # rotating 3D bob
    GravBallVis.GravBallVis(WIDTH,HEIGHT), 
    GridVis.GridVis(WIDTH,HEIGHT),  # Depth grid that moves based on accelerometer
    RainbowVis.RainbowVis(WIDTH,HEIGHT), # moving color lines 
    ShapesVis.ShapesVis(WIDTH,HEIGHT),  # moving bubbles that change size
    #SpriteVis.SpriteVis(WIDTH,HEIGHT), # more complex demo that needs some integration
    StarVis.StarVis(WIDTH,HEIGHT), # starfield
    #WaveVis.WaveVis(WIDTH,HEIGHT), # non working half green screen FIXME
    #WolframVis.WolframVis(WIDTH,HEIGHT), 
]
vis = vis_list[vis_ctr]
vis2 = None

vis.reset() # IMPORTANT!

# It's possible to layer 2 (or more) visualizations, but it's at the cost of performance
if vis2: # Reset the 2nd visualization if it has been declared
    vis2.reset() # IMPORTANT!

# Special visualization initialization
if isinstance(vis, SpriteVis.SpriteVis):
    # In this case the visualization loaded a bitmap and we need to copy the loaded palette back to our sprite layer
     vis.source_palette.make_transparent(0)
     tg2.pixel_shader = vis.source_palette
     print("Loaded palette for SpriteVis")

ang = 0 # for text movement

# We want to control when the screen updates
display.auto_refresh = False
display.refresh()

use_wifi = False

if use_wifi:
    # Get connected to the internet!
    print(f"My MAC address: {[hex(i) for i in wifi.radio.mac_address]}") # show our MAC

    # Show which WiFi networks we can see (comment this back in to survey the wifi in your area)
    # wifi.radio.stop_scanning_networks()
    # for network in wifi.radio.start_scanning_networks():
    #     print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
    #                                              network.rssi, network.channel))
    # wifi.radio.stop_scanning_networks() # stop scanning

    # Connect the specified access point in the TOML file
    print( f"WiFi Connecting to {os.getenv("CIRCUITPY_WIFI_SSID")}" )
    try:
        wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"),os.getenv("CIRCUITPY_WIFI_PASSWORD"))
    except Exception as e:
        print(f"Could not connect to {os.getenv("CIRCUITPY_WIFI_SSID")}" )
        
    # Set up objects so we can do Web API requests
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())

    # Grab the current time via the timeapi.io API (set a timeout so we don't wait forever)
    print( f"CircuitPython thinks the time/date is {adafruit_datetime.datetime.today()}\nGetting time from API" )
    try:
        response = requests.request("GET", "https://www.timeapi.io/api/timezone/zone?timeZone=America%2FLos_Angeles", timeout=2 )
        """ example response
        {
          "timeZone": "America/Los_Angeles",
          "currentLocalTime": "2025-08-18T17:15:28.519488",
          ...
        }
          """
        if response.status_code == 200:
            print("Got time from API - Parsing")
            # parse the JSON
        #    print( f"Response was:\n{response.json()}" )
            timestring = response.json()['currentLocalTime']
            # knock off the fractional seconds to prevent exceptions in the parser
            timestring = timestring.split('.')[0]
            local_rtc.datetime = adafruit_datetime.datetime.fromisoformat(timestring).timetuple() # Convert to actual datetime object and set the controller's time
            print( f"Updating local timesource to {timestring}" )
        else:
            print("Get response was {response}")
    except Exception as e:
        print(f"API check failed {e}")

show_time = False

if show_time:
    # Set the text on the text layer to the current time
    text_area.text = "* " + f"{local_rtc.datetime.tm_hour}:{local_rtc.datetime.tm_min:02} *\n\n" + "> 2025 <\nHACKADAY\nSUPERCON"
else:
    # this hangs 1-2sec, very slow lib?
    text_area.text = "* Marc *\n MERLIN \n\n> 2025 <\nHACKADAY\nSUPERCON"
#     text_area.text = "SUPERCON"
    
center_text(text_area)

last_min = local_rtc.datetime.tm_min # save current minute for update
last_down = False # Track down button previous state
last_up = False # Track up button previous state

display.auto_refresh = False # We want to control the display update
# Main Loop
while True:
    display.refresh() # Force the display to output what's on the current bitmap
    bitmap.fill(0) # clear the bitmap for next time around the loop

    # Timing stuff for FPS calculations and propotional updates
    ticks = supervisor.ticks_ms()
    delta = (ticks-fps_start)/1000
    fps_start = ticks

    if delta < 0 or delta > 1000: # first run, or ticks rolled over so avoid massive movements
        delta = 0.016

    # read accelerometer - Note: With Displaybuffer rotatated so that up has the MatrixPortal sticking out
    # of the top, then X and Y are swapped. e.g. Upright with have X at around -9
    #[adc_raw_x,adc_raw_y,adc_raw_z]
    acc = rotate_accel(accelerometer.acceleration,90)

    update_shake( acc, delta )

# Enable for tap detection
#     if accelerometer.tapped:
#         print("We got tapped!!!!")
#         vis.reset()
        
    if shaken(30):	# Display was shaken beyond the threshold
        print( f"{Eightball.EightBall().get_random_saying()}")
        time.sleep(1)

    # check buttons
    if not down_button.value and last_down: # Button pressed since last time
        time.sleep(0.25) # cheesy addition debounce
        vis.reset()
        if vis2:
            vs2.reset()
            
    if not up_button.value and last_up: # Button pressed since last time
        pass

    last_down = down_button.value
    last_up = up_button.value

    # Update the visualization(s)
    if isinstance(vis, SpriteVis.SpriteVis): # special render step
        vis.update( delta, bitmap, palettized_bitmap, acc )
    else:
        vis.update( delta, bitmap, acc )
        
    if vis2:
#         if isinstance(vis2, SpriteVis.SpriteVis): # special render step
#             vis2.update( delta, bitmap, palettized_bitmap, acc )
#         else:
        vis2.update( delta, bitmap, acc )
        
# Moving text effect
    text_area.y = int(14 + math.sin(ang)* 10)
    ang += 0.11
    if ang > PIx2:
        ang -= PIx2

    # Check to see if we need to update the time
    if local_rtc.datetime.tm_min != last_min and show_time:
        text_area.text = "* " + f"{local_rtc.datetime.tm_hour}:{local_rtc.datetime.tm_min:02} *\n\n" + "> 2025 <\nHACKADAY\nSUPERCON"
        text_area.x = 32-text_area.width//2 # re-center
        #save current minute for update
        last_min = local_rtc.datetime.tm_min

    fps_sum += 1; # Increment the number of frames

    # If more than a second has elapsed, show the Frames Per Second and reset the counters
    if ticks - last_print_time > 1000:
        time_ticks += 1
        # change demo very few seconds
        if time_ticks % demo_length_sec == 0:
            vis_ctr += 1
            demo = vis_ctr % len(vis_list)
            print("Switching to demo %d" % demo)
            vis = vis_list[demo]
            vis.reset() # IMPORTANT!

#         print( f"Average FPS {fps_sum} - delta {delta} # ADC {acc}`")
        color = 0xffff
        last_fps = fps_sum
        fps_sum = 0
        last_print_time = ticks
#     bitmaptools.draw_line(bitmap,0,63,min(last_fps,63),63,color) # Draw a line to show approx FPS

