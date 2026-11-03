''' ranges h = 0-360, s & v are 0-1 '''
def hsv_to_rgb(h, s, v):
    if s <= 0.0:
        return v, v, v
    
    # cap s & v if required
    if s > 1.0:
        s = 1.0
    if v > 1.0:
        v = 1.0
    
    hh = h
    if hh > 360.0:
        hh -= 360.0
    hh /= 60.0
    i = int(hh)
    ff = hh - i
    p = v*(1.0-s)
    q = v*(1.0-(s*ff))
    t = v*(1.0-(s*(1.0-ff)))

    i %= 6
    
    if i == 0:
        return [v,t,p]
    elif i == 1:
        return [q,v,p]
    elif i == 2:
        return [p,v,t]
    elif i == 3:
        return [p,q,v]
    elif i == 4:
        return [t,p,v]
    else:
        return [v,p,q]

def hsv_to_rgb_255(h, s, v):
    o = hsv_to_rgb(h,s/255,v/255)
    return [int(o[0]*255),int(o[1]*255),int(o[2]*255)]
