#include "helpers.h"

// float zbuffer[64*64];
// byte screenBuffer[64*64*3];
// byte screenBuffer2[64*64*3];

float fFocal = 300; // was 300;
float fXRot = 0, fYRot = 0, fZRot = 0;
float fXRotSpeed = 0, fYRotSpeed = 0, fZRotSpeed = 0;

float rMult = 1.0f;
float gMult = 1.0f;
float bMult = 1.0f;

sensors_event_t global_accelerometer;


uint16_t rgbto565Gamma( float r, float g, float b, float gamma = globalGamma )
{
  float rf = pow( r, gamma ) * rMult;
  float gf = pow( g, gamma ) * gMult;
  float bf = pow( b, gamma ) * bMult;

  // 5 bits (0-31) of red, 6 bits (0-63) of green, 5 bits (0-31) of blue
  return (uint16_t)(((int)(rf*31.0f)<<11) | ((int)(gf*63.0f)<<5) | (int)(bf*31.0f));
}

uint16_t rgbto565Gamma( byte r, byte g, byte b, float gamma = globalGamma )
{
  float rf = r/255.0f;
  float gf = g/255.0f;
  float bf = b/255.0f;

  return rgbto565Gamma( rf, gf, bf, gamma );
}


float v3_dot_product( vector3 u, vector3 v )
{
  return (u.x*v.x)+(u.y*v.y)+(u.z*v.z);
}

vector3 normalize( vector3 &v )
{
  float mag = sqrt(v.x*v.x+v.y*v.y+v.z*v.z);
  v.x /= mag;
  v.y /= mag;
  v.z /= mag;
  
  return v;
}

#ifdef COLOR_ORDER_BGR
  void rgbFrom565( uint16_t c, int &r, int &g, int &b )
  {
    b = (c & 0b1111100000000000) >> 8; // 5 bits of blue shift into the top 8 bits
    g = (c & 0b0000011111100000) >> 3; // 6 bits of green shift into the top 8 bits
    r = (c & 0b0000000000011111) << 3; // 5 bits of red, shift into the top 8 bits
  }
#elif defined(COLOR_ORDER_RBG)
  void rgbFrom565( uint16_t c, int &r, int &g, int &b )
  {
    r = (c & 0b1111100000000000) >> 8; // 5 bits of red shift into the top 8 bits
    b = (c & 0b0000011111100000) >> 3; // 6 bits of green shift into the top 8 bits
    g = (c & 0b0000000000011111) << 3; // 5 bits of blue, shift into the top 8 bits
  }
#else
  void rgbFrom565( uint16_t c, int &r, int &g, int &b )
  {
    r = (c & 0b1111100000000000) >> 8; // 5 bits of red shift into the top 8 bits
    g = (c & 0b0000011111100000) >> 3; // 6 bits of green shift into the top 8 bits
    b = (c & 0b0000000000011111) << 3; // 5 bits of blue, shift into the top 8 bits
  }
#endif

void make_counter_clockwise(int& x1, int& y1, int& x2, int& y2, int& x3, int& y3)
{
    int xm = (x1 + x2 + x3) / 3; // center point x coordinate
    int ym = (y1 + y2 + y3) / 3; // center point y coordiante

    float a1 = atan2(xm - x1, ym - y1); // angle between center point and first point
    float a2 = atan2(xm - x2, ym - y2); // angle between center point and second point
    float a3 = atan2(xm - x3, ym - y3); // angle between center point and third point

    // Points are already in order if...
    // 1 < 2 < 3 or
    // 2 < 3 < 1 or 
    // 3 < 1 < 2

    if ((a1 <= a2 && a2 <= a3) || (a2 <= a3 && a3 <= a1) || (a3 <= a1 && a1 <= a2))
    {
        // points are already in order - great!
    }
    else
    {
        // swap two of the points
        x1 = x1 ^ x3;
        x3 = x3 ^ x1;
        x1 = x1 ^ x3;

        y1 = y1 ^ y3;
        y3 = y3 ^ y1;
        y1 = y1 ^ y3;
    }
}

