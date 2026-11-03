import time
import picographics
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X64
# Setup for the display
i75 = Interstate75(
    display=DISPLAY_INTERSTATE75_64X64,
    stb_invert=False,
    panel_type=Interstate75.PANEL_GENERIC,
    pen_type=picographics.PEN_RGB888)

display = i75.display
WIDTH, HEIGHT = display.get_bounds()

BLACK = display.create_pen(0,0,0)
WHITE = display.create_pen(255,255,255)
RED = display.create_pen(255,0,0)
GREEN = display.create_pen(0,255,0)
BLUE = display.create_pen(0,0,255)

while True:
    display.set_pen(RED)
    display.clear()
    i75.update()
    time.sleep(1)
    display.set_pen(GREEN)
    display.clear()
    i75.update()
    time.sleep(1)
    display.set_pen(BLUE)
    display.clear()
    i75.update()
    time.sleep(1)
    display.set_pen(WHITE)
    display.clear()
    i75.update()
    time.sleep(1)
    