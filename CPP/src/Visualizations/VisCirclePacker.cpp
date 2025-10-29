#include "VisCirclePacker.h"
#include "helpers.h"


class Circle
{
public:
  float x;
  float y;
  float r;
  bool active;
  int hue = 0;
  
  Circle(float x_, float y_, float r_, bool a_)
  {
    x=x_;
    y=y_;
    r=r_;
    active=a_;
  }

  Circle()
  {
    x=0;
    y=0;
    r=0;
    active=false;
  }
};

const int MAX_CIRCLES = 100;
Circle circles[MAX_CIRCLES];
int lastNumActiveCircles = 0;
int numActiveCircles = 0;
int hueOff = 0;
float clearPause = 0;

// void drawCircle(float x, float y, float radius, byte r, byte g, byte b)
// {
//   float circumference = radius*PI*2.0f;
//   float dx,dy,dxf,dyf;
//   float step = (PI*2.0f)/circumference;
//   float intensity1, intensity2;
//   int nr, ng, nb;
  
//   for( float a = 0.0f; a <= PI*2.0f; a += step )
//   {
// //    dx = round(x + cosf(a)*radius);
// //    dy = round(y + sinf(a)*radius);
//     dx = (x + cosf(a)*radius);
//     dy = (y + sinf(a)*radius);

//     // floating point component
// //    dxf = dx-(int)dx;
// //    dyf = dy-(int)dy;
    
//     if( dx >= 0 && dx <= 63 && dy >= 0 && dy <= 63 )
//     {
//       matrix->RGBPixel(dx,dy,r,g,b);
//     }
//   }
// }

float CircleStepFactor = 360.0f;

void drawCircle(int x, int y, float radius, int color)//rgb_24 &color)
{
  // for(float i=0; i<PI2;i+=PI2/210.0f)
  float circumference = PI*2.0f*radius;
  // float cStep = 270.0f/circumference;// was 360, but that makes uglier circles
  float cStep = CircleStepFactor/circumference;// was 360, but that makes uglier circles
  for(float i=0; i<360.0f;i+=cStep)
  {
    int dx = round(x+cosf(i*PI/180.0f)*radius);
    int dy = round(y+sinf(i*PI/180.0f)*radius);
    matrix->drawPixel(dx,dy,color);
  }
}

bool stopTrying = false;
void resetCircles()
{
  clearPause = 0.0f;
  for( int i = 0; i < MAX_CIRCLES; i++ )
  {
    circles[i].active = false;
    circles[i].hue = random(360);
  }
  stopTrying = false;
}


// void doCircles( float delta )
// {
//   // reset circles if required
//   if( numActiveCircles == lastNumActiveCircles )
//   {
//     clearPause += delta;
//     if( clearPause > 5.0f )
//     {
//       clearPause = 0.0f;
//       resetCircles();
//     }
//   }
//   else
//   {
//     lastNumActiveCircles = numActiveCircles;
//     clearPause = 0;
//   }
  
// // CRGB black = CRGB(0,0,0);
// // CRGB white = CRGB(255,255,255);
  
//   numActiveCircles = 0;
//   int addThisFrame = 1; // was 2
//   hueOff+=3;
//   hueOff %=360;
  
//   for( int i = 0; i < MAX_CIRCLES; i++ )
//   {
//     Circle &c = circles[i];
//     if( c.active )
//     {
//       numActiveCircles++;
//       //if( c.x - (c.r+1) > 0 && c.x + (c.r+1) < 64 && c.y - (c.r+1) > 0  && c.y + (c.r+1) < 64 )
      
//       // Am I touching the edges?
//       // if( c.x - c.r > 0 && c.x + c.r < 64 && c.y - c.r > 0  && c.y + c.r < 64 )
//       {
//         // Now check the circle isn't touching any other circle
//         boolean canGrow = true;
//         for( int j = 0; j < MAX_CIRCLES; j++ )
//         {
//           if( i==j ) continue;
          
//           Circle &c2 = circles[j];
//           if( c2.active )
//           {
//             if( fabs(c.x - c2.x) < c.r+1+c2.r && fabs(c.y - c2.y) < c.r+1+c2.r ) 
//             {
//               // can't grow
//               canGrow = false;
//               break;
//             }
//           }
//         }

//         if( canGrow )
//         {
//           // Not touching anything, can still grow.
//           // So undraw first
// //          drawCircle(c.x,c.y,c.r, black );
//           //grow
//           c.r += 1;//0.25f;
//         }