void halfspace_triangle(int x1, int y1, int x2, int y2, int x3, int y3, byte r, byte g, byte b)
{
  int minx = imin(x1,x2,x3);
  int miny = imin(y1,y2,y3);
  int maxx = imax(x1,x2,x3);
  int maxy = imax(y1,y2,y3);

  // constrain to viewport
  if( minx < 0 ) minx = 0;
  if( miny < 0 ) miny = 0;
  if( maxx > 63 ) maxx = 63;
  if( maxy > 63 ) maxy = 63;

  for( int y = miny; y < maxy; y++ )
  {
    for( int x = minx; x < maxx; x++ )
    {
      if( (x1 - x2) * (y - y1) - (y1 - y2) * (x - x1) >= 0 &&
          (x2 - x3) * (y - y2) - (y2 - y3) * (x - x2) >= 0 &&
          (x3 - x1) * (y - y3) - (y3 - y1) * (x - x3) >= 0 )
      {
        matrix->RGBPixel(x,y,r,g,b);
      }
    }
  }
}

void halfspace_triangle_v(vector3 v1, vector3 v2, vector3 v3, byte r, byte g, byte b)
{
  halfspace_triangle(v1.x,v1.y,v2.x,v2.y,v3.x,v3.y,r,g,b);
}

#define RED(v) v.x
#define GREEN(v) v.y
#define BLUE(v) v.z

void halfspace_triangle_lerp( float *zbuffer, vector3 v1, vector3 v2, vector3 v3, vector3 c1, vector3 c2, vector3 c3)
{
  int minx = imin(v1.x,v2.x,v3.x);
  int miny = imin(v1.y,v2.y,v3.y);
  int maxx = imax(v1.x,v2.x,v3.x);
  int maxy = imax(v1.y,v2.y,v3.y);

  // constrain to viewport
  if( minx < 0 ) minx = 0;
  if( miny < 0 ) miny = 0;
  if( maxx > 63 ) maxx = 63;
  if( maxy > 63 ) maxy = 63;

  for( int y = miny; y <= maxy; y++ )
  {
    for( int x = minx; x <= maxx; x++ )
    {
      // barycentric coords for x,y
      float alpha,beta,gamma;
      alpha = (v1.x - v2.x) * (y - v1.y) - (v1.y - v2.y) * (x - v1.x);
      beta = (v2.x - v3.x) * (y - v2.y) - (v2.y - v3.y) * (x - v2.x);
      gamma = (v3.x - v1.x) * (y - v3.y) - (v3.y - v1.y) * (x - v3.x);

      // normalize
      float mag = alpha+beta+gamma;
      alpha /= mag;
      beta /= mag;
      gamma /= mag;

      if( alpha >= 0 && beta >= 0 && gamma >= 0 )
      {
        byte r,g,b;
        // lerp the vertex colors
        r = (c3.x*alpha + c1.x*beta + c2.x*gamma)*255;
        g = (c3.y*alpha + c1.y*beta + c2.y*gamma)*255;
        b = (c3.z*alpha + c1.z*beta + c2.z*gamma)*255;

        // bonus get lerped z position the same way
        float zl = (v3.z*alpha + v1.z*beta + v2.z*gamma); // use reciprocal instead of raw value

        if( zl < zbuffer[y*64+x] )
        {
          matrix->RGBPixel(x,y,r,g,b);
          zbuffer[y*64+x] = zl;
        }
      }
    }
  }
}

byte HSVColors[360*3];
uint16_t HSV565[360];
int hueOffset = 0;
bool cycleHue = true;
byte hueCycleDelay = 10;
byte hueCycleCount = 0;

byte shadedBall2[]={
  0,0,118,168,153,80,0,0,
  0,190,238,221,201,182,112,0,
  108,226,233,239,212,195,131,53,
  155,202,227,227,208,169,116,72,
  131,184,196,198,183,139,99,69,
  67,144,149,151,134,108,82,45,
  0,89,111,101,89,80,78,19,
  0,0,47,69,71,47,0,0
};

