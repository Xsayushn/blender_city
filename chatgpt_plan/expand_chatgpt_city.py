"""Add a larger, more varied city around the existing Vastu home scene.

The house and existing neighborhood are loaded from chatgpt_god.blend. This
script adds a separate CITY | collection and replaces only the context ground
plane, then verifies that every original non-context object's transform is
unchanged before saving a new Blender file and two city views.

Run with Blender 5.2:
    blender --background --python expand_chatgpt_city.py
"""
import bpy
import math
import os
import random
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(ROOT, "chatgpt_god.blend")
OUTPUT_BLEND = os.path.join(ROOT, "chatgpt_god_expanded_city.blend")
OUTPUT_OVERVIEW = os.path.join(ROOT, "chatgpt_god_expanded_city.png")
OUTPUT_DETAIL = os.path.join(ROOT, "chatgpt_god_city_detail.png")
RNG = random.Random(413)
CITY_COLLECTION = None
CUBE_MESHES = {}
CYLINDER_MESHES = {}
ICO_MESHES = {}


def original_house_signature():
    rows = []
    for obj in bpy.data.objects:
        if obj.name.startswith(("CONTEXT |", "CITY |")):
            continue
        matrix = tuple(round(value, 7) for row in obj.matrix_world for value in row)
        rows.append((obj.name, obj.type, matrix))
    return tuple(sorted(rows))


def material(name, color, roughness=.68, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat


def add_city_object(name, mesh, location):
    obj = bpy.data.objects.new(name, mesh)
    CITY_COLLECTION.objects.link(obj)
    obj.location = location
    return obj


def cube(name, location, dimensions, mat, bevel=0.0):
    key = mat.name if mat else "__no_material__"
    mesh = CUBE_MESHES.get(key)
    if mesh is None:
        mesh = bpy.data.meshes.new(f"CITY | shared cube | {key}")
        mesh.from_pydata(
            ((-.5, -.5, -.5), (.5, -.5, -.5), (.5, .5, -.5), (-.5, .5, -.5),
             (-.5, -.5, .5), (.5, -.5, .5), (.5, .5, .5), (-.5, .5, .5)),
            (),
            ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)),
        )
        if mat:
            mesh.materials.append(mat)
        CUBE_MESHES[key] = mesh
    obj = add_city_object(name, mesh, location)
    obj.scale = dimensions
    return obj


def cylinder(name, location, radius, depth, mat, vertices=16):
    key = (vertices, mat.name if mat else "__no_material__")
    mesh = CYLINDER_MESHES.get(key)
    if mesh is None:
        mesh = bpy.data.meshes.new(f"CITY | shared cylinder {vertices} | {key[1]}")
        verts = []
        for z in (-1.0, 1.0):
            verts.extend((math.cos(2 * math.pi * i / vertices),
                          math.sin(2 * math.pi * i / vertices), z) for i in range(vertices))
        faces = [tuple(reversed(range(vertices))), tuple(range(vertices, vertices * 2))]
        for i in range(vertices):
            j = (i + 1) % vertices
            faces.append((i, j, j + vertices, i + vertices))
        mesh.from_pydata(verts, (), faces)
        if mat:
            mesh.materials.append(mat)
        CYLINDER_MESHES[key] = mesh
    obj = add_city_object(name, mesh, location)
    obj.scale = (radius, radius, depth / 2)
    return obj


def ico_sphere(name, location, radius, mat):
    key = mat.name if mat else "__no_material__"
    mesh = ICO_MESHES.get(key)
    if mesh is None:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
        template = bpy.context.object
        mesh = template.data.copy()
        mesh.name = f"CITY | shared ico sphere | {key}"
        bpy.data.objects.remove(template, do_unlink=True)
        mesh.materials.clear()
        if mat:
            mesh.materials.append(mat)
        ICO_MESHES[key] = mesh
    obj = add_city_object(name, mesh, location)
    obj.scale = (radius, radius, radius)
    return obj


