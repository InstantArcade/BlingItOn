from random import randrange
import math

import VectorFont
from shapes import jollywrencher
from hsv import hsv_to_rgb_255

ASPECT_RATIO = 1

class Vertex:
    """ represents a vertex object """
    x = 0
    y = 0
    z = 0
    tx = 0 # Transfromed positions
    ty = 0
    tz = 0
    color = 0xFFFF
    shapeIndex = 0

# Vector Effect Types
VET_PAUSE = 0
VET_SET_COLOR = 1
VET_SET_SCALE = 2
VET_SET_ROTATION = 3
VET_SET_TRANSLATION = 4
VET_SET_WORD = 5
VET_SET_REPEAT = 6
VET_SET_SHAPE = 7

class VectorEffect:
    type = VET_PAUSE
    effect_time = 1.0 # How long to lerp the effect in seconds
    effect_time_remaining = 0 # set to effect_time when the effect is created 
    effect_value_start = None
    effect_value_end = None
    effect_value_current = None
    effect_complete = False
    stack = False # stack with previous effects or wait for previous to finish
    
    def __init__(self):
        self.type = VET_SET_SCALE
        self.effect_time = 0.0
        self.effect_time_remaining = self.effect_time
        self.effect_value_start = [1.0,1.0,1.0]
        self.effect_value_end = [1.0,1.0,1.0]
        self.effect_value_current = [1.0,1.0,1.0]
        self.group = 0
        self.effect_complete = False

    # Reset an expired effect to its initial values ready to go again
    def reset( self ):
        self.effect_time_remaining = self.effect_time
        for i in range(3):
            self.effect_value_current[i] = self.effect_value_start[i]
        self.effect_complete = False
        
    def update( self, delta ):
        if self.type == VET_SET_REPEAT: # special case don't update here
            return
            
        if self.effect_time_remaining < 0:
            self.effect_time_remaining = 0
            if self.type == VET_SET_WORD or self.type == VET_SET_SHAPE:
                pass
            else:
                self.effect_value_current[0] = self.effect_value_end[0]
                self.effect_value_current[1] = self.effect_value_end[1]
                self.effect_value_current[2] = self.effect_value_end[2]
            self.effect_complete = True # flag that this effect is done (for cleanup)
        else:
            if self.effect_time_remaining > 0.0:
                # lerp is now how close to the start value we are 0-1
                lerp = self.effect_time_remaining/self.effect_time
                if self.type == VET_PAUSE:
                    pass
                elif self.type == VET_SET_WORD:
                    pass
                else:
                    self.effect_value_current[0] = self.effect_value_start[0] + ((self.effect_value_end[0]-self.effect_value_start[0])*(1-lerp))
                    self.effect_value_current[1] = self.effect_value_start[1] + ((self.effect_value_end[1]-self.effect_value_start[1])*(1-lerp))
                    self.effect_value_current[2] = self.effect_value_start[2] + ((self.effect_value_end[2]-self.effect_value_start[2])*(1-lerp))
        # move time        
        self.effect_time_remaining -= delta
        