byte shadedBall3[]={
    0,118,153,  0,
  108,233,212,131,
  131,196,183, 99,
    0, 47, 71,  0,
};

byte  ringMaxVal = 0;
byte  ringMinVal = 255;

// 16 frames in total, each an 8x8 sprite
byte spinning_ring[]={
// 0
        0,      146,    167,    169,    167,    152,    0,      0,      // Row 0
        134,    164,    157,    129,    125,    157,    153,    0,      // Row 1
        148,    152,    86,     0,      0,      113,    153,    121,    // Row 2
        147,    141,    0,      0,      0,      0,      149,    128,    // Row 3
        139,    141,    0,      0,      0,      0,      148,    122,    // Row 4
        113,    151,    135,    0,      0,      147,    148,    85,     // Row 5
        0,      115,    152,    156,    156,    151,    105,    0,      // Row 6
        0,      0,      93,     102,    100,    75,     0,      0,      // Row 7
// 1
        0,      156,    168,    171,    167,    158,    0,      0,      // Row 0
        141,    163,    162,    138,    136,    156,    149,    0,      // Row 1
        146,    149,    75,     0,      0,      102,    150,    121,    // Row 2
        141,    131,    0,      0,      0,      0,      140,    123,    // Row 3
        132,    132,    0,      0,      0,      0,      141,    111,    // Row 4
        107,    144,    135,    0,      0,      148,    143,    72,     // Row 5
        0,      112,    147,    153,    154,    145,    99,     0,      // Row 6
        0,      0,      80,     99,     93,     79,     0,      0,      // Row 7
// 2
        0,      0,      164,    171,    166,    160,    0,      0,      // Row 0
        0,      164,    166,    151,    150,    159,    147,    0,      // Row 1
        146,    147,    99,     0,      0,      101,    140,    113,    // Row 2
        134,    114,    0,      0,      0,      0,      128,    108,    // Row 3
        119,    123,    0,      0,      0,      0,      133,    99,     // Row 4
        98,     134,    136,    0,      0,      147,    134,    71,     // Row 5
        0,      100,    139,    150,    152,    135,    94,     0,      // Row 6
        0,      0,      77,     90,     82,     69,     0,      0,      // Row 7
// 3
        0,      0,      159,    171,    161,    0,      0,      0,      // Row 0
        0,      163,    170,    171,    166,    161,    146,    0,      // Row 1
        143,    147,    120,    73,     85,     106,    138,    106,    // Row 2
        125,    100,    0,      0,      0,      0,      110,    93,     // Row 3
        101,    106,    0,      0,      0,      0,      122,    80,     // Row 4
        76,     120,    141,    144,    147,    144,    121,    62,     // Row 5
        0,      74,     116,    143,    145,    117,    61,     0,      // Row 6
        0,      0,      53,     59,     55,     52,     0,      0,      // Row 7
// 4
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 0
        0,      161,    172,    175,    171,    161,    138,    0,      // Row 1
        138,    151,    132,    115,    113,    125,    136,    100,    // Row 2
        115,    85,     0,      0,      0,      0,      82,     82,     // Row 3
        79,     73,     0,      0,      0,      52,     94,     61,     // Row 4
        58,     98,     130,    132,    139,    136,    102,    52,     // Row 5
        0,      52,     94,     116,    120,    95,     52,     0,      // Row 6
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 7
// 5
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 0
        0,      0,      165,    174,    169,    148,    0,      0,      // Row 1
        145,    158,    161,    159,    155,    153,    140,    86,     // Row 2
        113,    97,     80,     52,     52,     68,     78,     68,     // Row 3
        54,     52,     52,     0,      0,      52,     52,     52,     // Row 4
        53,     52,     51,     52,     52,     51,     52,     52,     // Row 5
        0,      0,      52,     52,     52,     52,     0,      0,      // Row 6
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 7
// 6
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 0
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 1
        146,    160,    170,    174,    171,    161,    140,    0,      // Row 2
        116,    124,    109,    113,    104,    98,     99,     76,     // Row 3
        53,     52,     129,    148,    148,    138,    59,     52,     // Row 4
        0,      52,     51,     78,     88,     51,     52,     0,      // Row 5
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 6
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 7
// 7
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 0
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 1
        0,      161,    171,    173,    165,    156,    141,    0,      // Row 2
        126,    151,    161,    161,    156,    147,    130,    89,     // Row 3
        56,     66,     116,    137,    140,    127,    64,     52,     // Row 4
        0,      52,     70,     81,     82,     63,     52,     0,      // Row 5
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 6
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 7
// 8
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 0
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 1
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 2
        138,    160,    169,    173,    168,    161,    145,    109,    // Row 3
        70,     92,     106,    110,    105,    92,     75,     53,     // Row 4
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 5
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 6
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 7
// 9
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 0
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 1
        0,      144,    145,    149,    147,    144,    144,    0,      // Row 2
        144,    147,    144,    145,    150,    148,    146,    124,    // Row 3
        100,    144,    161,    164,    161,    149,    120,    70,     // Row 4
        0,      52,     69,     81,     78,     62,     52,     0,      // Row 5
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 6
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 7
// 10
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 0
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 1
        143,    150,    150,    154,    156,    154,    142,    0,      // Row 2
        149,    139,    106,    104,    108,    120,    148,    132,    // Row 3
        123,    161,    168,    169,    166,    161,    147,    98,     // Row 4
        0,      93,     112,    129,    121,    100,    70,     0,      // Row 5
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 6
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 7
// 11
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 0
        0,      0,      152,    152,    150,    146,    0,      0,      // Row 1
        146,    155,    150,    143,    148,    155,    153,    102,    // Row 2
        152,    142,    76,     86,     75,     100,    151,    135,    // Row 3
        138,    161,    161,    0,      0,      160,    154,    108,    // Row 4
        52,     126,    157,    162,    160,    146,    112,    52,     // Row 5
        0,      0,      52,     77,     77,     52,     0,      0,      // Row 6
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 7
// 12
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 0
        0,      152,    158,    159,    159,    155,    129,    0,      // Row 1
        149,    157,    131,    105,    116,    141,    158,    118,    // Row 2
        152,    146,    0,      0,      0,      0,      149,    139,    // Row 3
        144,    158,    0,      0,      0,      147,    156,    121,    // Row 4
        98,     151,    163,    166,    165,    158,    131,    60,     // Row 5
        0,      88,     111,    122,    121,    96,     66,     0,      // Row 6
        0,      0,      0,      0,      0,      0,      0,      0,      // Row 7
// 13
        0,      0,      138,    153,    141,    0,      0,      0,      // Row 0
        0,      158,    161,    157,    159,    160,    147,    0,      // Row 1
        155,    158,    123,    86,     92,     131,    161,    132,    // Row 2
        153,    148,    0,      0,      0,      0,      157,    138,    // Row 3
        147,    157,    0,      0,      0,      0,      158,    130,    // Row 4
        115,    161,    163,    153,    156,    158,    148,    79,     // Row 5
        0,      101,    137,    154,    149,    127,    78,     0,      // Row 6
        0,      0,      53,     61,     58,     52,     0,      0,      // Row 7
// 14
        0,      0,      157,    161,    159,    150,    0,      0,      // Row 0
        0,      162,    162,    147,    147,    163,    153,    0,      // Row 1
        157,    158,    106,    0,      0,      130,    163,    135,    // Row 2
        154,    148,    0,      0,      0,      0,      157,    138,    // Row 3
        150,    153,    0,      0,      0,      0,      157,    133,    // Row 4
        109,    162,    154,    0,      0,      159,    153,    105,    // Row 5
        0,      114,    152,    157,    156,    142,    97,     0,      // Row 6
        0,      0,      52,     91,     83,     69,     0,      0,      // Row 7
// 15
        0,      129,    162,    166,    162,    150,    0,      0,      // Row 0
        157,    163,    158,    134,    137,    158,    153,    0,      // Row 1
        151,    157,    98,     0,      0,      125,    158,    122,    // Row 2
        152,    147,    0,      0,      0,      0,      153,    136,    // Row 3
        146,    151,    0,      0,      0,      0,      153,    128,    // Row 4
        125,    157,    147,    0,      0,      155,    154,    97,     // Row 5
        0,      121,    153,    161,    159,    152,    105,    0,      // Row 6
        0,      0,      85,     103,    95,     72,     0,      0,      // Row 7
};

