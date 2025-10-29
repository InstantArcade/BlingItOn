#include "VisConcentricCircles.h"
#include "helpers.h"

class CCircle
{
public:
  float x, y, numRings, startRadius, stepRadius;
  int hue;
  float ax, ay, sx, sy;
  float radiusOffset;
  
  void move( float delta )
  {
    ax += delta * sx * 9.0f;
    ay += delta * sy * 9.0f;
  }
  
  void draw()
  {
    int hueOffset = 0;
    int x2, y2; 
    int xt = PANEL_RES_X/2 + sinf(ax)*16.0f;
    int yt = PANEL_RES_Y/2 + cosf(ay)*16.0f;
    uint8_t r = HSVColors[((hue+hueOffset)%360)*3+0];
    uint8_t g = HSVColors[((hue+hueOffset)%360)*3+1];
    uint8_t b = HSVColors[((hue+hueOffset)%360)*3+2];
    int col = matrix->color565(r,g,b);
    for( int i=0; i < numRings; i++ )
    {
      // draw a circle at the current radius
      float r = startRadius + radiusOffset + i*stepRadius;
      BresenhamsCircle(xt,yt,(int)r,col);
    }
  }
 };

int CR_RADIUS = 1;
int CR_STEPS = 4;
int CR_NUM_RINGS = 7;

/*
int CModes[] = {
  CR_RADIUS,
  CR_STEPS,
  CR_NUM_RINGS,
  CR_RADIUS | CR_STEPS,
  CR_RADIUS | CR_NUM_RINGS,
  CR_STEPS | CR_NUM_RINGS,
  CR_RADIUS | CR_NUM_RINGS | CR_STEPS,
};
*/
const int MAX_CCIRCLES = 3;
int MAX_CRINGS = 8; //6

CCircle allCircles[MAX_CCIRCLES];
int ActualNumCircles = MAX_CCIRCLES;

void resetCCircles()
{
  int iHueShift = (int)random(255);
  
  ActualNumCircles = 3;
  
  for( int i = 0; i < ActualNumCircles; i++ )
  {
    allCircles[i].x = PANEL_RES_X/2;
    allCircles[i].y = PANEL_RES_Y/2;

    allCircles[i].numRings = MAX_CRINGS;
     
    allCircles[i].startRadius = 5;
    allCircles[i].stepRadius = 7;
    
    int iHue = int((((360.0f/ActualNumCircles)*i)+iHueShift))%360;
    
    allCircles[i].hue = iHue;
    
    allCircles[i].ax = 0;
    allCircles[i].ay = 0;
    allCircles[i].sx = 0.3f + random(5)/10.0f;
    allCircles[i].sy = 0.3f + random(5)/10.0f;
    if( random(100) < 50 ) allCircles[i].sx *= -1;
    if( random(100) < 50 ) allCircles[i].sy *= -1;
    
    allCircles[i].radiusOffset = 0;
  }
}

void VisConcentricCircles::init()
{
    resetCCircles();
}

void VisConcentricCircles::update( float delta )
{
  for( int iC = 0; iC < ActualNumCircles; iC++ )
  {
    allCircles[iC].move(delta);
    allCircles[iC].draw();
  }

}