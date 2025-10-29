#pragma once

#include <arduino.h>
#include <Adafruit_Protomatter.h> // For RGB matrix
#include <Adafruit_LIS3DH.h>      // For accelerometer

#define PANEL_RES_X 64 // Number of pixels wide of each INDIVIDUAL panel module. 
#define PANEL_RES_Y 64 // Number of pixels tall of each INDIVIDUAL panel module.

// #define HALF_PI (1.570796325f)

#ifdef COLOR_ORDER_BGR
  #define RGBPixel(x,y,r,g,b) drawPixelRGB888(x,y,b,g,r)
  #define ColorInt(r,g,b) color565(b,g,r)
#elif defined(COLOR_ORDER_RBG)
  #define RGBPixel(x,y,r,g,b) drawPixelRGB888(x,y,r,b,g)
  #define ColorInt(r,g,b) color565(r,b,g)
#else
  #define RGBPixel(x,y,r,g,b) drawPixel(x,y,matrix->color565(r,g,b))
  #define ColorInt(r,g,b) color565(r,g,b)
#endif

// #define FLIP_BUFFER matrix->flipDMABuffer();
//extern MatrixPanel_I2S_DMA *matrix;
extern Adafruit_Protomatter *matrix;


#define Z_INFINITY (99999.99f)
extern bool cycleHue;

#define PANEL_GAMMA (1.1f)
// #define PANEL_GAMMA (1.2f)
extern float globalGamma;

extern float rMult;
extern float gMult;
extern float bMult;


void drawRippedSprite(int x, int y, const int *planeOffsets, const int *frameOffsets, const byte* dataSrc, byte frame, uint16_t color_override );
void drawRippedSpriteWithMask(int x, int y, const int *planeOffsets, const int *frameOffsets, const byte* dataSrc, byte frame, uint16_t color_override, uint16_t mask_color );

int inline imin(int a, int b, int c)
{
  if( a <= b && a <= c ) return a;
  if( b <= a && b <= c ) return b;
  return c;
}

int inline imax(int a, int b, int c)
{
  if( a >= b && a >= c ) return a;
  if( b >= a && b >= c ) return b;
  return c;
}

class vector3 
{
public:
  // union
  // {
    float x,y,z;
  //   float r,g,b;
  // };

  vector3() { x = 0; y = 0; z = 0; }
  vector3(float x_, float y_, float z_){ x=x_; y=y_; z=z_; }
  vector3 operator-(const vector3 &rhs)
  {
    vector3 result;
    result.x = x - rhs.x;
    result.y = y - rhs.y;
    result.z = z - rhs.z;
    return vector3(result.x,result.y,result.z);
  }

  vector3 operator+(const vector3 &rhs)
  {
    vector3 result;
    result.x = x + rhs.x;
    result.y = y + rhs.y;
    result.z = z + rhs.z;
    return vector3(result.x,result.y,result.z);
  }

  void operator+=(const vector3 &rhs)
  {
    x += rhs.x;
    y += rhs.y;
    z += rhs.z;
  }

  void operator-=(const vector3 &rhs)
  {
    x -= rhs.x;
    y -= rhs.y;
    z -= rhs.z;
  }

  vector3 operator*(const vector3 &rhs)
  {
    vector3 result;
    result.x = x * rhs.x;
    result.y = y * rhs.y;
    result.z = z * rhs.z;
    return vector3(result.x,result.y,result.z);
  }

  vector3 operator*(const float f)
  {
    vector3 result;
    result.x = x * f;
    result.y = y * f;
    result.z = z * f;
    return vector3(result.x,result.y,result.z);
  }
};

const float PI2 = PI*2.0f;
inline void constrainPI2( float &rfVal ){ while(rfVal>PI2){rfVal-=PI2;} while(rfVal<-PI2){rfVal+=PI2;} } 
inline void constrainPI2( vector3 &rVec ){ while(rVec.x>PI2){rVec.x-=PI2;} while(rVec.x<-PI2){rVec.x+=PI2;} while(rVec.y>PI2){rVec.y-=PI2;} while(rVec.y<-PI2){rVec.y+=PI2;} while(rVec.z>PI2){rVec.z-=PI2;} while(rVec.z<-PI2){rVec.z+=PI2;}} 

// inline void constrainPI2( float &rfVal )
// {
//     while( rfVal > PI2 )
//     {
//         rfVal-=PI2;
        
//     }
//     while( rfVal <= PI2 )
//     {
//         rfVal+=PI2;
//     }
// }

inline float sqrt3( float x)  // fast sqrt approximation
{
  union
  {
    int i;
    float x;
  } u;
  
  u.x = x;
  u.i = (1<<29) + (u.i >> 1) - (1<<22);
  return u.x;
}

typedef struct {
    float r;       // a fraction between 0 and 1
    float g;       // a fraction between 0 and 1
    float b;       // a fraction between 0 and 1
} rgb;

typedef struct {
    float h;       // angle in degrees
    float s;       // a fraction between 0 and 1
    float v;       // a fraction between 0 and 1
} hsv;

struct colorbits565 {
    uint16_t r : 5;
    uint16_t g : 6;
    uint16_t b : 5;
};

union colorunion{
    uint16_t rawcolor;
    struct colorbits565 components;
};

hsv rgb2hsv(rgb in);
rgb hsv2rgb(hsv in);

extern byte HSVColors[360*3];
extern uint16_t HSV565[360];

extern byte shadedBall2[];
extern byte shadedBall3[];
extern byte spinning_ring[];
extern int hueOffset;
extern byte ringMaxVal;
extern byte ringMinVal;


extern float fFocal;
extern float fXRot, fYRot, fZRot;
extern float fXRotSpeed, fYRotSpeed, fZRotSpeed;
extern sensors_event_t global_accelerometer;

float v3_dot_product( vector3 u, vector3 v );
vector3 normalize( vector3 &v );

void handleColorBars( float );
void generateHSVTable();
void cycleTheHue( float );

void initNoise(void);
double noise(double x, double y, double z);

void clearZBuffer();
void make_counter_clockwise(int& x1, int& y1, int& x2, int& y2, int& x3, int& y3);
void halfspace_triangle(int x1, int y1, int x2, int y2, int x3, int y3, byte r, byte g, byte b);
void halfspace_triangle_v(vector3 v1, vector3 v2, vector3 v3, byte r, byte g, byte b);
void halfspace_triangle_lerp(vector3 v1, vector3 v2, vector3 v3, vector3 c1, vector3 c2, vector3 c3);
void BresenhamLine( int x0, int y0, int x1, int y1, byte r, byte g, byte b );
void BresenhamsCircle( int x0, int y0, int radius, int color );

uint16_t rgbto565Gamma( float r, float g, float b, float gamma);
uint16_t rgbto565Gamma( byte r, byte g, byte b, float gamma);

struct VISOPTION
{
  // Visualization *pVis;
  bool showTime;    // default is true
  bool cornerTime;  // default is false
  bool clearScreen; // default is true

  VISOPTION( bool st, bool ct, bool cs )
  {
    showTime = st; cornerTime = ct; clearScreen = cs;
  }
};