hsv rgb2hsv(rgb in)
{
    hsv         out;
    float      min, max, delta;

    min = in.r < in.g ? in.r : in.g;
    min = min  < in.b ? min  : in.b;

    max = in.r > in.g ? in.r : in.g;
    max = max  > in.b ? max  : in.b;

    out.v = max;                                // v
    delta = max - min;
    if (delta < 0.00001)
    {
        out.s = 0;
        out.h = 0; // undefined, maybe nan?
        return out;
    }
    if( max > 0.0 ) { // NOTE: if Max is == 0, this divide would cause a crash
        out.s = (delta / max);                  // s
    } else {
        // if max is 0, then r = g = b = 0
        // s = 0, h is undefined
        out.s = 0.0;
        out.h = 0;// -1.0 / 0;                            // its now undefined
        return out;
    }
    if( in.r >= max )                           // > is bogus, just keeps compilor happy
        out.h = ( in.g - in.b ) / delta;        // between yellow & magenta
    else
    if( in.g >= max )
        out.h = 2.0 + ( in.b - in.r ) / delta;  // between cyan & yellow
    else
        out.h = 4.0 + ( in.r - in.g ) / delta;  // between magenta & cyan

    out.h *= 60.0;                              // degrees

    if( out.h < 0.0 )
        out.h += 360.0;

    return out;
}


