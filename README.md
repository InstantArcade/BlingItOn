# Programming Your Own Generative Art Matrix

Welcome to the repository for our intermediate-level maker workshop! In this workshop, we explore the fundamentals of **generative algorithms** and apply them to create dynamic, data-driven visual art on a physical display. The repository is split into two separate implementation folders: one using **CircuitPython** and the other using **C++**.

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