def make_materials():
    global M, WALLS
    M = {
        "ground": material("CITY | soft olive ground", (.27, .37, .28)),
        "road": material("CITY | charcoal asphalt", (.105, .125, .14), .9),
        "curb": material("CITY | pale curb concrete", (.58, .61, .59), .8),
        "walk": material("CITY | warm sidewalk paving", (.58, .54, .46), .8),
        "line": material("CITY | road paint", (.91, .88, .70), .55),
        "white": material("CITY | warm ivory trim", (.88, .83, .72)),
        "glass": material("CITY | blue green glazing", (.12, .34, .40), .3, .08),
        "roof": material("CITY | slate roofs", (.20, .24, .27), .78),
        "wood": material("CITY | warm timber", (.40, .22, .12), .74),
        "metal": material("CITY | dark metal", (.18, .23, .24), .45, .35),
        "leaf": material("CITY | garden green", (.18, .36, .19)),
        "trunk": material("CITY | bark", (.25, .14, .08)),
        "skin": material("CITY | person skin", (.67, .42, .28)),
        "clothes": [
            material("CITY | saffron clothing", (.78, .31, .12)),
            material("CITY | indigo clothing", (.14, .27, .49)),
            material("CITY | teal clothing", (.10, .42, .37)),
            material("CITY | marigold clothing", (.88, .61, .12)),
            material("CITY | rose clothing", (.61, .20, .29)),
        ],
        "shop": material("CITY | shop terracotta", (.67, .33, .18)),
        "school": material("CITY | school peach", (.81, .66, .46)),
        "clinic": material("CITY | clinic sage", (.63, .75, .67)),
        "park": material("CITY | park lawn", (.22, .39, .23)),
        "court": material("CITY | sports court blue", (.16, .36, .49)),
        "play": material("CITY | playground red", (.76, .26, .16)),
        "flower": material("CITY | flower color", (.94, .62, .20)),
    }
    WALLS = [
        material("CITY | plaster ivory", (.82, .77, .66)),
        material("CITY | plaster pale sage", (.62, .71, .60)),
        material("CITY | plaster sand", (.78, .62, .45)),
        material("CITY | plaster warm white", (.91, .88, .79)),
        material("CITY | plaster muted blue", (.46, .62, .65)),
        material("CITY | plaster rose", (.72, .52, .43)),
    ]


def vertical_road(x, y0, y1, width=5.2, name="street"):
    center_y = (y0 + y1) / 2
    length = y1 - y0
    cube(f"CITY | {name} | asphalt", (x, center_y, -.39), (width, length, .12), M["road"])
    for side in (-1, 1):
        edge_x = x + side * (width / 2 + .11)
        cube(f"CITY | {name} | curb", (edge_x, center_y, -.245), (.22, length, .20), M["curb"], .025)
        walk_x = x + side * (width / 2 + .75)
        cube(f"CITY | {name} | sidewalk", (walk_x, center_y, -.305), (1.05, length, .12), M["walk"], .035)
    for y in range(math.ceil(y0 + 5), math.floor(y1 - 4), 8):
        for lane_offset in (-.09, .09):
            cube(f"CITY | {name} | center dash", (x + lane_offset, y, -.305), (.055, 3.1, .016), M["line"], .008)


def horizontal_road(y, x0, x1, width=5.2, name="street"):
    center_x = (x0 + x1) / 2
    length = x1 - x0
    cube(f"CITY | {name} | asphalt", (center_x, y, -.39), (length, width, .12), M["road"])
    for side in (-1, 1):
        edge_y = y + side * (width / 2 + .11)
        cube(f"CITY | {name} | curb", (center_x, edge_y, -.245), (length, .22, .20), M["curb"], .025)
        walk_y = y + side * (width / 2 + .75)
        cube(f"CITY | {name} | sidewalk", (center_x, walk_y, -.305), (length, 1.05, .12), M["walk"], .035)
    for x in range(math.ceil(x0 + 5), math.floor(x1 - 4), 8):
        for lane_offset in (-.09, .09):
            cube(f"CITY | {name} | center dash", (x, y + lane_offset, -.305), (3.1, .055, .016), M["line"], .008)