class VectorVis():
    """ A simple 3D rotating 3D Vector visulaization """

    def __init__(self, WIDTH,HEIGHT):
        self.visWidth = WIDTH
        self.visHeight = HEIGHT
        print( f"VectorVis initialized - Width {WIDTH}, Height {HEIGHT}")

    num_letters = 0 # track the number of letters for vector spacing
    letter_spacing = 8  #0.35
    
    x_rot = 0
    y_rot = 0
    z_rot = 0

    x_rot_speed = 1     * 2
    y_rot_speed = 1.01   * 2
    z_rot_speed = -0.02   * 2

    zoom = 3

    MAX_NUM_VERTS = 140
    all_verts = []
    effects = []

    default_scale = 1
    x_off = 0
    y_off = 0

    size_wave = 0
    size_wave_speed = 10

    xo_wave = 0
    yo_wave = 0
    xo_speed = 10
    yo_speed = 2

    hue_offset = 0

    last_print = 0
    
    use_effects = True

    def add_letter( self, letter ):
        # Find letter in vectorFont
        for entry in VectorFont.keyToShapeList:
            if entry[0] == letter:
                # move the verts based on how many letters we have to make room
                for x in range(len(self.all_verts)):
                    self.all_verts[x].x -= self.letter_spacing;
                # now add the letter
                for j in (entry[1]):
                    v = Vertex()
                    v.x = j[0]
                    v.y = j[1]
                    v.z = 0
                    v.shapeIndex = j[2] + self.num_letters*30  # for VectorFont shapes
                    v.color = 0xffff
                    self.all_verts.append(v)
                    
                self.num_letters += 1
                return

        # Special case if the letter was space or not found, just increment the letter count
        if letter == ' ':
            self.num_letters += 1        
            for x in range(len(self.all_verts)):
                self.all_verts[x].x -= self.letter_spacing;
        else: # not found
            for x in range(len(self.all_verts)):
                self.all_verts[x].x -= self.letter_spacing;

            for j in (VectorFont.symbol_dash_verts):
                v = Vertex()
                v.x = j[0]
                v.y = j[1]
                v.z = 0
                v.shapeIndex = j[2] + self.num_letters*30  # for VectorFont shapes
                v.color = 0xffff
                self.all_verts.append(v)
                
            self.num_letters += 1

    def add_word( self, string ):
        for i in range(len(string)):
            self.add_letter(string[i])
    
    def set_effect( self, effect ): # clear all effects and set this one
        self.effects = []
        self.effects.append(effect)
        
    def add_effect( self, effect): # Add the specified effect to the list
        self.effects.append(effect)

    def load_shape(self, shape_verts ):
        self.all_verts = []
        for i in shape_verts:
            v = Vertex()
            v.x = i[0]
            v.y = i[1]
            v.z = 0 # Z is not in the output of the shape maker for 2D shapes
            v.shapeIndex = i[2]
            self.all_verts.append(v)

    def load_shape_3D(self, shape_verts ):
        self.all_verts = []
        for i in shape_verts:
            v = Vertex()
            v.x = i[0]
            v.y = i[1]
            v.z = i[2]# For 3D shapes, z is the 3rd component and shape index is the 4th
            v.shapeIndex = i[3]
            self.all_verts.append(v)

    def clear(self):
        self.all_verts = []
        self.effects = []
    
    def center_all(self): # Centers the entire object
        minx = 99999
        maxx = -99999
        miny = 99999
        maxy = -99999
        for i in range(len(self.all_verts)): # Set the bounding box extents
            v = self.all_verts[i]
            if v.x < minx:
                minx = v.x
            if v.x > maxx:
                maxx = v.x
            if v.y < miny:
                miny = v.y
            if v.y > maxy:
                maxy = v.y
 
        vcx = minx + (maxx-minx)/2
        vcy = miny + (maxy-miny)/2
        # now center the verts based on this
        for i in range(len(self.all_verts)):
             self.all_verts[i].x -= vcx
             self.all_verts[i].y -= vcy

    def create_effect( self, type, fx,fy,fz, tx,ty,tz, secs, group):
        e = VectorEffect()
        e.type = type
        e.effect_value_start[0] = fx
        e.effect_value_start[1] = fy
        e.effect_value_start[2] = fz
        e.effect_value_end[0] = tx
        e.effect_value_end[1] = ty
        e.effect_value_end[2] = tz
        e.effect_time = e.effect_time_remaining = secs
        e.group = group
        e.complete = False
        return e

    def reset( self ):
        self.x_off = self.visWidth/2
        self.y_off = self.visHeight/2

        if self.use_effects:
            # Effect based mode, this example sets various effects in groups
            # and repeats certain groups
            # Effect parameters are 3 start values (RGB or XYZ, etc) and 3 end values, the time in seconds between them, and the goup number
            # Effects in the same group are processed at the same time, future groups don't start being processed unil all effects in
            # lower groups have been processed
            # For some effects only certain values are processed
            # EG, for text the first from parameter is the text to set, and the end value and timer are ignored (it's set immediately)
            # Similar for loading a shape, which you can do by adding a file containing the verts (from the shape editor) - https://instantarcade.github.io/ShapeEditor/
            self.add_effect( self.create_effect( VET_SET_WORD, "hackaday",0,0, 0,0,0, 2, 0) )
            self.add_effect( self.create_effect( VET_SET_COLOR, 255,0,0, 255,255,255, 1,0) )
            self.add_effect( self.create_effect( VET_SET_SCALE, 0.1,0.1,0.1, 3,3,1, 1,0) )
            
            self.add_effect( self.create_effect( VET_SET_SCALE, 3,3,1, 1,1,1, 1,1) )
            
            self.add_effect( self.create_effect( VET_SET_ROTATION, 0,0,0, 0,360,0, 1.5,2) )
            
            self.add_effect( self.create_effect( VET_SET_TRANSLATION, 0,0,0, -64,0,0, 1,3) )
            
            self.add_effect( self.create_effect( VET_SET_WORD, "supercon",0,0, 0,0,0, 2, 4) )
            self.add_effect( self.create_effect( VET_SET_TRANSLATION, 0,-40,0, 0,0,0, 0.5, 4) )
            self.add_effect( self.create_effect( VET_SET_COLOR, 255,255,255, 255,255,0, 2,4) )
            
            self.add_effect( self.create_effect( VET_SET_ROTATION, 0,0,0, 360,0,0, 1.5,5) )
            self.add_effect( self.create_effect( VET_SET_REPEAT, 5,0,0, 0,0,0, 2,6 ) ) # repeat group 5 twice

            self.add_effect( self.create_effect( VET_SET_ROTATION, 0,0,0, 0,0,0, 0,7) )
            self.add_effect( self.create_effect( VET_SET_ROTATION, 0,0,0, 0,0,45, 1.5,7) )
            self.add_effect( self.create_effect( VET_SET_TRANSLATION, 0,0,0, 0,0,-50, 1.5,7) )
            
            
            self.add_effect( self.create_effect( VET_SET_TRANSLATION, 0,0,0, 0,0,0, 0,8) )
            self.add_effect( self.create_effect( VET_SET_TRANSLATION, 0,0,0, 0,0,0, 0,8) )
            self.add_effect( self.create_effect( VET_SET_WORD, "eat",0,0, 0,0,0, 2, 8) )
            self.add_effect( self.create_effect( VET_SET_COLOR, 255,0,255, 255,0,255, 0,8) )
            self.add_effect( self.create_effect( VET_SET_ROTATION, 0,-90,0, 0,90,0, 0.5,8) )
            
            self.add_effect( self.create_effect( VET_SET_WORD, "sleep",0,0, 0,0,0, 2, 9) )
            self.add_effect( self.create_effect( VET_SET_COLOR, 0,255,0, 0,255,0, 0, 9) )
            self.add_effect( self.create_effect( VET_SET_ROTATION, 0,-90,0, 0,90,0, 0.5,9) )
            
            self.add_effect( self.create_effect( VET_SET_WORD, "hack",0,0, 0,0,0, 2, 10) )
            self.add_effect( self.create_effect( VET_SET_COLOR, 255,0,0, 255,0,0, 0, 10) )
            self.add_effect( self.create_effect( VET_SET_ROTATION, 0,-90,0, 0,90,0, 0.5,10) )
            
            self.add_effect( self.create_effect( VET_SET_WORD, "repeat",0,0, 0,0,0, 2, 11) )
            self.add_effect( self.create_effect( VET_SET_COLOR, 0,0,255, 0,0,255, 0, 11) )
            self.add_effect( self.create_effect( VET_SET_ROTATION, 0,-90,0, 0,90,0, 0.5,11) )
            
            self.add_effect( self.create_effect( VET_SET_REPEAT, 8,0,0, 0,0,0, 3, 13 ) ) # repeat group 8 3 times
            
            self.add_effect( self.create_effect( VET_SET_SHAPE, jollywrencher.verts,0,0, 0,0,0, 0, 14 ) ) # Set a shape
            self.add_effect( self.create_effect( VET_SET_ROTATION, 0,0,0, 0,0,0, 0.01,14) )
            self.add_effect( self.create_effect( VET_SET_COLOR, 255,255,255, 255,255,255, 2,14) )
            
            self.add_effect( self.create_effect( VET_SET_ROTATION, 0,0,0, 0,0,360, 1,15) )
            self.add_effect( self.create_effect( VET_SET_SCALE, 1,1,1, 0.15,0.15,0.15, 1,15) )
            
            self.add_effect( self.create_effect( VET_SET_REPEAT, 0,0,0, 0,0,0, -1, 20 ) ) # repeat everything indefinitely
        
    def constrain2pi2( self, value ):
        while value > math.pi*2:
            value -= math.pi*2
        while value < 0:
            value += math.pi*2
        return value
    
    @micropython.native
    def update( self, delta, display, accel ):
