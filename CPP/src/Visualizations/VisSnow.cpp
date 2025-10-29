#include "VisSnow.h"
#include "helpers.h"

byte collision_bufffer[64][64];

class SnowParticle
{
public:
  float x,y;
  float vx,vy;
  uint16_t color;
  float speedmul = 1.0f;
  bool active;

  SnowParticle()
  {
    x = y = vx = vy = 0;
    active = false;
    color = matrix->color565(255,255,255);
    speedmul = 1.0f + random(100)/100.0f;
  }

  void move(float delta)
  {
    if( !active ) return;

    // Calc new pos
    float nx = x + vx*delta;
    float ny = y + vy*delta;

    // check for going off screen
    int inx = (int)nx;
    int iny = (int)ny;
    if( inx <0 || inx > 63 || iny < 0 || iny > 63 )
    {
      // active = false;
      // return;
      nx = x;
      ny = y;
    }

    // check collision
    if( collision_bufffer[inx][iny] > 0 )
    {
      // stop it
      nx = x;
      ny = y;
    }

    // set new x & y
    x = nx;
    y = ny;
  }

};

const int MAX_SNARTS = 64*5;
SnowParticle snarticles[MAX_SNARTS];

void resetSnow()
{
  // clear collision buffer
  for( int y = 0; y < 64; y++ )
    for( int x = 0; x < 64; x++ )
      collision_bufffer[x][y] = 0;

  // reset all particles
  for( int y = 0; y < 5; y++ )
    for( int x = 0; x < 64; x++ )
    {
      int i = y*64+x;
      snarticles[i].x = x;
      snarticles[i].y = y;
      snarticles[i].vx = snarticles[i].vy = 0;
      snarticles[i].active = true;
      snarticles[i].color = HSV565[random(360)];
      snarticles[i].speedmul = 1.0f + random(100)/100.0f;
    }

}

void VisSnow::init()
{
    resetSnow();
}

void VisSnow::update( float delta )
{

  for( int i = 0; i < MAX_SNARTS; i++ )
  {
    bool collided = false;
    SnowParticle *sp = &snarticles[i];

    sp->vx += global_accelerometer.acceleration.x * sp->speedmul * delta * 10.0f;
    sp->vy += global_accelerometer.acceleration.y * sp->speedmul * delta * 10.0f;

    // cap velocities
    if( sp->vx > 100.0f ){ sp->vx = 100.0f; }
    if( sp->vy > 100.0f ){ sp->vy = 100.0f; }
    if( sp->vx < -100.0f ){ sp->vx = -100.0f; }
    if( sp->vy > 100.0f ){ sp->vy = -100.0f; }

//    sp->move(delta);

    // if it's active, move and draw it
    if( sp->active )
    {
      // Calc new pos
      float nx = sp->x + sp->vx*delta;
      float ny = sp->y + sp->vy*delta;

      // check for going off screen
      int inx = (int)nx;
      int iny = (int)ny;
      if( inx <0 || inx > 63 || iny < 0 || iny > 63 ) // hit the edge
      {
        // active = false;
        // return;
        collided = true;          
      }

      // check collision with buffer
      if( collision_bufffer[inx][iny] > 0 ) // hit something in the buffer
      {
        collided = true;          
      }

      // check collision with other snarticles
      for( int j = 0; j < MAX_SNARTS; j++ )
      {
        if( i == j ) continue; // don't check against ourselves
        SnowParticle *so = &snarticles[j];
        if( inx == (int)so->x && iny == (int)so->y )
        {
          collided = true;  // Hit another particle
        }
      }

      if( collided )
      {
        // don't update position
        nx = sp->x;
        ny = sp->y;

        // bounce?
        sp->vx *= 0.5f;
        sp->vy *= 0.5f;
      }
      else
      {
        // set new x & y
        sp->x = nx;
        sp->y = ny;
      }

      matrix->drawPixel( (int)sp->x,(int)sp->y, sp->color );
    }
  }
}