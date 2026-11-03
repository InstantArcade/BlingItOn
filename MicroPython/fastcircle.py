def bresenhams_circle( display, x0, y0, r):
    # use existing pen color that is currently set
    x = 0
    y = r
    d = 3 - 2 * r
    
    while (x <= y):
        display.pixel(x + x0, y + y0)  #  SSE arc
        display.pixel(y + x0, x + y0)  #  ESE arc
        display.pixel(-x + x0, y + y0) #  SSW arc
        display.pixel(-y + x0, x + y0) #  WSW arc
        display.pixel(x + x0, -y + y0) #  NNE arc
        display.pixel(y + x0, -x + y0) #  ENE arc
        display.pixel(-x + x0, -y + y0) #  NNW arc
        display.pixel(-y + x0, -x + y0) #  WNW arc
      
        if (d < 0):
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
    
        x += 1
