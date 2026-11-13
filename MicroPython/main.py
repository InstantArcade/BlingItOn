import time
import math
from random import randint, randrange
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X64
import picographics
import machine
import msa311
import re
import gc
import pngdec  #  For png decoding and display

# Wifi imports
import WIFI_CONFIG
# from network_manager import NetworkManager
import uasyncio
import urequests
from machine import Timer

# Preferences
vis_switch_seconds = 30
use_wifi = False
show_time = False
show_text = False
show_bg_img = False
bg_img_path = "png/dirk.png"
last_min = -1

fps_start = 0


# Time related imports
import time

# Realtime clock
local_rtc = machine.RTC()

# Consts
PI = const(3.1415926535)
PIx2 = const(PI*2.0)

# Setup for the display
i75 = Interstate75(
    display=DISPLAY_INTERSTATE75_64X64,
    stb_invert=False,
    panel_type=Interstate75.PANEL_GENERIC,
    pen_type=picographics.PEN_RGB888)

display = i75.display
WIDTH, HEIGHT = display.get_bounds()

png = pngdec.PNG(display)

if show_bg_img:
    try:
        png.open_file(bg_img_path)
    except Exception as e:
        print(f"Couldn't open image {e}")
    
# 
# matrix = i75.hub75 # access to the lower level matrix
# import hub75
# WIDTH=64
# HEIGHT=64
# matrix = hub75.Hub75(WIDTH,HEIGHT,stb_invert=False,panel_type=Interstate75.PANEL_GENERIC)
# matrix.start()


BLACK = display.create_pen(0,0,0)
WHITE = display.create_pen(255,255,255)
RED = display.create_pen(255,0,0)
GREEN = display.create_pen(0,255,0)
RETRO_AMBER = display.create_pen(0x77,0x33,0)

# Accelerometer stuff
sda = machine.Pin(20)
scl = machine.Pin(21)
i2c = machine.I2C(0,sda=sda,scl=scl,freq=40000)

# Uncomment to scan for i2c devices
#devices = i2c.scan()
# if len(devices) == 0:
#     print("No I2C Devices found!")
# else:
#     print( 'Devices found:', len(devices))
#     
#     for device in devices:
#         print("I2C Addr: ", hex(device) )
# 

# Accelerometer
accel = None
try:
    accel = msa311.MSA311(i2c,0x62)
except Exception as e:
    print(f"Couldn't connect to accelerometer {e}")

import network
import urequests

w_status = "? "
def do_connect():
    import machine, network
    global w_status
    wlan = network.WLAN()
    wlan.active(True)
    if not wlan.isconnected():
        print(f'Connecting to network {WIFI_CONFIG.SSID}...')
        wlan.connect( WIFI_CONFIG.SSID, WIFI_CONFIG.PASS )
        while not wlan.isconnected():
            stat = wlan.status()
            print( f"Status: {stat}" )
            # show progess on the matrix
            
            display.set_layer(0)
            display.set_pen(BLACK)
            display.clear()
            display.set_pen(WHITE)
            display.text(f"WIFI {w_status}", 15, 28, WIDTH, 1)
            if w_status == "? ":
                w_status = " ?"
            else:
                w_status = "? "
                
            i75.update()
            if stat == network.STAT_WRONG_PASSWORD:
                print("Wrong password, check credentials!")
                break
            time.sleep(0.5)
            
    if wlan.status() == network.STAT_GOT_IP:
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(GREEN)
        display.text(f"WIFI {wlan.ipconfig('addr4')[0]}", 0, 28, WIDTH, 1)
        i75.update()
        time.sleep(2)
    else:
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(RED)
        display.text(f"WIFI FAIL!", 10, 28, WIDTH, 1)
        i75.update()
        time.sleep(2)
        
    print('network config:', wlan.ipconfig('addr4'))

if use_wifi:
    do_connect()
    # Wifi Example gets the Los Angeles time from TimeAPI.io and updates the RTC
    try:
        print(f"Requesting the time")
        r = urequests.get("https://www.timeapi.io/api/timezone/zone?timeZone=America%2FLos_Angeles", timeout=2)
        if r.status_code == 200:
            print("Got time from API - Parsing")
            # open the json data
            j = r.json()
            timestring = j['currentLocalTime'] #  example: 2026-10-26T22:40:43.4899966
            m = re.match( "(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)",timestring )
            yr = int(m.group(1))
            mo = int(m.group(2))
            dy = int(m.group(3))
            hr = int(m.group(4))
            mi = int(m.group(5))
            se = int(m.group(6))
            wd = 0 #  API doesn't return weekday, so set it to 0 for now
            
            local_rtc.datetime((yr,mo,dy,wd,hr,mi,se,0))
            print( f"Updating local timesource to {yr}-{mo}-{dy} {hr}:{mi}:{se}" )
            
            r.close()
    except Exception as e:
        print(f"API check failed {e}")

