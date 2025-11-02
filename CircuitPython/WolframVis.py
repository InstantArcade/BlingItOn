from random import randrange
import math


class WolframVis:
    """ A visulaization of Wolfram rules """

    cool_rules = [30,129,135,22]
    current_rule = 30

    current_bits = [0]*32
    new_bits = [0]*32

    visWidth = 32 #overwritten by constructor
    visHeight = 32
    visWidthHalf = 16
    visHeighthalf = 16

    def __init__(self, WIDTH,HEIGHT):
        # WIDTH=32
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        self.visWidthHalf = WIDTH//2
        self.visHeighthalf = HEIGHT//2
        self.current_bits = [0]*WIDTH
        self.new_bits = [0]*WIDTH
        print( f"WolframVis initialized - Width {WIDTH}, Height {HEIGHT}")

    def reset( self ):
        self.current_bits = [0]*self.visWidth
        self.new_bits = [0]*self.visWidth

        for i in range( self.visWidth ):
            self.current_bits[i] = 0
        # set center bit
        self.current_bits[self.visWidthHalf-1] = 1

    def mclear(i):
        self.new_bits[i] = 0
        
    def runRule( self, rule_number ):
        for i in range( self.visWidth ):
            self.new_bits[i] = 0
#         map(self.mclear,range(self.visWidth))

        for i in range( self.visWidth ):
            if i == 0: # leftmost bit
                lbit = self.current_bits[ self.visWidth-1 ]
                rbit = self.current_bits[i+1]
                mbit = self.current_bits[i]
            elif i ==  self.visWidth-1: # rightmost bit
                lbit = self.current_bits[i-1]
                rbit = self.current_bits[0]
                mbit = self.current_bits[i]
            else: # all other bits
                lbit = self.current_bits[i-1]
                rbit = self.current_bits[i+1]
                mbit = self.current_bits[i]
        
            key = (lbit<<2) | (mbit<<1) | rbit

            if (1<<key) & rule_number:
                self.new_bits[i] = 1
            else:
                self.new_bits[i] = 0

#     def mappedy( self, rule_number, bitmap ):      
#     del mapsaveline(saved_line, i):
#         
#     
#     def maprulecheck( current_rule, y ):
#         self.runRule( current_rule )

    def update( self, delta, bitmap, accel ):
        saved_line = [0] * self.visWidth

        for y in range( self.visHeight ):
            self.runRule(self.current_rule)

            if y == 0:
                for i in range( self.visWidth ):
                    saved_line[i] = self.new_bits[i]
            
            for x in range( self.visWidth ):
                if self.new_bits[x]:
                    bitmap[x,y] = 14505
#                 else:
#                     bitmap[x,y] = 14505

                self.current_bits[x] = self.new_bits[x]

#         bitmap[63,0] = 0xf800#14505
#         bitmap[4,16] = 0x07e9#matrix.color656(0,255,0)

#         print( self.current_bits )

        # restore line 0
        for x in range( self.visWidth ):