#         self.hue_offset += 1
#         self.hue_offset %= 360

        # we move the rotator for all the verts
        #self.x_rot += self.x_rot_speed * delta
        #self.y_rot += self.y_rot_speed * delta
#        self.z_rot += self.z_rot_speed * delta

##        self.size_wave += (math.pi/self.size_wave_speed)  * delta * 3
#        self.xo_wave += (math.pi/self.xo_speed) * delta
#        self.yo_wave += (math.pi/self.yo_speed) * delta

        # constrain angles to maintain precision
#         self.x_rot = self.constrain2pi2(self.x_rot)
#         self.y_rot = self.constrain2pi2(self.y_rot)
#         self.z_rot = self.constrain2pi2(self.z_rot)
#         self.size_wave = self.constrain2pi2(self.size_wave)
#         self.xo_wave = self.constrain2pi2(self.xo_wave)
#         self.yo_wave = self.constrain2pi2(self.yo_wave)
            
##        self.cube_size = 36 + math.sin(self.size_wave)*36
##        self.x_off = self.visWidth/2# + math.cos(self.xo_wave) *self.visWidth/3
##        self.y_off = self.visHeight/2# + math.sin(self.yo_wave) *self.visHeight/3


        focal = 3 #300 for flatter depth

        c = hsv_to_rgb_255(self.hue_offset,255,255)
        
        global_scale = [self.default_scale,self.default_scale,self.default_scale]
        global_rotation = [self.x_rot,self.y_rot,self.z_rot]
        global_translation = [0,0,0]
        
        # loop through active effects and set effect values appropriately
        low_group = -1
        high_group = -1
        for e in self.effects:
            if e.group < low_group or low_group == -1:
                low_group = e.group
            if e.group > high_group or high_group == -1:
                high_group = e.group
