#pragma once

#include "Visualization.h"
class VisSnow : public Visualization
{
    public:
    VisSnow(): Visualization()
    {

    }

    void init();
    void update(float);

    ~VisSnow()
    {

    }
};