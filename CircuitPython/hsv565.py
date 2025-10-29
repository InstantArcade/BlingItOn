# Hue colors sit in these ranges
# 0 Red
# 25 Orange
# 50 Yellow
# 100 Green
# 175 Cyan
# 230 Blue
# 280 Magenta
# 350 Red
#
# Note that conversion can get expensive if you're doing it a lot, so consider
# caching the output values if they don't change much but are used often
# If you only need a hue at full saturation and brightness, then use the
# getHSV function with the hue index to get the pre-calculated value
class HSV565:
    hsv_colors = [0]*360

    def hsv2rgb565( self, h, s, v ):
        hh = 0
        p = 0
        q = 0
        t = 0
        ff = 0
        i = 0

        r = 0
        g = 0
        b = 0

        hh = h
        if hh >= 360.0:
            hh = 0.0

        hh /= 60.0

        i = int(hh)
        ff = hh - i
        p = v * (1.0 - s)
        q = v * (1.0 - (s * ff))
        t = v * (1.0 - (s * (1.0 - ff)))


        if i== 0:
            r = v
            g = t
            b = p
        elif i == 1:
            r = q
            g = v
            b = p
        elif i == 2:
            r = p
            g = v
            b = t
        elif i == 3:
            r = p
            g = q
            b = v
        elif i == 4:
            r = t
            g = p
            b = v
        else:
            r = v
            g = p
            b = q

        # rgb values will be 0-1, make them ints of the correct size
        r *= 15
        g *= 31
        b *= 15
        col565 = (int(r)<<12) | (int(g)<<5) | int(b)

        return col565

    def __init__( self ):
        for i in range(360):
            self.hsv_colors[i] = self.hsv2rgb565(i,1,1)

    def getHSV( self, index ):
        return self.hsv_colors[index%360]