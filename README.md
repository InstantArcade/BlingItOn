# Programming Your Own Generative Art Matrix

Welcome to the repository for our intermediate-level maker workshop, originally presented at the **[2025 Hackaday Superconference](https://hackaday.com/2025/09/23/2025-hackaday-superconference-announcing-our-workshops-and-tickets/)**! In this workshop, we explore the fundamentals of **generative algorithms** and apply them to create dynamic, data-driven visual art on a physical display. The repository is split into separate implementation folders: one using **CircuitPython** and and one using **C++** on the Adafruit Matrix Portal S3, and for 2026 an implementation in **MicroPython** on the Pimoroni Interstate 75W. ˇ

**[Join our discord!](https://discord.gg/EVwvhfPvVR)**

## Hardware / Materials
The case for the LED matrix was designed for this 64x64 matrix:
* **Adafruit 64x64 RGB LED Matrix (2.0mm Pitch):** [Product Page (ID: 5362)](https://www.adafruit.com/product/5362)
  * *Specs:* 130 mm x 130 mm dimensions, high-density RGB LEDs.
* **Matrix Portal S3:** https://www.adafruit.com/product/5778
* or **Pimoroni Interstate75W:** https://shop.pimoroni.com/en-us/products/interstate-75-w?variant=54977948713339

*Note: Depending on your microcontroller choice (e.g., ESP32, Raspberry Pi Pico), make sure you have the appropriate logic level shifters or a dedicated driver shield/wing as recommended by Adafruit. (MatrixPortal and Interstate 75W have these built in)*

*Note: The MatrixPortal S3 has an onboard accelerometer, but for other boards, you'll need to add one for visualizations that use it. e.g. https://shop.pimoroni.com/en-us/products/adafruit-msa311-triple-axis-accelerometer-stemma-qt-qwiic?variant=39605361508435*

## Structure

```text
├── CPP/    # C++ / Arduino implementation source files (Adafruit Matrix Portal S3 board only for now)
└── CircuitPython/    # CircuitPython implementation scripts and libraries for the Adafruit Matrix Portal S3 board
└── MicroPython/    # MicroPython implementation scripts and libraries for the Pimironi Interstate 75W board
└── Case/    # svg and dxf files to laser cut the custom case
└──Tools/i75    # uf2 files to install MicroPython on the i75 and a nuke file to clear the i75 flash if all goes wrong (you'll lose everything on the board)
```

## Tools
For the Vector visualizer, you can load a shape from a list of verts.
We've provided a simple vector shape editor here - https://instantarcade.github.io/ShapeEditor/
Copy the vert data and paste it into a new python file inside the ```shapes``` folder, then import it by importing it with
```from shapes import myshape``` and then use ```load_shape( myshape.verts )``` to load the shape (and remove/replace any existing verts)

## Optional CPP Enhancements
If you decide to use this project with Arduino/C++, Marc MERLIN has made a driver
for this CPU/Board/Display combo (Matrixportal Board only) that allows you full framebuffer functionality 
along with Adafruit GFX, FastLED, and LEDMatrix API support.

Please refer to 
https://marc.merlins.org/perso/arduino/post_2026-01-05_FastLED-ESP32-HUB75-MatrixPanel-FrameBuffer-GFX.html
and
https://github.com/marcmerlin/FastLED_ESP32-HUB75-MatrixPanel_FrameBuffer_GFX

Video demo:
https://www.youtube.com/watch?v=1d6U-6twpCk
<img width="1134" height="769" alt="image" src="https://github.com/user-attachments/assets/5e2faa48-15d8-42f1-b7e3-bc08be29c866" />