# Visualizations
from VectorVis import VectorVis
from GridVis import GridVis
from BlinkenVis import BlinkenVis
from ConcentricVis import ConcentricVis
from ShapesVis import ShapesVis
from RippleVis import RippleVis

visualizations = [
    ShapesVis(WIDTH,HEIGHT),
    VectorVis(WIDTH,HEIGHT),
    GridVis(WIDTH,HEIGHT),
    BlinkenVis(WIDTH,HEIGHT),
    ConcentricVis(WIDTH,HEIGHT),
    RippleVis(WIDTH,HEIGHT),
]
for visualization in visualizations:
    visualization.reset()
vis_index = 0
vis = visualizations[vis_index]
vis_start = time.ticks_ms()

# It's possible to layer 2 (or more) visualizations, but it's at the cost of performance
vis2 = None
if vis2: # Reset the 2nd visualization if it has been declared
    vis2.reset() # IMPORTANT!

t_count = 0
t_total = 0
fps_start = 0

text_wave_y = 0
text_wave_x = 0
hue = 0

while 1:
    tstart = time.ticks_ms()
    if time.ticks_diff(tstart, vis_start) >= vis_switch_seconds * 1000:
        vis_index = (vis_index + 1) % len(visualizations)
        vis = visualizations[vis_index]
        vis_start = tstart
    gc.collect()
    delta = (tstart-fps_start)/1000
    fps_start = tstart

    if delta < 0 or delta > 1000: # first run, or ticks rolled over so avoid massive movements
        delta = 0.016
        
    display.set_pen(BLACK)
    if show_bg_img:
        display.clear()  # only need to clear if bg if png is not 64x64
        png.decode(0, 0)
    else:
        # Clear the screen
        display.clear()
        
#     display.set_font("bitmap14_outline")
    display.set_font("bitmap6")
    
    # read accelerometer
    acc = [0,0,0]
    if accel:
        acc = accel.read()

    vis.update( delta, display, acc )
    
    if vis2:
        vis2.update( delta, display, acc )

    # Set the layer we're going to be drawing to.
    display.set_layer(0)

    display.set_pen(WHITE)  #  RETRO_AMBER

    if show_text:
        # some movement for the text
        text_wave_y += PI*1.5*delta
        if text_wave_y > PIx2:
            text_wave_y -= PIx2

        text_wave_x += PI*0.5*delta
        if text_wave_x > PIx2:
            text_wave_x -= PIx2

        hue += delta*0.2
        if hue > 1.0:
            hue -= 1.0

        p = display.create_pen_hsv(hue,1,1)
        t = "SUPERCON 10"
        tw = int(display.measure_text(t,1))
        x = (32-tw//2) + int(math.cos(text_wave_x)*30)
        y = 54+int(math.sin(text_wave_y)*5)
    #    y = 55
        display.set_pen(BLACK)
        display.text(t, x+1, y+1, 200, 1)
        display.set_pen(p)
        display.text(t, x, y, 200, 1)
        
    # Check to see if we need to update the time
    dt = local_rtc.datetime()  # YYYY, MM, DD, ??, HH, MM, SS, DST?
    if show_time:
        time_text = f"{dt[4]}:{dt[5]:02}:{dt[6]:02}"
        xoff = 32 - int(display.measure_text(time_text,1))//2
        display.set_pen(BLACK)
        display.text(time_text, xoff+1,1,WIDTH,1)
        display.set_pen(WHITE)
        display.text(time_text, xoff,0,WIDTH,1)

    # Update the display
    i75.update()

    tfinish = time.ticks_ms()

    total = tfinish - tstart
    t_total += total
    t_count += 1

    if t_count == 60:
        per_frame_avg = t_total / t_count
        # Disable this print if not connected to a computer since it will cause
        # brief lockups otherwise
#         print(f"60 frames in {t_total}ms, avg {per_frame_avg:.02f}ms per frame, {1000 / per_frame_avg:.02f} FPS")
        t_count = 0
        t_total = 0

    # pause for a moment (important or the USB serial device will fail)
    # try to pace at 60fps or 30fps
    if total > 1000 / 30:
        time.sleep(0.0001)
    elif total > 1000 / 60:
        t = 1000 / 30 - total
        time.sleep(t / 1000)
    else:
        t = 1000 / 60 - total
        time.sleep(t / 1000)