rgb hsv2rgb(hsv in)
{
    float      hh, p, q, t, ff;
    int        i;
    rgb         out;

    if(in.s <= 0.0) {       // < is bogus, just shuts up warnings
        out.r = in.v;
        out.g = in.v;
        out.b = in.v;
        return out;
    }
    hh = in.h;
    if(hh >= 360.0) hh = 0.0;
    hh /= 60.0;
    i = (int)hh;
    ff = hh - i;
    p = in.v * (1.0 - in.s);
    q = in.v * (1.0 - (in.s * ff));
    t = in.v * (1.0 - (in.s * (1.0 - ff)));

    switch(i) {
    case 0:
        out.r = in.v;
        out.g = t;
        out.b = p;
        break;
    case 1:
        out.r = q;
        out.g = in.v;
        out.b = p;
        break;
    case 2:
        out.r = p;
        out.g = in.v;
        out.b = t;
        break;

    case 3:
        out.r = p;
        out.g = q;
        out.b = in.v;
        break;
    case 4:
        out.r = t;
        out.g = p;
        out.b = in.v;
        break;
    case 5:
    default:
        out.r = in.v;
        out.g = p;
        out.b = q;
        break;
    }
    return out;
}

void generateHSVTable()
{
//    if( !HSVColors )
//        HSVColors = new byte[360*3];
    
    // generate HSVColors
    for( int i = 0; i < 360; i++ )
    {
        hsv in;
        in.h = i;//(360/256)*i;
        in.s = 1.0f;
        in.v = 1.0f;
        rgb col = hsv2rgb(in);
        // col values are all 0-1
        HSVColors[i*3+0] = col.r * 255;
        HSVColors[i*3+1] = col.g * 255;
        HSVColors[i*3+2] = col.b * 255;
        HSV565[i] = rgbto565Gamma(col.r,col.g,col.b);
    }
}

void cycleTheHue( float delta )
{
  hueCycleCount++;
  if( hueCycleCount >= hueCycleDelay )
  {
    hueCycleCount = 0;
    hueOffset++;
    hueOffset %= 360;
  }
}