def tree(x, y, scale=1.0, name="street tree"):
    cylinder(f"CITY | {name} | trunk", (x, y, .80 * scale), .15 * scale, 1.6 * scale, M["trunk"], 12)
    for dx, dy, radius in ((0, 0, .72), (-.34, .12, .49), (.35, -.08, .51)):
        ico_sphere(f"CITY | {name} | canopy",
                   (x + dx * scale, y + dy * scale, 1.76 * scale),
                   radius * scale, M["leaf"])


def streetlight(x, y, name="streetlight"):
    cylinder(f"CITY | {name} | pole", (x, y, 2.55), .065, 5.1, M["metal"], 12)
    cube(f"CITY | {name} | arm", (x - .43, y, 4.95), (.94, .075, .075), M["metal"], .025)
    cube(f"CITY | {name} | lamp", (x - .88, y, 4.87), (.40, .24, .17), M["flower"], .05)


def house(x0, y0, width, depth, stories, style, number):
    height = stories * 2.75
    wall = WALLS[style % len(WALLS)]
    x = x0 + width / 2
    y = y0 + depth / 2
    name = f"Villa {number:03d}"
    cube(f"CITY | {name} | garden pad", (x, y, -.20), (width + .8, depth + .8, .22), M["park"], .045)
    cube(f"CITY | {name} | body", (x, y, height / 2), (width, depth, height), wall, .075)
    cube(f"CITY | {name} | roof slab", (x, y, height + .10), (width + .22, depth + .22, .20), M["roof"], .035)

    # A short parapet, rooftop tank, and optional solar panels break up repeated silhouettes.
    for sx in (-1, 1):
        cube(f"CITY | {name} | roof parapet", (x + sx * (width / 2), y, height + .27), (.11, depth + .15, .34), M["white"], .02)
    cylinder(f"CITY | {name} | water tank", (x + width * .25, y + depth * .18, height + .68), .28, .65, M["clinic"], 16)
    if number % 4 == 0:
        for i in range(2):
            cube(f"CITY | {name} | solar panel", (x - .45 + i * .60, y - .40, height + .235), (.48, .78, .055), M["court"], .015)

    # South and east sides are detailed for the city camera's view direction.
    for floor in range(stories):
        z = .82 + floor * 2.75
        for wx in (x - width * .27, x + width * .27):
            cube(f"CITY | {name} | south window", (wx, y0 - .035, z), (.92, .055, 1.08), M["glass"], .02)
            cube(f"CITY | {name} | south sill", (wx, y0 - .09, z - .57), (1.04, .13, .10), M["white"], .015)
        for wy in (y0 + depth * .36, y0 + depth * .76):
            cube(f"CITY | {name} | east window", (x0 + width + .035, wy, z), (.055, .90, 1.08), M["glass"], .02)

    cube(f"CITY | {name} | front door", (x, y0 - .045, 1.06), (.94, .10, 2.12), M["wood"], .025)
    cube(f"CITY | {name} | entry hood", (x, y0 - .34, 2.24), (1.48, .72, .14), M["wood"], .035)
    cube(f"CITY | {name} | entry step", (x, y0 - .34, .02), (1.30, .70, .18), M["curb"], .025)

    if stories > 1 and number % 3 != 0:
        balcony_y = y0 - .34
        cube(f"CITY | {name} | balcony floor", (x, balcony_y, 3.00), (width * .66, .74, .14), M["walk"], .025)
        cube(f"CITY | {name} | balcony rail", (x, balcony_y - .35, 3.47), (width * .66, .06, .82), M["metal"], .02)

    # A low garden wall has gaps at the gate and a line of shrubs by the path.
    for wx in (x0 + .35, x0 + width - .35):
        cube(f"CITY | {name} | front garden wall", (wx, y0 - .75, .27), (.12, .12, .54), M["white"], .025)
    for wy in (y0 + .5, y0 + depth - .5):
        cube(f"CITY | {name} | side garden wall", (x0 + width + .42, wy, .27), (.12, .12, .54), M["white"], .025)
    for i in range(3):
        ico_sphere(f"CITY | {name} | planter",
                   (x0 + .58 + i * .78, y0 + depth - .48, .26), .29, M["leaf"])


