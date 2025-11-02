import time
import board
import terminalio
import displayio
import bitmaptools
import supervisor
import rgbmatrix
import framebufferio

WIDTH = 64
HEIGHT = 64

displayio.release_displays()

# --- Display Setup --- #
#RGB order
matrix = rgbmatrix.RGBMatrix(
    width=WIDTH, height=HEIGHT, bit_depth=6,
    rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1,
              board.MTX_R2, board.MTX_G2, board.MTX_B2],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC,
               board.MTX_ADDRD, board.MTX_ADDRE],
    clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT, output_enable_pin=board.MTX_OE,
    doublebuffer=False)

display = framebufferio.FramebufferDisplay(matrix,auto_refresh=True)

bitmap = displayio.Bitmap(WIDTH,HEIGHT,65535)
cc = displayio.ColorConverter(input_colorspace=displayio.Colorspace.RGB565)
tg1 = displayio.TileGrid(bitmap,pixel_shader=cc)
g1 = displayio.Group(scale=1)
g1.append(tg1)
display.root_group = g1


fps_sum = 0
fps_samples = 0
fps_start = -1
last_print_time = 0

display.auto_refresh = True

while True:
    ticks = supervisor.ticks_ms()
    delta = (ticks-fps_start)/1000
    fps_start = ticks
    
    if delta < 0 or delta > 1000: # first run, or ticks rolled over
        continue

    xs = bytes([4, 63, 33, 19])
    ys = bytes([4, 19,  55, 17])
    bitmaptools.draw_polygon(bitmap,xs,ys,15300)

    bitmap.fill(0) # ~239 FPS for this alone
    fps_sum += 1;
    
    if ticks - last_print_time > 1000:
        print( f"Average FPS {fps_sum} - delta {delta}")
        fps_sum = 0
        last_print_time = ticks
    
