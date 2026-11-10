"""Standalone Blender concept model for an east-facing 37.5 x 37 ft Vastu home.

Run with: blender --background --python chatgpt_god.py
Scene units are meters. This is a presentation concept, not a construction set.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND_OUT = ROOT + r"\chatgpt_god.blend"
RENDER_OUT = ROOT + r"\chatgpt_god.png"
INTERIOR_OUT = ROOT + r"\chatgpt_god_interior.png"
SURROUNDINGS_OUT = ROOT + r"\chatgpt_god_surroundings.png"
NEIGHBORHOOD_OUT = ROOT + r"\chatgpt_god_neighborhood.png"
FT = 0.3048
PLOT_X, PLOT_Y = 37.5 * FT, 37.0 * FT
X0, X1 = 3.0 * FT, 27.0 * FT
Y0, Y1 = 2.5 * FT, 34.0 * FT
FLOOR_H = 3.05
SLAB = 0.18
WALL_H = 2.70
WALL_T = 0.16


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


M = {}
M["ivory"] = material("Warm limestone | ivory", (0.79, 0.75, 0.67), .78)
M["white"] = material("Chalk white render", (.91, .89, .84), .72)
M["sand"] = material("Sandstone accent", (.62, .36, .23), .72)
M["wood"] = material("Teak battens", (.34, .18, .085), .42)
M["glass"] = material("Blue-grey glass", (.105, .25, .30), .18, .28)
M["metal"] = material("Dark bronze metal", (.075, .095, .10), .28, .65)
M["concrete"] = material("Pale concrete", (.40, .43, .42), .86)
M["paver"] = material("Entry pavers", (.64, .59, .50), .9)
M["grass"] = material("Garden green", (.13, .24, .13), .96)
M["leaf"] = material("Leaf green", (.16, .31, .16), .92)
M["trunk"] = material("Tree bark", (.20, .115, .06), .9)
M["water"] = material("Water tank blue", (.08, .26, .39), .3, .12)
M["car"] = material("Graphite blue car", (.10, .20, .27), .22, .6)
M["tyre"] = material("Tyre rubber", (.025, .03, .035), .9)
M["seat"] = material("Warm interior timber", (.40, .24, .12), .65)
M["fabric"] = material("Linen upholstery", (.66, .59, .47), .9)
M["sage"] = material("Muted sage fabric", (.31, .42, .37), .92)
M["tile"] = material("Interior pale terrazzo", (.68, .67, .62), .65)
M["ceramic"] = material("Bathroom ceramic", (.86, .88, .86), .24)
M["brass"] = material("Pooja brass", (.63, .38, .10), .26, .65)
M["asphalt"] = material("Neighborhood asphalt", (.115, .13, .14), .92)
M["neighbor"] = material("Neighbor home | warm plaster", (.69, .65, .57), .8)
M["neighbor2"] = material("Neighbor home | pale sage", (.52, .62, .55), .8)
M["roof"] = material("Neighbor home | graphite roof", (.20, .23, .24), .72)
M["flower"] = material("Garden flowers", (.75, .40, .25), .78)
M["roadmark"] = material("Road line | warm yellow", (.95, .72, .12), .56)
M["skin"] = material("Pedestrian | warm skin", (.64, .43, .29), .84)
M["pants"] = material("Pedestrian | charcoal clothing", (.16, .19, .20), .88)
M["shirt_blue"] = material("Pedestrian | indigo shirt", (.16, .30, .48), .8)
M["shirt_red"] = material("Pedestrian | rust shirt", (.56, .20, .15), .82)
M["shirt_gold"] = material("Pedestrian | ochre shirt", (.69, .46, .12), .84)
M["shop"] = material("Local shop | pale mint", (.48, .68, .59), .78)


def box(name, loc, size, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new("Soft architectural edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        ob.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return ob


def cube_between(name, a, b, thickness, mat):
    mid = (Vector(a) + Vector(b)) / 2
    direction = Vector(b) - Vector(a)
    ob = box(name, mid, (thickness, thickness, direction.length), mat)
    ob.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return ob


def window_south(name, x, z, width, height, y=Y0):
    # Exterior glazing sits within a true opening in the south wall.
    box(name + " | glass", (x, y - .018, z + height / 2), (width, .035, height), M["glass"])
    for xx in (x - width / 2, x + width / 2):
        box(name + " | jamb", (xx, y - .04, z + height / 2), (.055, .09, height + .06), M["metal"])
    box(name + " | head", (x, y - .04, z + height), (width + .08, .09, .055), M["metal"])
    box(name + " | sill", (x, y - .055, z), (width + .14, .18, .075), M["ivory"])


def window_east(name, y, z, width, height, x=X1):
    box(name + " | glass", (x + .018, y, z + height / 2), (.035, width, height), M["glass"])
    for yy in (y - width / 2, y + width / 2):
        box(name + " | jamb", (x + .04, yy, z + height / 2), (.09, .055, height + .06), M["metal"])
    box(name + " | head", (x + .04, y, z + height), (.09, width + .08, .055), M["metal"])
    box(name + " | sill", (x + .055, y, z), (.18, width + .14, .075), M["ivory"])


def south_wall(z, openings):
    # openings: (center x, width, sill, head)
    intervals = sorted((cx-w/2, cx+w/2, sill, head) for cx,w,sill,head in openings)
    cursor = X0
    for lo,hi,sill,head in intervals:
        if lo > cursor:
            box("South facade solid", ((cursor+lo)/2, Y0, z+WALL_H/2), (lo-cursor, WALL_T, WALL_H), M["white" if z > .1 else "ivory"])
        if sill > 0:
            box("South facade below window", ((lo+hi)/2, Y0, z+sill/2), (hi-lo, WALL_T, sill), M["ivory"])
        if WALL_H > head:
            box("South facade lintel", ((lo+hi)/2, Y0, z+(head+WALL_H)/2), (hi-lo, WALL_T, WALL_H-head), M["white"])
        cursor = hi
    if cursor < X1:
        box("South facade solid", ((cursor+X1)/2, Y0, z+WALL_H/2), (X1-cursor, WALL_T, WALL_H), M["white"])
    for i,(cx,w,sill,head) in enumerate(openings):
        window_south(f"South window {i+1}",cx,z+sill,w,head-sill)


def east_wall(z, openings):
    # openings: (center y, width, sill, head, kind)
    intervals = sorted((cy-w/2,cy+w/2,sill,head,kind) for cy,w,sill,head,kind in openings)
    cursor=Y0
    for lo,hi,sill,head,kind in intervals:
        if lo>cursor:
            box("East facade solid",(X1,(cursor+lo)/2,z+WALL_H/2),(WALL_T,lo-cursor,WALL_H),M["white"])
        if sill>0:
            box("East facade below opening",(X1,(lo+hi)/2,z+sill/2),(WALL_T,hi-lo,sill),M["ivory"])
        if WALL_H>head:
            box("East facade lintel",(X1,(lo+hi)/2,z+(head+WALL_H)/2),(WALL_T,hi-lo,WALL_H-head),M["white"])
        cursor=hi
    if cursor<Y1:
        box("East facade solid",(X1,(cursor+Y1)/2,z+WALL_H/2),(WALL_T,Y1-cursor,WALL_H),M["white"])
    for i,(cy,w,sill,head,kind) in enumerate(openings):
        if kind == "door":
            box("East entry | teak door",(X1+.10,cy,z+head/2),(.10,w-.10,head),M["wood"],.025)
            box("East entry | glazed sidelight",(X1+.075,cy+w*.37,z+head/2),(.045,w*.22,head-.1),M["glass"])
            box("East entry | canopy",(X1+.58,cy,z+head+.20),(1.15,w+.65,.14),M["wood"],.04)
        else:
            window_east(f"East window {i+1}",cy,z+sill,w,head-sill)


def floor_shell(level, south_openings, east_openings, north_windows=False):
    z=level*FLOOR_H
    box(f"Level {level} | floor slab",((X0+X1)/2,(Y0+Y1)/2,z),(X1-X0,Y1-Y0,SLAB),M["concrete"],.035)
    wall_z=z+SLAB/2
    south_wall(wall_z,south_openings)
    east_wall(wall_z,east_openings)
    # North and west walls keep the building envelope simple; slim windows mark bedrooms.
    box("North facade",((X0+X1)/2,Y1,wall_z+WALL_H/2),(X1-X0,WALL_T,WALL_H),M["white"])
    box("West facade",(X0,(Y0+Y1)/2,wall_z+WALL_H/2),(WALL_T,Y1-Y0,WALL_H),M["ivory"])
    if north_windows:
        for wx in (X0+1.4,X0+4.4,X0+6.6):
            box("North clerestory glass",(wx,Y1+.025,wall_z+1.55),(1.25,.04,1.05),M["glass"])
            box("North window cap",(wx,Y1+.055,wall_z+2.10),(1.38,.11,.06),M["metal"])
    # East and south corner pilasters add a strong frame to the glass.
    for yy in (Y0+.08,Y1-.08):
        box("East sandstone pilaster",(X1+.05,yy,z+FLOOR_H/2),(.26,.22,FLOOR_H-.12),M["sand"],.025)


def railing_east(name,z,center_y,width,height=1.0):
    yy0=center_y-width/2
    box(name+" | bottom rail",(X1+.72,center_y,z+.10),(.07,width,.07),M["metal"])
    box(name+" | top rail",(X1+.72,center_y,z+height),(.07,width,.07),M["metal"])
    for i in range(9):
        yy=yy0+width*i/8
        box(name+" | baluster",(X1+.72,yy,z+height/2),(.045,.045,height),M["metal"])


def plant(name,x,y,z=0,scale=1.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=.11*scale,depth=.55*scale,location=(x,y,z+.275*scale))
    bpy.context.object.name=name+" | trunk"; bpy.context.object.data.materials.append(M["trunk"])
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.62*scale,location=(x,y,z+.88*scale))
    bpy.context.object.name=name+" | canopy"; bpy.context.object.data.materials.append(M["leaf"])


def car(x,y,body_material=None,prefix="Compact car",base_z=0.0):
    body_material=body_material or M["car"]
    box(prefix+" | body",(x,y,.53+base_z),(1.82,4.0,.62),body_material,.18)
    box(prefix+" | cabin",(x,y+.05,1.06+base_z),(1.53,2.12,.70),M["glass"],.17)
    box(prefix+" | hood",(x,y-1.38,.87+base_z),(1.55,1.12,.18),body_material,.08)
    for yy in (y-1.28,y+1.28):
        for xx in (x-.91,x+.91):
            bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.34,depth=.18,location=(xx,yy,.39+base_z),rotation=(0,math.pi/2,0))
            bpy.context.object.name=prefix+" | wheel"; bpy.context.object.data.materials.append(M["tyre"])


def fx(value):
    return value * FT


def interior_box(name, center, size, mat, bevel=0.0):
    return box("INTERIOR | " + name, center, size, mat, bevel)


def partition_x(name, x_ft, y0_ft, y1_ft, z, door_y_ft=None, door_w_ft=2.7, height=2.36):
    """Interior wall running north-south, with an optional doorway."""
    x=fx(x_ft); a=fx(y0_ft); b=fx(y1_ft); t=.10
    lo=fx(door_y_ft)-fx(door_w_ft)/2 if door_y_ft is not None else b
    hi=fx(door_y_ft)+fx(door_w_ft)/2 if door_y_ft is not None else b
    if lo>a:
        interior_box(name+" | wall",(x,(a+lo)/2,z+height/2),(t,lo-a,height),M["white"])
    if hi<b:
        interior_box(name+" | wall",(x,(hi+b)/2,z+height/2),(t,b-hi,height),M["white"])
    if door_y_ft is not None:
        interior_box(name+" | lintel",(x,(lo+hi)/2,z+2.12),(t,hi-lo,height-2.12),M["white"])


def partition_y(name, y_ft, x0_ft, x1_ft, z, door_x_ft=None, door_w_ft=2.7, height=2.36):
    """Interior wall running east-west, with an optional doorway."""
    y=fx(y_ft); a=fx(x0_ft); b=fx(x1_ft); t=.10
    lo=fx(door_x_ft)-fx(door_w_ft)/2 if door_x_ft is not None else b
    hi=fx(door_x_ft)+fx(door_w_ft)/2 if door_x_ft is not None else b
    if lo>a:
        interior_box(name+" | wall",((a+lo)/2,y,z+height/2),(lo-a,t,height),M["white"])
    if hi<b:
        interior_box(name+" | wall",((hi+b)/2,y,z+height/2),(b-hi,t,height),M["white"])
    if door_x_ft is not None:
        interior_box(name+" | lintel",((lo+hi)/2,y,z+2.12),(hi-lo,t,height-2.12),M["white"])


def bed(name, x_ft, y_ft, z, width_ft=6.0, length_ft=6.7, fabric=None):
    x,y=fx(x_ft),fx(y_ft); w,l=fx(width_ft),fx(length_ft)
    interior_box(name+" | timber frame",(x,y,z+.22),(w,l,.36),M["wood"],.045)
    interior_box(name+" | mattress",(x,y,z+.43),(w-.08,l-.08,.20),M["fabric"],.07)
    interior_box(name+" | duvet",(x,y-fx(.25),z+.55),(w-.18,l*.60,.07),fabric or M["sage"],.055)
    interior_box(name+" | headboard",(x,y-l/2+.09,z+.72),(w+.10,.17,1.22),M["wood"],.035)
    for side in (-1,1):
        interior_box(name+" | pillow",(x+side*w*.23,y+l*.25,z+.62),(w*.37,l*.20,.10),M["ceramic"],.035)
        interior_box(name+" | bedside",(x+side*(w/2+.24),y-l/2+.28,z+.37),(.42,.46,.64),M["seat"],.045)


def sofa(name, x_ft, y_ft, z, width_ft=7.0, depth_ft=2.7, mat=None, rotation=0.0):
    x,y=fx(x_ft),fx(y_ft); w,d=fx(width_ft),fx(depth_ft); cloth=mat or M["fabric"]
    c,s=math.cos(rotation),math.sin(rotation)

    def part(label, local_x, local_y, local_z, size, material, bevel):
        center=(x+c*local_x-s*local_y,y+s*local_x+c*local_y,z+local_z)
        if abs(s)>.5:
            size=(size[1],size[0],size[2])
        ob=interior_box(name+" | "+label,center,size,material,bevel)
        ob.rotation_euler.z=rotation

    part("base",0,0,.30,(w,d,.48),cloth,.10)
    part("back",0,d/2-.10,.78,(w,.22,.94),M["seat"],.07)
    for i in range(3):
        lx=-w/3+i*w/3
        part("cushion",lx,0,.57,(w/3-.035,d-.18,.16),cloth,.05)
    for lx in (-w/2+.12,w/2-.12):
        part("arm",lx,0,.64,(.22,d,.68),M["seat"],.06)


def add_stairs(level, x_ft=4.8, y_ft=22.8, count=13):
    z0=level*FLOOR_H+SLAB/2
    width=fx(3.3); run=fx(9.7)/count; rise=(FLOOR_H-SLAB)/count
    x=fx(x_ft)
    for i in range(count):
        h=rise*(i+1)
        interior_box(f"L{level} stair tread {i+1}",(x,y_ft*FT+run*i+run/2,z0+h/2),(width,run,h),M["seat"],.018)
    interior_box(f"L{level} stair handrail",(x+width/2+.08,fx(y_ft+4.8),z0+1.0),(.055,fx(9.7),.08),M["wood"])


def add_furnishings():
    """Furnish and partition three levels according to the east-facing concept."""
    # Ground floor: SW bedroom; SE kitchen; central living/dining; NE pooja; NW stairs.
    z0=SLAB/2
    partition_x("L0 | guest bedroom east wall",15.8,2.8,15.3,z0,door_y_ft=13.2)
    partition_y("L0 | guest bedroom north wall",15.3,3.0,15.8,z0,door_x_ft=14.2)
    partition_x("L0 | kitchen west wall",17.0,2.8,13.2,z0,door_y_ft=11.4)
    partition_y("L0 | kitchen north wall",13.0,17.0,27.0,z0,door_x_ft=18.5)
    partition_x("L0 | bath east wall",10.0,15.3,21.5,z0,door_y_ft=20.0,door_w_ft=2.4)
    partition_y("L0 | bath south wall",21.5,3.0,10.0,z0,door_x_ft=8.5,door_w_ft=2.4)
    partition_x("L0 | stair east screen",10.5,21.5,34.0,z0)
    partition_y("L0 | pooja south wall",26.5,21.0,27.0,z0,door_x_ft=22.2,door_w_ft=2.4)
    partition_x("L0 | pooja west wall",21.0,26.5,34.0,z0,door_y_ft=29.0,door_w_ft=2.4)
    # bedroom finish and queen bed with head to the south.
    interior_box("L0 | bedroom rug",(fx(9.2),fx(8.7),z0+.025),(fx(9.8),fx(8.5),.035),M["tile"],.04)
    bed("L0 | elder guest bed",9.2,8.3,z0,width_ft=6.0,length_ft=6.4)
    interior_box("L0 | bedroom wardrobe",(fx(4.4),fx(10.7),z0+1.05),(fx(1.7),fx(5.7),2.1),M["wood"],.055)
    # Kitchen counters, tall pantry, sink, hob and stools.
    interior_box("L0 | kitchen south counter",(fx(21.6),fx(3.5),z0+.47),(fx(8.5),fx(1.35),.90),M["seat"],.05)
    interior_box("L0 | kitchen counter top",(fx(21.6),fx(3.5),z0+.94),(fx(8.65),fx(1.42),.07),M["ceramic"],.025)
    interior_box("L0 | kitchen east counter",(fx(25.8),fx(8.0),z0+.47),(fx(1.3),fx(7.7),.90),M["seat"],.045)
    interior_box("L0 | kitchen hob",(fx(18.3),fx(3.5),z0+1.01),(fx(1.45),fx(.78),.08),M["metal"],.025)
    for xx in (17.9,18.5,19.1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.095,depth=.055,location=(fx(xx),fx(3.5),z0+1.08))
        bpy.context.object.name="INTERIOR | L0 | hob burner"; bpy.context.object.data.materials.append(M["brass"])
    interior_box("L0 | kitchen sink",(fx(25.75),fx(9.0),z0+.99),(fx(.80),fx(1.2),.075),M["metal"],.06)
    interior_box("L0 | kitchen pantry",(fx(26.0),fx(4.5),z0+1.25),(fx(1.05),fx(1.2),2.45),M["white"],.035)
    # Dining and living in the open Brahmasthan zone.
    interior_box("L0 | dining rug",(fx(16.6),fx(18.5),z0+.025),(fx(8.5),fx(6.0),.035),M["fabric"],.05)
    interior_box("L0 | dining table",(fx(16.7),fx(18.2),z0+.80),(fx(5.0),fx(3.2),.13),M["wood"],.055)
    for xx in (14.9,18.5):
        for yy in (16.9,19.5):
            interior_box("L0 | dining chair seat",(fx(xx),fx(yy),z0+.49),(fx(1.15),fx(1.05),.14),M["sage"],.045)
            interior_box("L0 | dining chair back",(fx(xx),fx(yy+.40),z0+.89),(fx(1.15),.12,.76),M["wood"],.035)
    interior_box("L0 | living rug",(fx(16.2),fx(24.1),z0+.03),(fx(9.8),fx(5.1),.04),M["fabric"],.045)
    sofa("L0 | living sofa",14.0,24.8,z0,width_ft=7.4,depth_ft=2.5)
    sofa("L0 | living loveseat",11.9,21.9,z0,width_ft=5.0,depth_ft=2.3,mat=M["sage"])
    interior_box("L0 | coffee table",(fx(16.0),fx(22.5),z0+.40),(fx(3.1),fx(1.7),.16),M["wood"],.07)
    interior_box("L0 | media console",(fx(11.0),fx(25.4),z0+.45),(fx(4.6),fx(.70),.82),M["seat"],.04)
    interior_box("L0 | foyer console",(fx(24.5),fx(13.2),z0+.48),(fx(1.0),fx(3.0),.88),M["wood"],.04)
    # NE pooja room: floating altar, brass lamps and a small shrine plinth.
    interior_box("L0 | pooja floor inset",(fx(24.0),fx(30.4),z0+.04),(fx(5.3),fx(6.7),.07),M["tile"],.035)
    interior_box("L0 | pooja altar",(fx(25.7),fx(30.6),z0+.76),(fx(.62),fx(3.5),1.35),M["wood"],.045)
    interior_box("L0 | pooja back panel",(fx(26.55),fx(30.6),z0+1.46),(.10,fx(3.5),1.80),M["seat"],.025)
    for yy in (29.7,30.6,31.5):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.12,location=(fx(25.32),fx(yy),z0+1.36))
        bpy.context.object.name="INTERIOR | L0 | brass shrine ornament"; bpy.context.object.data.materials.append(M["brass"])
    # Compact common bath, with practical fixtures.
    interior_box("L0 | bath floor",(fx(6.4),fx(18.4),z0+.035),(fx(6.0),fx(5.8),.05),M["tile"])
    interior_box("L0 | bath vanity",(fx(4.0),fx(20.3),z0+.52),(fx(1.8),fx(.8),.85),M["wood"],.04)
    interior_box("L0 | bath basin",(fx(4.0),fx(20.3),z0+.98),(fx(1.25),fx(.54),.08),M["ceramic"],.055)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.23,depth=.43,location=(fx(8.2),fx(17.2),z0+.25))
    bpy.context.object.name="INTERIOR | L0 | bath toilet"; bpy.context.object.data.materials.append(M["ceramic"])
    interior_box("L0 | shower screen",(fx(8.7),fx(19.2),z0+1.08),(.04,fx(2.5),2.05),M["glass"])
    add_stairs(0)

    # First floor: master SW, secondary bedrooms east/north, lounge in the centre.
    z1=FLOOR_H+SLAB/2
    partition_x("L1 | master east wall",17.0,2.8,16.5,z1,door_y_ft=14.4)
    partition_y("L1 | master north wall",16.0,3.0,17.0,z1,door_x_ft=15.3)
    partition_x("L1 | bedroom 2 west wall",18.0,2.8,14.5,z1,door_y_ft=13.0)
    partition_y("L1 | bedroom 2 north wall",14.5,18.0,27.0,z1,door_x_ft=19.0)
    partition_y("L1 | bedroom 3 south wall",23.0,12.0,27.0,z1,door_x_ft=17.5)
    partition_x("L1 | bedroom 3 west wall",12.0,23.0,34.0,z1,door_y_ft=24.5)
    partition_x("L1 | bath west wall",10.0,16.0,22.0,z1,door_y_ft=20.5,door_w_ft=2.4)
    partition_y("L1 | bath south wall",16.0,10.0,15.0,z1,door_x_ft=13.8,door_w_ft=2.4)
    bed("L1 | master bed",9.6,8.5,z1,width_ft=6.5,length_ft=7.0,fabric=M["fabric"])
    interior_box("L1 | master rug",(fx(9.5),fx(9.1),z1+.025),(fx(10.5),fx(9.1),.035),M["tile"],.04)
    interior_box("L1 | master wardrobe",(fx(4.4),fx(11.5),z1+1.15),(fx(1.6),fx(6.0),2.25),M["wood"],.05)
    bed("L1 | bedroom 2 bed",22.7,8.6,z1,width_ft=5.7,length_ft=6.2,fabric=M["sage"])
    interior_box("L1 | bedroom 2 wardrobe",(fx(25.4),fx(11.3),z1+1.05),(fx(1.2),fx(4.5),2.1),M["wood"],.04)
    bed("L1 | bedroom 3 bed",21.7,28.2,z1,width_ft=5.8,length_ft=6.4)
    interior_box("L1 | bedroom 3 desk",(fx(25.0),fx(25.2),z1+.72),(fx(3.3),fx(1.5),.12),M["wood"],.04)
    interior_box("L1 | family lounge rug",(fx(16.5),fx(18.9),z1+.025),(fx(9.2),fx(7.5),.035),M["tile"],.04)
    sofa("L1 | family lounge sofa",15.8,21.5,z1,width_ft=7.0,depth_ft=2.4,mat=M["sage"])
    interior_box("L1 | family coffee table",(fx(16.0),fx(18.7),z1+.40),(fx(2.8),fx(1.6),.14),M["wood"],.06)
    interior_box("L1 | bath vanity",(fx(12.0),fx(20.6),z1+.50),(fx(2.2),fx(.75),.82),M["seat"],.04)
    interior_box("L1 | bath basin",(fx(12.0),fx(20.6),z1+.94),(fx(1.5),fx(.55),.07),M["ceramic"],.04)
    add_stairs(1)

    # Third level: furnished yoga/music pavilion and an outdoor dining nook on terrace.
    z2=2*FLOOR_H+SLAB/2
    interior_box("L2 | pavilion yoga mat",(fx(11.2),fx(9.0),z2+.06),(fx(5.8),fx(2.1),.07),M["sage"],.035)
    interior_box("L2 | pavilion lounge rug",(fx(11.4),fx(14.2),z2+.04),(fx(10.0),fx(5.4),.04),M["tile"],.04)
    sofa("L2 | pavilion daybed",10.7,14.6,z2,width_ft=6.2,depth_ft=2.1)
    interior_box("L2 | pavilion bookcase",(fx(4.5),fx(12.4),z2+1.05),(fx(.7),fx(5.4),2.1),M["wood"],.045)
    # East/north terrace: dining table, lounge chairs, planters and side tables.
    interior_box("L2 | terrace dining table",(fx(23.5),fx(26.7),z2+.80),(fx(4.3),fx(2.8),.13),M["wood"],.055)
    for xx in (21.8,25.2):
        for yy in (25.1,28.3):
            interior_box("L2 | terrace dining chair",(fx(xx),fx(yy),z2+.48),(fx(1.0),fx(1.0),.14),M["fabric"],.05)
    sofa("L2 | terrace lounge",24.0,20.0,z2,width_ft=5.0,depth_ft=2.0,mat=M["sage"],rotation=-math.pi/2)
    interior_box("L2 | terrace coffee table",(fx(20.0),fx(20.0),z2+.40),(fx(2.4),fx(1.3),.14),M["wood"],.055)
    for xx,yy in ((20.2,31.8),(25.8,31.6),(19.8,16.8),(26.0,15.6)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.24,depth=.42,location=(fx(xx),fx(yy),z2+.25))
        bpy.context.object.name="INTERIOR | L2 | terrace planter"; bpy.context.object.data.materials.append(M["sand"])
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.34,location=(fx(xx),fx(yy),z2+.72))
        bpy.context.object.name="INTERIOR | L2 | terrace plant"; bpy.context.object.data.materials.append(M["leaf"])


def collect_interiors():
    scene=bpy.context.scene
    collection=bpy.data.collections.new("INTERIORS | furnished, Vastu-zoned")
    scene.collection.children.link(collection)
    for ob in list(scene.objects):
        if ob.name.startswith("INTERIOR |"):
            for old in list(ob.users_collection):
                old.objects.unlink(ob)
            collection.objects.link(ob)


def neighbor_home(name, x0, y0, width, depth, height, wall_mat):
    """Small, deliberately quiet neighboring villas beyond the east street."""
    cx=x0+width/2; cy=y0+depth/2
    box("CONTEXT | "+name+" | garden pad",(cx,cy,-.18),(width+1.0,depth+1.0,.20),M["grass"],.035)
    box("CONTEXT | "+name+" | house body",(cx,cy,height/2),(width,depth,height),wall_mat,.065)
    box("CONTEXT | "+name+" | roof edge",(cx,cy,height+.10),(width+.24,depth+.24,.20),M["roof"],.035)
    # Street-facing west windows and a recessed entry make the context read as homes.
    for level in range(max(1,int(height//2.7))):
        wz=.95+level*2.75
        if wz+1.0 < height:
            for wy in (y0+depth*.34,y0+depth*.72):
                box("CONTEXT | "+name+" | street window",(x0-.025,wy,wz+.50),(.045,.95,1.0),M["glass"])
                box("CONTEXT | "+name+" | window hood",(x0-.07,wy,wz+1.04),(.13,1.12,.09),M["white"])
                # East and south windows face the overview camera so the houses read as homes.
                box("CONTEXT | "+name+" | east window",(x0+width+.025,wy,wz+.50),(.045,.95,1.0),M["glass"])
                box("CONTEXT | "+name+" | east window hood",(x0+width+.07,wy,wz+1.04),(.13,1.12,.09),M["white"])
            for wx in (x0+width*.34,x0+width*.72):
                box("CONTEXT | "+name+" | south window",(wx,y0-.025,wz+.50),(.95,.045,1.0),M["glass"])
                box("CONTEXT | "+name+" | south window hood",(wx,y0-.07,wz+1.04),(1.12,.13,.09),M["white"])
    box("CONTEXT | "+name+" | entry door",(x0-.03,y0+depth*.12,1.05),(.08,.92,2.10),M["wood"],.025)
    box("CONTEXT | "+name+" | east entry",(x0+width+.035,y0+depth*.15,1.02),(.08,.86,2.04),M["wood"],.025)
    # Low garden wall, with a clear path from the public sidewalk.
    for yy in (y0-.45,y0+depth+.45):
        box("CONTEXT | "+name+" | garden wall",(cx,yy,.42),(width+1.0,.12,.84),M["white"],.025)
    box("CONTEXT | "+name+" | side wall",(x0+width+.45,cy,.42),(.12,depth+1.0,.84),M["white"],.025)
    for i in range(3):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.34,location=(x0+.75+i*1.0,y0+.65,.37))
        bpy.context.object.name="CONTEXT | "+name+" | hedge"; bpy.context.object.data.materials.append(M["leaf"])


def street_tree(x,y,scale=1.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.13*scale,depth=1.9*scale,location=(x,y,.95*scale))
    bpy.context.object.name="CONTEXT | street tree trunk"; bpy.context.object.data.materials.append(M["trunk"])
    for dx,dy,r in ((0,0,.78),(-.40,.15,.55),(.38,-.12,.58)):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=r*scale,location=(x+dx*scale,y+dy*scale,2.0*scale))
        bpy.context.object.name="CONTEXT | street tree canopy"; bpy.context.object.data.materials.append(M["leaf"])
    box("CONTEXT | street tree pit",(x,y,.04),(1.25*scale,1.25*scale,.08),M["grass"],.04)


def streetlight(x,y):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.065,depth=4.7,location=(x,y,2.35))
    bpy.context.object.name="CONTEXT | streetlight pole"; bpy.context.object.data.materials.append(M["metal"])
    box("CONTEXT | streetlight arm",(x-.45,y,4.55),(.95,.07,.07),M["metal"],.025)
    box("CONTEXT | streetlight head",(x-.88,y,4.48),(.40,.20,.16),M["brass"],.04)


def neighborhood_shop(x0,y0):
    width,depth,height=4.5,4.2,3.45
    cx=x0+width/2; cy=y0+depth/2
    box("CONTEXT | Corner Shop | garden pad",(cx,cy,-.18),(width+1.0,depth+1.0,.20),M["paver"],.035)
    box("CONTEXT | Corner Shop | body",(cx,cy,height/2),(width,depth,height),M["shop"],.055)
    box("CONTEXT | Corner Shop | roof",(cx,cy,height+.12),(width+.28,depth+.28,.24),M["roof"],.04)
    # Glazed west-facing storefront and a deep shade canopy.
    box("CONTEXT | Corner Shop | display glass",(x0-.04,cy,1.52),(.06,2.75,2.35),M["glass"])
    box("CONTEXT | Corner Shop | front door",(x0-.09,y0+.52,1.08),(.11,.88,2.16),M["wood"],.025)
    box("CONTEXT | Corner Shop | awning",(x0-.34,cy,2.83),(.72,depth+.2,.16),M["sand"],.035)
    box("CONTEXT | Corner Shop | signboard",(x0-.16,cy,3.22),(.12,3.65,.48),M["wood"],.025)
    # Camera-facing east shopfront and its sign.
    box("CONTEXT | Corner Shop | east display glass",(x0+width+.04,cy,1.52),(.06,2.75,2.35),M["glass"])
    box("CONTEXT | Corner Shop | east entry",(x0+width+.09,y0+.52,1.08),(.11,.88,2.16),M["wood"],.025)
    box("CONTEXT | Corner Shop | east awning",(x0+width+.34,cy,2.83),(.72,depth+.2,.16),M["sand"],.035)
    box("CONTEXT | Corner Shop | east signboard",(x0+width+.16,cy,3.22),(.12,3.65,.48),M["wood"],.025)
    for yy in (y0+depth*.67,y0+depth*.83):
        box("CONTEXT | Corner Shop | shelf",(x0+.52,yy,1.20),(.38,.10,1.75),M["seat"])
    text_curve=bpy.data.curves.new("Corner shop sign lettering","FONT")
    text_curve.body="CORNER SHOP"
    text_curve.size=.31
    text_curve.extrude=.003
    text_obj=bpy.data.objects.new("CONTEXT | Corner Shop | lettering",text_curve)
    bpy.context.scene.collection.objects.link(text_obj)
    text_obj.location=(x0-.235,cy+.55,3.08)
    text_obj.rotation_euler=(math.pi/2,0,-math.pi/2)
    text_obj.data.materials.append(M["white"])
    east_text_curve=bpy.data.curves.new("Corner shop east sign lettering","FONT")
    east_text_curve.body="CORNER SHOP"
    east_text_curve.size=.31
    east_text_curve.extrude=.003
    east_text=bpy.data.objects.new("CONTEXT | Corner Shop | east lettering",east_text_curve)
    bpy.context.scene.collection.objects.link(east_text)
    east_text.location=(x0+width+.235,cy-.55,3.08)
    east_text.rotation_euler=(math.pi/2,0,math.pi/2)
    east_text.data.materials.append(M["white"])
    for yy in (y0-.48,y0+depth+.48):
        box("CONTEXT | Corner Shop | planter wall",(cx,yy,.38),(width+1.0,.12,.76),M["white"],.02)


def person_limb(name,start,end,radius,mat):
    a=Vector(start); b=Vector(end); direction=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=radius,depth=direction.length,location=(a+b)/2)
    ob=bpy.context.object
    ob.name="CONTEXT | "+name
    ob.rotation_euler=direction.to_track_quat("Z","Y").to_euler()
    ob.data.materials.append(mat)


def context_person(name,x,y,z,yaw,shirt):
    # Low-poly people are placed on the sidewalks and by the shop, away from the house facade.
    forward=Vector((math.sin(yaw),-math.cos(yaw),0))
    right=Vector((math.cos(yaw),math.sin(yaw),0))
    center=Vector((x,y,z))
    torso=box("CONTEXT | "+name+" | torso",center+Vector((0,0,1.03)),(.38,.26,.69),shirt,.07)
    torso.rotation_euler.z=yaw
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.14,location=center+Vector((0,0,1.55)))
    bpy.context.object.name="CONTEXT | "+name+" | head"; bpy.context.object.data.materials.append(M["skin"])
    for side in (-1,1):
        hip=center+right*(side*.105)+Vector((0,0,.40))
        knee=center+right*(side*.12)+forward*.03+Vector((0,0,.22))
        foot=center+right*(side*.12)+forward*.10+Vector((0,0,.08))
        person_limb(name+" | leg",hip,knee,.075,M["pants"])
        person_limb(name+" | shin",knee,foot,.060,M["pants"])
        shoulder=center+right*(side*.22)+Vector((0,0,1.27))
        wrist=center+right*(side*.33)+forward*.03+Vector((0,0,.85))
        person_limb(name+" | arm",shoulder,wrist,.055,shirt)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.065,location=wrist)
        bpy.context.object.name="CONTEXT | "+name+" | hand"; bpy.context.object.data.materials.append(M["skin"])


def create_surroundings():
    """Add a larger, walkable neighborhood around the unchanged plot."""
    box("CONTEXT | ground beyond plot",(10.0,7.0,-.49),(70.0,80.0,.14),M["grass"],.06)
    road_x=PLOT_X+3.60
    # Main two-lane street extends through the enlarged district.
    for yc,length in ((-14.6,28.4),(24.5,25.8)):
        box("CONTEXT | wide road extension",(road_x,yc,-.39),(7.20,length,.12),M["asphalt"])
    for x in (road_x-.09,road_x+.09):
        for yc in range(-28,39,5):
            box("CONTEXT | double yellow road marking",(x,yc,-.315),(.075,2.5,.015),M["roadmark"],.01)
    for x in (PLOT_X+.16,PLOT_X+7.04):
        box("CONTEXT | white road edge line",(x,5.0,-.315),(.045,70.0,.015),M["white"])

    cross_y=PLOT_Y+3.60
    box("CONTEXT | north cross street",(-1.8,cross_y,-.39),(27.0,5.60,.12),M["asphalt"])
    for xc in range(-14,12,5):
        box("CONTEXT | cross street lane marking",(xc,cross_y,-.315),(1.25,.045,.015),M["white"])
    # A second east-west connector joins the expanded rows and side streets.
    connector_y=39.0
    box("CONTEXT | north city connector",(14.0,connector_y,-.39),(62.0,5.60,.12),M["asphalt"])
    for xc in range(-15,45,5):
        box("CONTEXT | city connector lane marking",(xc,connector_y,-.315),(1.35,.045,.015),M["white"])

    service_x=PLOT_X+15.4
    service_x2=37.0
    west_lane_x=-12.2
    side_lanes=(west_lane_x,service_x,service_x2)
    for lane_x,label in ((west_lane_x,"west"),(service_x,"neighborhood"),(service_x2,"outer")):
        box(f"CONTEXT | {label} access lane",(lane_x,5.0,-.39),(3.25,70.0,.12),M["asphalt"])
        for yc in range(-28,39,5):
            box(f"CONTEXT | {label} lane marking",(lane_x,yc,-.315),(.04,1.0,.015),M["white"])
        for edge in (-1,1):
            box(f"CONTEXT | {label} curb",(lane_x+edge*1.70,5.0,-.24),(.12,70.0,.26),M["concrete"],.025)
        # Zebra crossings make the new street connections legible to drivers.
        for i in range(5):
            box(f"CONTEXT | {label} connector crosswalk",(lane_x+(i-2)*.62,connector_y,-.315),(.38,.82,.015),M["white"],.01)

    sidewalk_x=PLOT_X+7.62
    box("CONTEXT | east sidewalk",(sidewalk_x,5.0,-.28),(.72,70.0,.15),M["paver"],.035)
    box("CONTEXT | east curb",(PLOT_X+7.24,5.0,-.24),(.14,70.0,.26),M["concrete"],.025)
    box("CONTEXT | west curb",(PLOT_X+.03,5.0,-.24),(.14,70.0,.26),M["concrete"],.025)
    box("CONTEXT | north sidewalk",(-1.8,cross_y+3.12,-.28),(27.0,.70,.15),M["paver"],.035)
    for lane_x,label in ((service_x,"far-row"),(service_x2,"outer-row"),(west_lane_x,"west-row")):
        sx=lane_x+2.05 if lane_x>0 else lane_x+2.0
        box(f"CONTEXT | {label} sidewalk",(sx,5.0,-.28),(.55,70.0,.15),M["paver"],.035)
    box("CONTEXT | north connector sidewalk",(14.0,connector_y+3.12,-.28),(62.0,.70,.15),M["paver"],.035)
    for i in range(9):
        box("CONTEXT | junction crosswalk",(PLOT_X+.55+i*.72,cross_y,-.315),(.38,3.8,.018),M["white"],.01)

    # Twenty-nine compact villas in four residential rows around the original house.
    near_y=(-14.0,-7.0,0.0,21.0,28.0)
    far_y=(-17.0,-11.0,-5.0,1.0,7.0,21.0,28.0)
    home_colors=(M["neighbor"],M["neighbor2"],M["white"])
    n=1
    for i,yc in enumerate(near_y):
        h=3.2+(i%3)*.45
        neighbor_home(f"Villa {n:02d}",PLOT_X+8.55,yc-2.0,3.55,4.0,h,home_colors[i%3]); n+=1
    for i,yc in enumerate(far_y):
        h=3.0+(i%3)*.50
        neighbor_home(f"Villa {n:02d}",PLOT_X+19.75,yc-1.9,3.65,3.8,h,home_colors[(i+1)%3]); n+=1
    for i,yc in enumerate(far_y):
        h=3.0+(i%3)*.50
        neighbor_home(f"Villa {n:02d}",PLOT_X+28.7,yc-1.9,3.65,3.8,h,home_colors[(i+2)%3]); n+=1
    west_y=(-17.0,-11.0,-5.0,1.0,7.0,28.0,30.0)
    for i,yc in enumerate(west_y):
        h=3.0+(i%3)*.45
        neighbor_home(f"Villa {n:02d}",-8.9,yc-2.0,3.65,4.0,h,home_colors[(i+1)%3]); n+=1
    for i,xc in enumerate((-11.5,-6.3,-1.1)):
        neighbor_home(f"Villa {n:02d}",xc,cross_y+4.6,3.35,3.6,3.1+(i%2)*.5,home_colors[(i+2)%3]); n+=1
    neighborhood_shop(PLOT_X+8.55,cross_y-2.1)

    # A small pocket park gives residents a green shared space.
    park_x,park_y=-19.2,24.3
    box("CONTEXT | pocket park lawn",(park_x,park_y,-.29),(7.6,8.2,.18),M["grass"],.08)
    box("CONTEXT | pocket park path",(park_x,park_y,-.145),(.82,7.65,.07),M["paver"],.04)
    for bx,by in ((-21.5,22.0),(-21.5,26.2)):
        box("CONTEXT | park bench seat",(bx,by,.31),(1.5,.46,.12),M["wood"],.05)
        box("CONTEXT | park bench back",(bx,by+.22,.72),(1.5,.10,.82),M["wood"],.04)
        for dx in (-.55,.55):
            box("CONTEXT | park bench leg",(bx+dx,by,.02),(.10,.10,.44),M["metal"])
    for tx,ty in ((-22.1,21.3),(-16.2,21.2),(-22.0,27.5),(-16.1,27.4)):
        street_tree(tx,ty,.62)
    for i in range(5):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.18,location=(-23.0+i*.44,24.3,.02))
        bpy.context.object.name="CONTEXT | park flower border"; bpy.context.object.data.materials.append(M["flower"])

    car(road_x-1.85,4.8,M["car"],"CONTEXT | northbound car",-.38)
    car(road_x+1.85,4.8,M["neighbor2"],"CONTEXT | southbound car",-.38)
    pedestrians=[
        (PLOT_X+7.62,-12,0,"shirt_blue"),(PLOT_X+7.62,-5,0,"shirt_red"),
        (PLOT_X+7.62,3,0,"shirt_gold"),(PLOT_X+7.62,15,0,"shirt_blue"),
        (PLOT_X+7.62,25,0,"shirt_red"),(-11.5,cross_y+3.5,math.pi/2,"shirt_gold"),
        (-5.5,cross_y+3.5,math.pi/2,"shirt_blue"),(-3.5,cross_y+3.5,math.pi/2,"shirt_red"),
        (PLOT_X+8.0,cross_y-1.0,math.pi/2,"shirt_gold"),(PLOT_X+8.0,cross_y+1.0,math.pi/2,"shirt_blue"),
        (service_x+2.05,-9,0,"shirt_gold"),(service_x+2.05,4,0,"shirt_blue"),
        (service_x+2.05,22,0,"shirt_red"),(PLOT_X+8.0,cross_y+2.5,math.pi/2,"shirt_blue"),
        (road_x-2.4,cross_y,math.pi/2,"shirt_red"),(road_x,cross_y,math.pi/2,"shirt_gold"),
        (road_x+2.4,cross_y,math.pi/2,"shirt_blue"),
    ]
    pedestrians.extend((service_x+2.05,y,0,cloth) for y,cloth in (
        (-16,"shirt_gold"),(-2,"shirt_red"),(12,"shirt_blue"),(31,"shirt_gold")))
    pedestrians.extend((service_x2+2.05,y,0,cloth) for y,cloth in (
        (-18,"shirt_red"),(-9,"shirt_blue"),(-1,"shirt_gold"),(8,"shirt_red"),
        (17,"shirt_blue"),(26,"shirt_gold"),(35,"shirt_red")))
    pedestrians.extend((-10.2,y,0,cloth) for y,cloth in (
        (-15,"shirt_blue"),(-7,"shirt_gold"),(1,"shirt_red"),(10,"shirt_blue"),
        (21,"shirt_gold"),(32,"shirt_red")))
    pedestrians.extend((x,y,yaw,cloth) for x,y,yaw,cloth in (
        (-20.6,22.0,0,"shirt_red"),(-18.1,25.8,math.pi/2,"shirt_gold"),
        (-16.7,23.8,math.pi,"shirt_blue"),(-20.0,27.1,0,"shirt_red")))
    for i,(x,y,yaw,cloth) in enumerate(pedestrians):
        base=-.20 if x>PLOT_X+7.2 or x<0 or (x<12 and y>cross_y+3.0) else -.32
        context_person(f"Resident {i+1:02d}",x,y,base,yaw,M[cloth])

    for yy in (-16,-9,-2,5,21,28,35):
        street_tree(PLOT_X+7.70,yy,.82)
    for yy in (-13,1,16,29,36):
        streetlight(PLOT_X+7.9,yy)
    for yy in (-15,-3,7,24,34):
        street_tree(service_x+2.05,yy,.74)
    for yy in (-17,-5,9,20,31):
        street_tree(service_x2+3.0,yy,.72)
    for yy in (-19,-10,-1,8,18,29,33):
        street_tree(west_lane_x+2.0,yy,.72)
    for xx in (-14,-8,-2,4,10):
        street_tree(xx,cross_y+3.55,.78)
    for i in range(6):
        xx=1.2+i*1.45
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.20,location=(xx,PLOT_Y+.48,.18))
        bpy.context.object.name="CONTEXT | north edge shrub"; bpy.context.object.data.materials.append(M["leaf"])
        if i%2==0:
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.10,location=(xx+.16,PLOT_Y+.48,.35))
            bpy.context.object.name="CONTEXT | flower"; bpy.context.object.data.materials.append(M["flower"])
    collection=bpy.data.collections.new("SURROUNDINGS | street, sidewalk, neighbors, trees")
    bpy.context.scene.collection.children.link(collection)
    for ob in list(bpy.context.scene.objects):
        if ob.name.startswith("CONTEXT |"):
            for old in list(ob.users_collection):
                old.objects.unlink(ob)
            collection.objects.link(ob)


def setup_context_camera():
    scene=bpy.context.scene
    bpy.ops.object.camera_add(location=(24.0,-23.5,18.0))
    cam=bpy.context.object
    cam.name="Camera | neighborhood context"
    cam.rotation_euler=(Vector((7.3,5.5,3.5))-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.type="ORTHO"
    cam.data.ortho_scale=31.0
    scene.camera=cam
    scene.render.filepath=SURROUNDINGS_OUT
    scene.render.resolution_x=2000
    scene.render.resolution_y=1500
    scene.render.resolution_percentage=100
    for area in bpy.context.screen.areas:
        if area.type=="VIEW_3D":
            area.spaces.active.region_3d.view_distance=25
            area.spaces.active.region_3d.view_location=(7.3,5.5,3.3)
            area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
    return cam


def setup_neighborhood_camera():
    scene=bpy.context.scene
    bpy.ops.object.camera_add(location=(50.0,-45.0,38.0))
    cam=bpy.context.object
    cam.name="Camera | full neighborhood overview"
    target=Vector((10.0,6.5,3.0))
    cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.type="ORTHO"
    cam.data.ortho_scale=96.0
    scene.camera=cam
    scene.render.filepath=NEIGHBORHOOD_OUT
    scene.render.resolution_x=2200
    scene.render.resolution_y=1500
    scene.render.resolution_percentage=100
    for area in bpy.context.screen.areas:
        if area.type=="VIEW_3D":
            area.spaces.active.region_3d.view_distance=70
            area.spaces.active.region_3d.view_location=(10.0,6.5,3.0)
            area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
    return cam


def create_house():
    clear_scene()
    # Raised site, east road and entry drive.
    box("Site plinth",(PLOT_X/2,PLOT_Y/2,-.22),(PLOT_X,PLOT_Y,.40),M["grass"],.08)
    box("East street",(PLOT_X+3.60,PLOT_Y/2,-.39),(7.20,PLOT_Y+.8,.12),M["asphalt"])
    # House footprint and three Vastu-aligned levels.
    floor_shell(0,[(X0+1.75,2.0,.72,2.32),(X0+4.45,2.5,.86,2.20),(X0+6.55,1.2,.70,1.85)],
                [(Y0+2.35,1.30,0,2.35,"door"),(Y0+5.0,1.65,.72,2.2,"window"),(Y0+8.1,1.50,.80,2.10,"window")],True)
    floor_shell(1,[(X0+1.65,2.2,.92,2.18),(X0+4.65,2.45,.82,2.15),(X0+6.8,1.2,.80,1.90)],
                [(Y0+2.35,1.55,.90,2.20,"window"),(Y0+5.45,2.35,.92,2.15,"window"),(Y0+8.2,1.45,.82,2.00,"window")],True)
    # Third storey is intentionally a compact pavilion; the rest becomes a shaded terrace.
    z2=2*FLOOR_H
    box("Terrace level | slab",((X0+X1)/2,(Y0+Y1)/2,z2),(X1-X0,Y1-Y0,SLAB),M["concrete"],.035)
    # SW pavilion, smaller and heavier at the southwest; front is mostly glazed.
    xA,xB=X0+.15,X0+4.95; yA,yB=Y0+.15,Y0+4.75
    box("Pavilion south wall",((xA+xB)/2,yA,z2+SLAB+WALL_H/2),(xB-xA,WALL_T,WALL_H),M["sand"])
    box("Pavilion west wall",(xA,(yA+yB)/2,z2+SLAB+WALL_H/2),(WALL_T,yB-yA,WALL_H),M["ivory"])
    box("Pavilion north wall",((xA+xB)/2,yB,z2+SLAB+WALL_H/2),(xB-xA,WALL_T,WALL_H),M["white"])
    box("Pavilion east glazing",(xB,(yA+yB)/2,z2+SLAB+1.30),(WALL_T,yB-yA-.18,2.35),M["glass"])
    for xx in (xA+.2,xB-.2):
        box("Pavilion glazing frame",(xx,yA-.04,z2+SLAB+1.3),(.10,.08,2.50),M["wood"])
    box("Pavilion roof",((xA+xB)/2,(yA+yB)/2,z2+SLAB+WALL_H+.10),(xB-xA+.24,yB-yA+.24,.20),M["white"],.05)
    # Slender pergola shades the northeast terrace without filling its open air/light zone.
    pergola_x0,pergola_x1=X0+5.7,X1-.25
    pergola_y0,pergola_y1=Y0+5.55,Y1-.3
    for xx in (pergola_x0,pergola_x1):
        for yy in (pergola_y0,pergola_y1):
            box("Pergola post",(xx,yy,z2+1.43),(.13,.13,2.86),M["wood"],.02)
    for yy in (pergola_y0,pergola_y1):
        box("Pergola beam",((pergola_x0+pergola_x1)/2,yy,z2+2.86),(pergola_x1-pergola_x0+.12,.16,.16),M["wood"],.025)
    count=9
    for i in range(count):
        xx=pergola_x0+.18+(pergola_x1-pergola_x0-.36)*i/(count-1)
        box("Pergola slat",(xx,(pergola_y0+pergola_y1)/2,z2+2.93),(.075,pergola_y1-pergola_y0,.12),M["wood"],.02)
    # Roof parapet leaves a break at the east terrace access.
    for a,b in [((X0,Y0),(X1,Y0)),((X0,Y0),(X0,Y1)),((X0,Y1),(X1,Y1)),((X1,Y1),(X1,Y0+5.3)),((X1,Y0+7.3),(X1,Y1))]:
        cube_between("Roof terrace parapet",(a[0],a[1],z2+.58),(b[0],b[1],z2+.58),.12,M["white"])
    # Southwest overhead tank tucked behind pavilion parapet.
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.62,depth=1.32,location=(X0+1.05,Y0+1.0,z2+SLAB+WALL_H+.78))
    bpy.context.object.name="O.H. tank | SW"; bpy.context.object.data.materials.append(M["water"])
    # East balconies and their bronze rails.
    for level,cy,w in ((1,Y0+5.35,3.2),(2,Y0+8.0,2.6)):
        z=level*FLOOR_H
        box(f"East balcony L{level} slab",(X1+.62,cy,z+.02),(1.35,w,.17),M["concrete"],.03)
        railing_east(f"East balcony L{level} rail",z+.12,cy,w)
    # Vertical teak sun screen defines the sunrise-facing entrance and stair hall.
    for i in range(7):
        yy=Y0+4.2+i*.23
        box("East facade | teak sun fin",(X1+.14,yy,FLOOR_H*1.65),(.12,.075,2.25),M["wood"],.015)
    # Entrance path: a straight, east-facing approach; compact parking at the east side.
    for i in range(7):
        yy=Y0+1.28+i*.48
        box("Entry stepping stone",(X1+.52,yy,.015),(.82,.34,.09),M["paver"],.045)
    box("East-side car pad",(PLOT_X-1.40,3.95,.035),(2.65,5.85,.09),M["paver"],.06)
    car(PLOT_X-1.40,4.05)
    # Low boundary edges and the opening to the east street.
    for y in (.22,PLOT_Y-.22):
        box("Boundary wall | north/south",(PLOT_X/2,y,.40),(PLOT_X,.22,.80),M["ivory"],.035)
    box("Boundary wall | west",(.20,PLOT_Y/2,.40),(.22,PLOT_Y,.80),M["ivory"],.035)
    for y in (.22,7.2):
        box("East boundary pier",(PLOT_X-.12,y,.50),(.24,.30,1.0),M["sand"],.035)
    # Green NE tulsi court and two compact trees; keep the east approach clear.
    box("NE tulsi court",(PLOT_X-.8,PLOT_Y-.75,.035),(1.20,1.15,.08),M["grass"],.04)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.18,depth=.16,location=(PLOT_X-.8,PLOT_Y-.75,.16))
    bpy.context.object.name="Tulsi pedestal"; bpy.context.object.data.materials.append(M["white"])
    plant("Northwest tree",.9,9.8,.02,1.05)
    plant("Southwest garden tree",1.0,1.2,.02,.82)
    # A few warm benches on the open terrace.
    box("Terrace bench seat",(X1-.72,Y1-1.15,z2+.43),(1.45,.48,.14),M["wood"],.05)
    box("Terrace bench back",(X1-.72,Y1-1.38,z2+.74),(1.45,.09,.56),M["wood"],.04)


def setup_render():
    scene=bpy.context.scene
    scene.render.engine="BLENDER_EEVEE"
    scene.render.resolution_x=1800
    scene.render.resolution_y=1400
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False
    scene.render.filepath=RENDER_OUT
    scene.render.resolution_percentage=100
    scene.render.image_settings.color_mode="RGBA"
    scene.render.engine="BLENDER_EEVEE"
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=RENDER_OUT
    scene.render.image_settings.color_mode="RGBA"
    scene.render.resolution_x=1800
    scene.render.resolution_y=1400
    scene.render.resolution_percentage=100
    scene.render.engine="BLENDER_EEVEE"
    scene.render.film_transparent=False
    scene.render.image_settings.color_mode="RGBA"
    scene.render.image_settings.file_format="PNG"
    scene.render.resolution_percentage=100
    scene.view_settings.view_transform="AgX"
    scene.render.image_settings.color_depth="8"
    scene.world.color=(.34,.37,.41)
    scene.render.engine="BLENDER_EEVEE"
    # Soft studio daylight
    bpy.ops.object.light_add(type="AREA", location=(8,-7,14))
    key=bpy.context.object; key.name="Warm late-morning sun"; key.data.energy=1800; key.data.shape="DISK"; key.data.size=8
    key.rotation_euler=(Vector((5.6,5.4,3.7))-key.location).to_track_quat("-Z","Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(-4,7,10))
    fill=bpy.context.object; fill.name="Soft sky fill"; fill.data.energy=1100; fill.data.size=9
    fill.rotation_euler=(Vector((5.6,5.4,3.0))-fill.location).to_track_quat("-Z","Y").to_euler()
    bpy.ops.object.camera_add(location=(19,-18,15.2))
    cam=bpy.context.object; cam.name="Camera | chatgpt_god presentation"
    cam.rotation_euler=(Vector((5.8,5.1,4.25))-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.type="ORTHO"; cam.data.ortho_scale=17.5; cam.data.lens=48
    scene.camera=cam
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value=(.55,.61,.68,1)
    bg.inputs["Strength"].default_value=.45
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=RENDER_OUT
    scene.render.resolution_x=1800; scene.render.resolution_y=1400
    scene.render.resolution_percentage=100
    scene.render.engine="BLENDER_EEVEE"
    scene.camera.data.lens=50
    # Render look and contact shadows.
    scene.render.image_settings.color_mode="RGBA"
    scene.render.image_settings.file_format="PNG"
    scene.render.resolution_percentage=100
    scene.camera.data.dof.use_dof=False
    scene.render.film_transparent=False
    scene.view_settings.look="AgX - Medium High Contrast"
    scene.camera.data.lens=52
    scene.render.filepath=RENDER_OUT
    scene.render.resolution_x=1800; scene.render.resolution_y=1400
    scene.render.resolution_percentage=100
    scene.eevee.taa_render_samples=48
    # Store a useful exterior view as the opening viewport.
    for area in bpy.context.screen.areas:
        if area.type=="VIEW_3D":
            area.spaces.active.region_3d.view_distance=18
            area.spaces.active.region_3d.view_location=(5.7,5.3,4.1)
            area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()


if __name__=="__main__":
    create_house()
    add_furnishings()
    collect_interiors()
    create_surroundings()
    setup_render()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    scene=bpy.context.scene
    # Keep the exterior as the main view, then make a second southeast cutaway render.
    bpy.ops.render.render(write_still=True)
    cutaway_prefixes=("South facade", "East facade", "South window", "East window",
                      "East entry", "East sandstone pilaster", "Pavilion south wall", "Pavilion east glazing")
    hidden=[]
    for ob in bpy.data.objects:
        if ob.name.startswith(cutaway_prefixes):
            ob.hide_render=True
            hidden.append(ob)
    scene.render.filepath=INTERIOR_OUT
    bpy.ops.render.render(write_still=True)
    for ob in hidden:
        ob.hide_render=False
    scene.render.filepath=RENDER_OUT
    setup_context_camera()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    bpy.ops.render.render(write_still=True)
    setup_neighborhood_camera()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("Saved", BLEND_OUT)
    print("Rendered", RENDER_OUT)
    print("Rendered cutaway interiors", INTERIOR_OUT)
    print("Rendered neighborhood surroundings", SURROUNDINGS_OUT)
    print("Rendered neighborhood overview", NEIGHBORHOOD_OUT)