def civic_building(name, center, size, stories, wall_mat, sign, accent):
    x, y = center
    width, depth = size
    height = stories * 3.0
    cube(f"CITY | {name} | forecourt", (x, y - depth * .72, -.19), (width + 2.5, 3.0, .20), M["walk"], .04)
    cube(f"CITY | {name} | body", (x, y, height / 2), (width, depth, height), wall_mat, .08)
    cube(f"CITY | {name} | roof", (x, y, height + .12), (width + .35, depth + .35, .24), M["roof"], .04)
    for floor in range(stories):
        z = .95 + floor * 3.0
        for i in range(3):
            wx = x - width * .31 + i * width * .31
            cube(f"CITY | {name} | window", (wx, y - depth / 2 - .04, z), (1.45, .08, 1.35), M["glass"], .025)
            cube(f"CITY | {name} | side window", (x + width / 2 + .04, y - depth * .30 + i * depth * .30, z), (.08, 1.1, 1.3), M["glass"], .025)
    cube(f"CITY | {name} | entry", (x, y - depth / 2 - .07, 1.15), (1.5, .12, 2.3), M["wood"], .025)
    cube(f"CITY | {name} | sign", (x, y - depth / 2 - .12, 3.15), (width * .70, .12, .56), accent, .025)
    curve = bpy.data.curves.new(f"{name} sign text", "FONT")
    curve.body = sign
    curve.size = .36
    curve.extrude = .003
    text = bpy.data.objects.new(f"CITY | {name} | lettering", curve)
    bpy.context.collection.objects.link(text)
    text.location = (x - width * .32, y - depth / 2 - .20, 3.02)
    text.rotation_euler = (math.pi / 2, 0, 0)
    text.data.materials.append(M["white"])


def park(name, center, size):
    x, y = center
    width, depth = size
    cube(f"CITY | {name} | lawn", (x, y, -.32), (width, depth, .18), M["park"], .08)
    cube(f"CITY | {name} | walking path", (x, y, -.205), (1.5, depth - 1.0, .08), M["walk"], .035)
    cube(f"CITY | {name} | cross path", (x, y, -.20), (width - 1.0, 1.15, .08), M["walk"], .035)
    for sx in (-1, 1):
        for sy in (-1, 1):
            tree(x + sx * (width / 2 - 1.1), y + sy * (depth / 2 - 1.1), .62, f"{name} tree")
    for i in range(3):
        bx = x - width * .26 + i * width * .26
        cube(f"CITY | {name} | bench seat", (bx, y + 1.3, .27), (1.45, .42, .12), M["wood"], .04)
        cube(f"CITY | {name} | bench back", (bx, y + 1.5, .64), (1.45, .10, .70), M["wood"], .035)
    # A compact play area adds a recognizable family destination.
    cube(f"CITY | {name} | play surface", (x + width * .26, y - depth * .25, -.18), (width * .30, depth * .28, .12), M["play"], .06)
    cube(f"CITY | {name} | slide", (x + width * .26, y - depth * .25, .53), (1.0, 2.4, .10), M["flower"], .05)


