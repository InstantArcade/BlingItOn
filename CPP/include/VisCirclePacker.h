#pragma once
#include "Visualization.h"

class VisCirclePacker : public Visualization
{
public:
	VisCirclePacker() : Visualization()
	{

	}

	void init();
    void focus();
    void reset();
	void update( float delta );

	~VisCirclePacker()
	{

	}
};
