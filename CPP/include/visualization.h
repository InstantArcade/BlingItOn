#pragma once
#include <Arduino.h>

typedef void (*callback_function)(void);

class Visualization
{
  public:
    callback_function callbackFunc = nullptr; // a callback function that a visualization can activate

	Visualization(){} 
    virtual void init() = 0;
	virtual void update( float deltaTime ) = 0;
    void setCallback( callback_function pFunc )
    {
        // Serial.printf("Setting callback to %p\n", pFunc );
        callbackFunc = pFunc;
    }

    ~Visualization(){};
};