def car(x, y, direction=0, color=None, number=1):
    color = color or M["clinic"]
    car_name = f"CITY | car {number:02d}"
    body = cube(f"{car_name} | body", (x, y, .50), (1.75, 3.65, .58), color, .20)
    body.rotation_euler.z = direction
    cabin = cube(f"{car_name} | cabin", (x, y, .94), (1.48, 1.86, .66), M["glass"], .16)
    cabin.rotation_euler.z = direction
    for side in (-1, 1):
        for along in (-1, 1):
            wx = x + side * .90 * math.cos(direction) - along * 1.12 * math.sin(direction)
            wy = y + side * .90 * math.sin(direction) + along * 1.12 * math.cos(direction)
            wheel = cylinder(f"{car_name} | wheel", (wx, wy, .31), .29, .16, M["metal"], 16)
            wheel.rotation_euler.y = math.pi / 2


def person(x, y, shirt, name):
    cube(f"CITY | {name} | torso", (x, y, .98), (.34, .24, .64), shirt, .07)
    ico_sphere(f"CITY | {name} | head", (x, y, 1.44), .13, M["skin"])
    for side in (-1, 1):
        cylinder(f"CITY | {name} | leg", (x + side * .11, y, .36), .075, .50, M["metal"], 10)


def boulevard_roundabout(center):
    x, y = center
    cylinder("CITY | rotary | planted island", (x, y, -.26), 3.4, .18, M["park"], 48)
    bpy.ops.mesh.primitive_torus_add(major_radius=4.0, minor_radius=.17, major_segments=48, minor_segments=10)
    template = bpy.context.object
    ring_mesh = template.data.copy()
    ring_mesh.name = "CITY | shared rotary ring"
    bpy.data.objects.remove(template, do_unlink=True)
    ring_mesh.materials.append(M["curb"])
    add_city_object("CITY | rotary | stone ring", ring_mesh, (x, y, -.30))
    tree(x, y, .75, "rotary island tree")
    for angle in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
        dx, dy = math.cos(angle) * 5.4, math.sin(angle) * 5.4
        for stripe in (-1, 0, 1):
            if angle in (0, math.pi):
                dims = (.32, .75, .025)
                loc = (x + dx, y + stripe * .55, -.29)
            else:
                dims = (.75, .32, .025)
                loc = (x + stripe * .55, y + dy, -.29)
            cube("CITY | rotary | crossing stripe", loc, dims, M["line"], .01)


