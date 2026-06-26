# Programming Your Own Generative Art Matrix

Welcome to the repository for our intermediate-level maker workshop, originally presented at the **[2025 Hackaday Superconference](https://hackaday.com/2025/09/23/2025-hackaday-superconference-announcing-our-workshops-and-tickets/)**! In this workshop, we explore the fundamentals of **generative algorithms** and apply them to create dynamic, data-driven visual art on a physical display. The repository is split into two separate implementation folders: one using **CircuitPython** and the other using **C++**. ˇ

**[Join our discord!](https://discord.gg/dmBcJM6YX)**

## Hardware / Materials
The case for the LED matrix was designed for this 64x64 matrix:
* **Adafruit 64x64 RGB LED Matrix (2.0mm Pitch):** [Product Page (ID: 5362)](https://www.adafruit.com/product/5362)
  * *Specs:* 130 mm x 130 mm dimensions, high-density RGB LEDs.
* **Matrix Portal S3:** https://www.adafruit.com/product/5778

*Note: Depending on your microcontroller choice (e.g., ESP32, Raspberry Pi Pico, MatrixPortal), make sure you have the appropriate logic level shifters or a dedicated driver shield/wing as recommended by Adafruit.*

## Structure

```text
├── CPP/    # C++ / Arduino implementation source files 
└── CircuitPython/    # CircuitPython implementation scripts and libraries
└── case/ svg file to laser cut the custom case
```

## Optional CPP Enhancements
If you decide to use this project with Arduino/C++, Marc MERLIN has made a driver
for this CPU/Board/Display combo that allows you full framebuffer functionality 
along with Adafruit GFX, FastLED, and LEDMatrix API support.

Please refer to 
https://marc.merlins.org/perso/arduino/post_2026-01-05_FastLED-ESP32-HUB75-MatrixPanel-FrameBuffer-GFX.html
and
https://github.com/marcmerlin/FastLED_ESP32-HUB75-MatrixPanel_FrameBuffer_GFX

Video demo:
https://www.youtube.com/watch?v=1d6U-6twpCk
<img width="1134" height="769" alt="image" src="https://github.com/user-attachments/assets/5e2faa48-15d8-42f1-b7e3-bc08be29c866" />
