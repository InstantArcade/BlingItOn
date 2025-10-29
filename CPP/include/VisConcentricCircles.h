#pragma once

#include "Visualization.h"
class VisConcentricCircles : public Visualization
{
    public:
    VisConcentricCircles(): Visualization()
    {

    }

    void init();
    void update(float);

    ~VisConcentricCircles()
    {

    }
};