#         print( f"Low group {low_group}, High Group {high_group}")
        
        for group in range (low_group,high_group+1):
            this_group_complete = True
#             print( f"Processing Group {group}" )
            for e in self.effects:
#                 print(f"effect {e}, group {e.group}" )
                if e.group == group:
                    e.update( delta )
#                     print(f"Processing> Type:{e.type}, Remaining:{e.effect_time_remaining}, Complete:{e.complete}" )
                    if e.effect_complete == False:
                        this_group_complete = False
                    
                    ty = e.type
                    if ty == VET_SET_COLOR:
#                         print( f"Processing Color for effect {e} in group {e.group} (group is {group})" )
                        r = int(e.effect_value_current[0])
                        g = int(e.effect_value_current[1])
                        b = int(e.effect_value_current[2])
                        nr = r >> 3
                        ng = g >> 2
                        nb = b >> 3
                        c = (nr<<11) | (ng<<5) | nb
                    elif ty == VET_SET_SCALE:
#                         print( f"Processing Scale for effect {e} in group {e.group} (group is {group})" )
                        for i in range(3):
                            global_scale[i] = self.default_scale * e.effect_value_current[i]
                    elif ty == VET_SET_ROTATION:
#                         print( f"Processing Rotation for effect {e} in group {e.group} (group is {group})" )
                        for i in range(3):
                            global_rotation[i] = (e.effect_value_current[i]/180.0)*3.1415926585
                    elif ty == VET_SET_TRANSLATION:
#                         print( f"Processing Translation for effect {e} in group {e.group} (group is {group})" )
                        for i in range(3):
                            global_translation[i] = self.default_scale * e.effect_value_current[i]
                    elif ty == VET_SET_WORD:
                        if not e.effect_complete:
#                             print( f"Processing Set Word for effect {e} in group {e.group} (group is {group})" )
                            self.all_verts = []
                            self.add_word( e.effect_value_start[0] )
                            self.center_all()
#                             print( f"Setting word to {e.effect_value_start[0]}" )
                            e.effect_complete = True
                    elif ty == VET_SET_SHAPE:
                        self.load_shape( e.effect_value_start[0] )
                        e.effect_complete = True
                    elif ty == VET_PAUSE:
                        if not e.effect_complete:
#                             print( f"Processing Pause for effect {e} in group {e.group} (group is {group}) Effect time is {e.effect_time_remaining}" )
                            pass
                    elif ty == VET_SET_REPEAT:
                        if not e.effect_complete:
#                             print( f"Processing Repeat for effect {e} in group {e.group} (group is {group}) Repeat Count is {e.effect_time_remaining}" )
                            # first value is the group to repeat
                            # Time is repeat count
                            old_time = e.effect_time_remaining # store current count in case it gets reset
                            for eg in self.effects: # reset all the effects in the group an higher groups
                                if eg.group >= e.effect_value_start[0]:
                                    eg.reset()
                            if old_time > -1: # Respect finite repeat count
                                old_time -= 1
                                if old_time <= 0:
                                    e.effect_complete = True
                            e.effect_time_remaining = old_time
                            e.update(delta) # update this effect again
                            
                            
            if this_group_complete == False:
#                 print(f"Group {group} not all complete, ignoring higher groups" )
                break # don't process any higher groups this time around
            else:
#                 print(f"Group {group} complete!" )
                pass
                
        
        # Precalc for use on each vert
        sin_x = math.sin(global_rotation[0])
        cos_x = math.cos(global_rotation[0])
        
        sin_y = math.sin(global_rotation[1])
        cos_y = math.cos(global_rotation[1])
        
        sin_z = math.sin(global_rotation[2])
        cos_z = math.cos(global_rotation[2])

        # move all the verts
        for i in range(len(self.all_verts)):
            vert = self.all_verts[i]
            #scale
            tx = (global_translation[0]+vert.x)# * global_scale[0]
            ty = (global_translation[1]+vert.y)# * global_scale[1]
            tz = (global_translation[2]+vert.z)# * global_scale[2]

            #x rot
            fxy = (cos_x * ty) - (sin_x * tz)
            fxz = (sin_x * ty) + (cos_x * tz)
            
            #y rot
            fyz = (cos_y * fxz) - (sin_y * tx)
            fyx = (sin_y * fxz) + (cos_y * tx)
            
            #z rot
            fzx = (cos_z * fyx) - (sin_z * fxy)
            fzy = (sin_z * fyx) + (cos_z * fxy)

            #perspective
            focal = 45
            div = focal+fyz
            # avoid possible division by zero
            if div == 0:
                div = 0.0001
            scale_factor = focal / div
            lfx = fzx * scale_factor
            lfy = fzy * scale_factor
            lfz = fyz * scale_factor
                
            
            #translate to center
            vert.tx = lfx#  (lfx + self.x_off + global_translation[0])
            vert.ty = lfy# (lfy + self.y_off + global_translation[1])
            self.all_verts[i] = vert

            
        # Draw lines from all_verts
        p = display.create_pen(r,g,b)
        display.set_pen(p)
        for i in range(len(self.all_verts)):
            # each vert has an x, y, and shape index
            # if a vert has the same shape index as the previous one, draw a line
            # from this one to the previous one
            v = self.all_verts[i]
            if i > 0:
                vp = self.all_verts[i-1]
                if v.shapeIndex == vp.shapeIndex: # same shape?
                    display.line(int((vp.tx  * global_scale[0])+ self.x_off),
                                 int((vp.ty * global_scale[1]) + self.y_off),
                                 int((v.tx * global_scale[0]) + self.x_off),
                                 int((v.ty * global_scale[1]) + self.y_off) )