def add_city():
    scene = bpy.context.scene
    global CITY_COLLECTION
    collection = bpy.data.collections.new("CITY | expansion | outer districts")
    scene.collection.children.link(collection)
    CITY_COLLECTION = collection
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]

    # Replace only the old context lawn tile so new blocks have a continuous base.
    old_ground = bpy.data.objects.get("CONTEXT | ground beyond plot")
    if old_ground:
        bpy.data.objects.remove(old_ground, do_unlink=True)
    cube("CITY | continuous district ground", (21.0, 5.0, -.49), (198.0, 168.0, .14), M["ground"], .05)

    # New residential street grid wraps around the existing 29-home neighborhood.
    west_roads = (-66.0, -51.0, -36.0, -21.0)
    east_roads = (54.0, 69.0, 84.0, 99.0, 114.0)
    south_roads = (-69.0, -54.0, -39.0)
    middle_roads = (-39.0, -24.0, -9.0, 6.0, 21.0, 36.0, 51.0)
    north_roads = (51.0, 66.0, 81.0)

    for i, x in enumerate(west_roads):
        vertical_road(x, -72.0, 54.0, 5.2, f"west avenue {i + 1}")
    for i, x in enumerate(east_roads):
        vertical_road(x, -72.0, 84.0, 5.5 if x == 54 else 5.0, f"east avenue {i + 1}")
    for i, y in enumerate(south_roads):
        horizontal_road(y, -69.0, 69.0, 5.2, f"south cross street {i + 1}")
    for i, y in enumerate(middle_roads):
        horizontal_road(y, 54.0, 117.0, 5.0, f"east cross street {i + 1}")
    for i, y in enumerate(north_roads):
        horizontal_road(y, -69.0, 117.0, 5.2, f"north cross street {i + 1}")

    # A tree-lined boulevard and planted roundabout mark the new eastern entrance.
    boulevard_roundabout((54.0, 51.0))
    for y in (-31.0, -1.0, 29.0, 59.0):
        tree(50.15, y, .82, "boulevard tree")
        streetlight(50.4, y, "boulevard lamp")

    number = 30  # Existing code has 29 villas.
    home_specs = []
    # East district: four varied rows of town homes along the new avenue.
    for row, y_center in enumerate((-31.5, -16.5, -1.5, 13.5, 28.5, 43.5)):
        for col, center_x in enumerate((61.5, 76.5, 91.5, 106.5)):
            if (center_x, y_center) == (76.5, -16.5):
                continue  # Keep this block open for a pocket plaza.
            stories = (1, 2, 2, 3)[(row + col) % 4]
            home_specs.append((center_x - 2.35, y_center - 3.15, 4.7, 6.3, stories, (row + col) % 6))
    # Western extension, with a quieter scale and planted front gardens.
    for row, y_center in enumerate((-16.0, 0.0, 16.0, 32.0, 48.0)):
        for col, center_x in enumerate((-58.5, -43.5)):
            stories = 1 if (row + col) % 3 == 0 else 2
            home_specs.append((center_x - 2.25, y_center - 3.0, 4.5, 6.0, stories, (row + col + 2) % 6))
    # South blocks form a compact grid below the original homes.
    for row, y_center in enumerate((-46.5, -61.5)):
        for col, center_x in enumerate((-13.5, 1.5, 16.5, 31.5, 46.5, 61.5)):
            stories = (1, 2, 3)[(row * 2 + col) % 3]
            home_specs.append((center_x - 2.3, y_center - 3.0, 4.6, 6.0, stories, (row + col) % 6))
    # North blocks leave room for the school, clinic, and new landscaped square.
    for row, y_center in enumerate((58.5, 73.5)):
        for col, center_x in enumerate((-13.5, 1.5, 16.5, 31.5, 46.5, 61.5, 76.5)):
            if (center_x, y_center) in ((31.5, 58.5), (61.5, 73.5)):
                continue
            stories = (2, 3, 2, 1)[(row + col) % 4]
            home_specs.append((center_x - 2.3, y_center - 3.0, 4.6, 6.0, stories, (row + col + 3) % 6))
    for spec in home_specs:
        house(*spec, number=number)
        number += 1

    # Civic uses and public space give the district a purpose beyond housing.
    civic_building("neighborhood school", (-29.0, 58.5), (10.0, 9.0), 2, M["school"], "SCHOOL", M["shop"])
    civic_building("community clinic", (91.5, 58.5), (10.0, 9.0), 2, M["clinic"], "CLINIC", M["shop"])
    civic_building("city apartments", (106.5, 58.5), (9.0, 9.0), 4, WALLS[4], "APARTMENTS", M["shop"])
    park("family park", (76.5, -16.5), (10.5, 10.0))
    park("north garden square", (31.5, 58.5), (10.5, 10.0))
    park("west neighborhood park", (-28.5, -1.5), (8.0, 8.0))

    # Two storefronts fill otherwise quiet southern blocks without crossing streets.
    for i, center_x in enumerate((76.5, 106.5)):
        civic_building(
            f"market {i + 1}", (center_x, -46.5), (8.0, 6.0), 1,
            WALLS[(i + 2) % len(WALLS)], ("GROCERY", "CAFE")[i], M["shop"],
        )

    # Street trees, poles, people, and cars add scale and everyday activity.
    for road_x in (-51.0, -36.0, 69.0, 84.0, 99.0, 114.0):
        for y in (-61.0, -31.0, -1.0, 29.0, 59.0, 74.0):
            if road_x > 0 and y > 50 and road_x > 100:
                continue
            side = -1 if road_x < 0 else 1
            tree(road_x + side * 3.6, y, .62, "residential street tree")
        for y in (-45.0, 0.0, 45.0):
            light_x = road_x + (3.8 if road_x > 0 else -3.8)
            streetlight(light_x, y, "residential lamp")

    for i, (x, y, angle) in enumerate((
        (54.0, -30.0, 0.0), (54.0, 17.0, 0.0), (84.0, -46.0, 0.0),
        (99.0, 30.0, 0.0), (-34.0, 6.0, math.pi / 2), (-52.0, 21.0, math.pi / 2),
        (20.0, -35.4, math.pi / 2), (45.0, 81.0, math.pi / 2),
    )):
        car(x, y, angle, WALLS[i % len(WALLS)], i + 1)

    for i, (x, y) in enumerate((
        (50.5, -16.0), (50.5, 5.0), (50.5, 33.0), (50.5, 54.5),
        (-27.0, 47.8), (-10.0, 47.8), (6.0, 47.8), (25.0, 47.8),
        (72.6, 49.0), (102.6, 49.0), (35.0, -37.0), (-41.0, -37.0),
        (30.0, 82.0), (40.0, 82.0),
    )):
        person(x, y, M["clothes"][i % len(M["clothes"])], f"resident {i + 1:02d}")

    return len(home_specs)