//       }
//       // redraw
//       int color = matrix->color565(HSVColors[((c.hue+hueOff)%360)*3+0],HSVColors[((c.hue+hueOff)%360)*3+1],HSVColors[((c.hue+hueOff)%360)*3+2]);
//       drawCircle(c.x,c.y,int(c.r), color);
//     }
//     else if( !stopTrying && addThisFrame > 0 && numActiveCircles < MAX_CIRCLES )
//     {
//       boolean clear = false;
//       // shift method
//       //int numTries = 4096;
//       //c.x = random(64);
//       //c.y = random(64);
//       int numTries = 200;
//       while( clear == false && numTries > 0 )
//       {
//         numTries--;
//         clear = true;
  
//         // truly random method
//         c.x = random(64);
//         c.y = random(64);
//         c.r = 1.0f;
        
//         // Now check the new circle isn't inside any other circle
//         for( int j = 0; j < MAX_CIRCLES; j++ )
//         {
//           if( i==j ) continue;
          
//           Circle &c2 = circles[j];
//           if( c2.active )
//           {
//             if( fabs(c.x - c2.x) < (c2.r + c.r + 1) && fabs(c.y - c2.y) < (c2.r+c.r+1) ) { clear = false; break; }
//           }
//         }
//       } // tries loop
//       if( numTries > 0 && clear )
//       {
//         c.r = 1.0f;
//         c.active = true;
//         addThisFrame--;
//       }
//       else if( numTries == 0 )
//       {
//         lastNumActiveCircles = numActiveCircles;
//         clearPause = 0;
//         stopTrying = true;
//       }
//       Serial.printf("Num tries %d\n", numTries);
//     } // active Circles < Max and we're trying to add
//   } // loop through all circles 0-MAX
// }


void VisCirclePacker::focus()
{
  resetCircles();
//   resetRects();
}

void VisCirclePacker::reset()
{
    resetCircles();
    // resetRects();
}

void VisCirclePacker::init()
{
    resetCircles();
    // resetRects();
}

extern float gfCommon;
extern float gxCommon;
extern float gyCommon;

float frad = 0.1;
float fdelay = 0.0f;
void VisCirclePacker::update( float delta )
{
  // reset circles if required
  if( numActiveCircles == lastNumActiveCircles )
  {
    clearPause += delta;
    if( clearPause > 5.0f )
    {
      clearPause = 0.0f;
      resetCircles();
    }
  }
  else
  {
    lastNumActiveCircles = numActiveCircles;
    clearPause = 0;
  }
  
  numActiveCircles = 0;
  int addThisFrame = 1; // was 2
  hueOff+=3;
  hueOff %=360;
  
  for( int i = 0; i < MAX_CIRCLES; i++ )
  {
    Circle &c = circles[i];
    if( c.active )
    {
      numActiveCircles++;
      // Now check the circle isn't touching any other circle
      boolean canGrow = true;
      for( int j = 0; j < MAX_CIRCLES; j++ )
      {
        if( i==j ) continue;
        
        Circle &c2 = circles[j];
        if( c2.active )
        {
          if( fabs(c.x - c2.x) < c.r+1+c2.r && fabs(c.y - c2.y) < c.r+1+c2.r ) 
          {
            // can't grow
            canGrow = false;
            break;
          }
        }
      }

      if( canGrow )
      {
        // Not touching anything, can still grow.
        c.r += 1;//0.25f;
      }

      // redraw
      int color = matrix->color565(HSVColors[((c.hue+hueOff)%360)*3+0],HSVColors[((c.hue+hueOff)%360)*3+1],HSVColors[((c.hue+hueOff)%360)*3+2]);
      //drawCircle(c.x,c.y,int(c.r), color);
      BresenhamsCircle(c.x,c.y,int(c.r), color );
    }
    else if( !stopTrying && addThisFrame > 0 && numActiveCircles < MAX_CIRCLES )
    {
      boolean clear = false;
      // shift method
      int numTries = 200;
      while( clear == false && numTries > 0 )
      {
        numTries--;
        clear = true;
  
        // truly random method
        c.x = random(64);
        c.y = random(64);
        c.r = 1.0f;
        
        // Now check the new circle isn't inside any other circle
        for( int j = 0; j < MAX_CIRCLES; j++ )
        {
          if( i==j ) continue;
          
          Circle &c2 = circles[j];
          if( c2.active )
          {
            if( fabs(c.x - c2.x) < (c2.r + c.r + 1) && fabs(c.y - c2.y) < (c2.r+c.r+1) ) { clear = false; break; }
          }
        }
      }
      if( numTries > 0 && clear )
      {
        c.r = 1.0f;
        c.active = true;
        addThisFrame--;
      }
      if( numTries == 0 )
      {
        // exhaused all our tries
        stopTrying = true;
      }
    }
  }
}
