#include <Arduino.h>
#include <Adafruit_LIS3DH.h>      // For accelerometer
#include <Adafruit_Protomatter.h> // For RGB matrix

#include <WiFi.h>
char ssid[] = "YOUR_SSID";             // your network SSID (name)
char pass[] = "YOUR_SSID_PASSWORD";    // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;
WiFiClient client;

Adafruit_LIS3DH accel = Adafruit_LIS3DH();

uint8_t rgbPins[]  = {42, 41, 40, 38, 39, 37};
uint8_t addrPins[] = {45, 36, 48, 35, 21};
uint8_t clockPin   = 2;
uint8_t latchPin   = 47;
uint8_t oePin      = 14;

#define WIDTH   64 // Matrix width (pixels)
#define HEIGHT   64 // Matrix height (pixels)
#define NUM_ADDR_PINS 5

#include "helpers.h"
#include "Visualization.h"
#include "VisConcentricCircles.h"
#include "VisCirclePacker.h"
#include "VisSnow.h"


Adafruit_Protomatter thematrix(
  WIDTH, 4, 1, rgbPins, NUM_ADDR_PINS, addrPins,
  clockPin, latchPin, oePin, true);

Adafruit_Protomatter *matrix = &thematrix;
float wave = 0;

Visualization *pVis = nullptr;

float globalGamma = PANEL_GAMMA;

void setup() 
{
  Serial.begin(115200);

  generateHSVTable(); // create the HSV colors or they will all be black

  ProtomatterStatus status = thematrix.begin();

  thematrix.fillScreen(0);
  thematrix.print("Hello");
  thematrix.show();

  delay(100); // give the board a little time to get the accelerometer ready

  if (!accel.begin(0x19)) {
    Serial.println("Couldn't find accelerometer");
    thematrix.setCursor(0,10);
    thematrix.print("Accel err!");
    thematrix.show();
    while(1);
  }
  accel.setRange(LIS3DH_RANGE_4_G);   // 2, 4, 8 or 16 G!
/*
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print("."); this is a test OK .oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.
  }

  Serial.println("");
  Serial.println("Connected to WiFi");
  //printWifiStatus();
*/

  // pVis = new VisConcentricCircles();
  // pVis = new VisCirclePacker();
  pVis = new VisSnow();
  pVis->init();

}

// FPS Tracking
int lastTicks = 0;
int fpsavg[5]={0};
float fPTimer = 0;
int fpIndex = 0;

void loop() 
{
  int iNow = millis();
  float delta = (iNow-lastTicks)/1000.0f;
  lastTicks = iNow;

  // Track and display Frames per Second
  int fps = 1.0f/delta;
  fpsavg[fpIndex++] = fps;
  fpIndex %= 5;

  fPTimer += delta;
  if( fPTimer > 1.0f )
  {
    fPTimer -= 1.0f;
    float ff = (fpsavg[0]+fpsavg[1]+fpsavg[2]+fpsavg[3]+fpsavg[4])/5.0f;
    printf("%0.2f FPS\n",ff);
  }

  wave += 0.03f;

  if( wave > PI*2.0f)
    wave -= PI*2.0f;

  // Read accelerometer...
  sensors_event_t event;
  accel.getEvent( &event );
  // copy it to global accel value
  global_accelerometer = event;

  // Serial.printf("(%0.1f, %0.1f, %0.1f)\n", event.acceleration.x, event.acceleration.y, event.acceleration.z);

  float diameter = 30.0f;
  float step = 0.62f;
  
  thematrix.fillScreen(0);
  // thematrix.drawPixel(32 + sinf(wave)        * diameter, 32 + cosf(wave)          * diameter, thematrix.color565(255,64,64) );
  // thematrix.drawPixel(32 + sinf(wave+step*1) * diameter, 32 + cosf((wave+step*1)) * diameter, thematrix.color565(255,0,0) );
  // thematrix.drawPixel(32 + sinf(wave+step*2) * diameter, 32 + cosf((wave+step*2)) * diameter, thematrix.color565(0,255,0) );
  // thematrix.drawPixel(32 + sinf(wave+step*3) * diameter, 32 + cosf((wave+step*3)) * diameter, thematrix.color565(0,0,255) );
  pVis->update(delta);
  // matrix->drawPixel(32,32,matrix->color565(255,255,255));
  thematrix.show();
}