def setup_cameras(scene):
    overview_target = Vector((22.0, 7.0, 1.2))
    overview = bpy.data.objects.new("CITY | expanded city overview camera", bpy.data.cameras.new("CITY | overview lens"))
    bpy.context.collection.objects.link(overview)
    overview.location = overview_target + Vector((100.0, -118.0, 145.0))
    overview.rotation_euler = (overview_target - overview.location).to_track_quat("-Z", "Y").to_euler()
    overview.data.type = "ORTHO"
    overview.data.ortho_scale = 248.0
    overview.data.lens = 48
    overview.data.clip_end = 600

    detail_target = Vector((18.0, 6.0, 2.1))
    detail = bpy.data.objects.new("CITY | district detail camera", bpy.data.cameras.new("CITY | detail lens"))
    bpy.context.collection.objects.link(detail)
    detail.location = detail_target + Vector((57.0, -68.0, 78.0))
    detail.rotation_euler = (detail_target - detail.location).to_track_quat("-Z", "Y").to_euler()
    detail.data.type = "ORTHO"
    detail.data.ortho_scale = 126.0
    detail.data.lens = 52
    detail.data.clip_end = 400
    scene.camera = overview
    return overview, detail


def main():
    bpy.ops.wm.open_mainfile(filepath=SOURCE)
    scene = bpy.context.scene
    if not bpy.data.objects.get("Site plinth"):
        raise RuntimeError("The original house plot is missing from the source file.")
    original_signature = original_house_signature()
    make_materials()
    added_homes = add_city()
    overview, detail = setup_cameras(scene)

    if original_house_signature() != original_signature:
        raise RuntimeError("An original house or scene object's transform changed during city expansion.")

    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 32
    scene.view_settings.exposure = .65
    scene.render.resolution_percentage = 100
    scene.render.resolution_x = 2200
    scene.render.resolution_y = 1500
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False

    # Keep an attractive, zoomed-out city overview as the saved opening view.
    scene.camera = overview
    scene.render.filepath = OUTPUT_OVERVIEW
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    bpy.ops.render.render(write_still=True)

    # Render a closer district view without changing any geometry.
    scene.camera = detail
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1200
    scene.render.filepath = OUTPUT_DETAIL
    bpy.ops.render.render(write_still=True)

    scene.camera = overview
    scene.render.resolution_x = 2200
    scene.render.resolution_y = 1500
    scene.render.filepath = OUTPUT_OVERVIEW
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    print("Saved expanded city Blender file:", OUTPUT_BLEND)
    print("Rendered city overview:", OUTPUT_OVERVIEW)
    print("Rendered close district view:", OUTPUT_DETAIL)
    print("Added detached homes:", added_homes)


if __name__ == "__main__":
    main()