void drawRippedSprite(int x, int y, const int *planeOffsets, const int *frameOffsets, const byte* dataSrc, byte frame, uint16_t color_override )
{
  uint32_t dataOffset = frameOffsets[frame*2+1];
  const byte *pData = dataSrc + dataOffset;
  uint16_t numPlanes = frameOffsets[frame*2];
  int skipPlanes = 0;

  for( int i = 0; i < frame; i++ )
  {
    skipPlanes += frameOffsets[i*2]; // add plane count of each frame we're skiping 
  }
  
  for( int i = 0; i < numPlanes; i++ )
  {
    pData = dataSrc + planeOffsets[skipPlanes+i];

    pData++; // skip alpha
    byte r= *pData++;
    byte g= *pData++;
    byte b= *pData++;
    byte xoff = *(pData++);
    byte yoff = *(pData++);
    byte w = *(pData++);
    byte h = *(pData++);


    if( color_override != 0 )
      matrix->drawBitmap(x+xoff,y+yoff,pData,w,h,color_override);
    else
      matrix->drawBitmap(x+xoff,y+yoff,pData,w,h,matrix->color565(r,g,b));
  }
}

void drawRippedSpriteWithMask(int x, int y, const int *planeOffsets, const int *frameOffsets, const byte* dataSrc, byte frame, uint16_t color_override, uint16_t mask_color )
{
  uint32_t dataOffset = frameOffsets[frame*2+1];
  const byte *pData = dataSrc + dataOffset;
  uint16_t numPlanes = frameOffsets[frame*2];
  int skipPlanes = 0;

  for( int i = 0; i < frame; i++ )
  {
    skipPlanes += frameOffsets[i*2]; // add plane count of each frame we're skiping 
  }
  
  
  for( int i = 0; i < numPlanes; i++ )
  {
    pData = dataSrc + planeOffsets[skipPlanes+i];

    pData++; // skip alpha
    byte r= *pData++;
    byte g= *pData++;
    byte b= *pData++;
    byte xoff = *(pData++);
    byte yoff = *(pData++);
    byte w = *(pData++);
    byte h = *(pData++);

    // now draw the normal color
    if( color_override != 0 )
      matrix->drawBitmap(x+xoff,y+yoff,pData,w,h,color_override);
    else
      matrix->drawBitmap(x+xoff,y+yoff,pData,w,h,matrix->color565(r,g,b));
  }
}

void BresenhamLine( int x0, int y0, int x1, int y1, byte r, byte g, byte b )
{   
  int dx =  abs(x1-x0); // delta x
  int sx = x0 < x1 ? 1 : -1; // s direction
  
  int dy = -abs(y1-y0); // delta y
  int sy = y0 < y1 ? 1 : -1; // y direction
  
  int err = dx+dy;  // error value e_xy
  
  while (true)   // loop
  {
    // bound check
    if( x0 >= 0 && x0 < 64 && y0 >=0 && y0 <64 )
    {
      matrix->RGBPixel(x0,y0,r,g,b);
    }
    if (x0 == x1 && y0 == y1) break; // we reached the destination - stop now
    
    int e2 = 2*err;
    if (e2 >= dy) // e_xy + e_x > 0
    {
      err += dy;
      x0 += sx; // move along the x direction
    }
    if (e2 <= dx) // e_xy + e_y < 0
    {
      err += dx;
      y0 += sy; // move along the y direction
    }
  }     
}

void BresenhamsCircle(int x0, int y0, int radius, int color )
{
  int x = 0;
  int y = radius;
  int d = 3 - 2 * radius;

  while (x <= y) 
  {
    matrix->drawPixel(x + x0, y + y0, color);
    matrix->drawPixel(y + x0, x + y0, color);
    matrix->drawPixel(-x + x0, y + y0, color);
    matrix->drawPixel(-y + x0, x + y0, color);

    matrix->drawPixel(x + x0, -y + y0, color);
    matrix->drawPixel(y + x0, -x + y0, color);
    matrix->drawPixel(-x + x0, -y + y0, color);
    matrix->drawPixel(-y + x0, -x + y0, color);
  
    if( d < 0 ) 
    {
      d += 4 * x + 6;
    }
    else 
    {
      d += 4 * (x - y) + 10;
      y--;
    }
    x++;
  }
}