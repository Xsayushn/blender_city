"""Create a room-by-room cinematic tour of the Vastu home.

Run with Blender 5.2:
    blender --background --python animate_chatgpt_god_rooms.py

The original house file and neighborhood animation are left untouched.
"""
import bpy
import os
import sys
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(ROOT, "chatgpt_god.blend")
OUTPUT_BLEND = os.path.join(ROOT, "chatgpt_god_room_tour.blend")
OUTPUT_VIDEO = os.path.join(ROOT, "chatgpt_god_room_tour.mp4")
PREVIEW = os.path.join(ROOT, "chatgpt_god_room_tour_preview.png")

FPS = 24
OPENING_END = 48
ARRIVAL_START = 49
ARRIVAL_END = 96
INTERIOR_START = 97
SHOT_GAP = 60
ROOM_MOVE_FRAMES = 47
FLOOR1_SHOT = 8
FLOOR2_SHOT = 15


ROOMS = [
    {
        "title": "GROUND FLOOR | FULL ROOM LAYOUT",
        "floor": 0,
        "a": ((4.57, 5.56, 13.2), (4.57, 5.56, .08)),
        "b": ((4.57, 5.56, 11.6), (4.57, 5.56, .08)),
        "lens": 14,
    },
    {
        "title": "GROUND FLOOR | ENTRY + FAMILY HALL",
        "floor": 0,
        "a": ((7.45, 1.65, 1.58), (5.30, 5.15, 1.22)),
        "b": ((6.05, 3.85, 1.55), (4.65, 6.05, 1.20)),
        "lens": 30,
    },
    {
        "title": "GROUND FLOOR | LIVING + DINING",
        "floor": 0,
        "a": ((8.00, 8.30, 3.55), (4.90, 6.15, .82)),
        "b": ((7.45, 5.80, 3.15), (4.55, 7.25, .85)),
        "lens": 26,
    },
    {
        "title": "GROUND FLOOR | KITCHEN",
        "floor": 0,
        "a": ((7.35, 3.45, 2.20), (6.45, 1.55, 1.05)),
        "b": ((5.60, 3.45, 2.10), (7.45, 2.25, 1.02)),
        "lens": 28,
    },
    {
        "title": "GROUND FLOOR | GUEST BEDROOM",
        "floor": 0,
        "a": ((4.05, 4.20, 2.05), (2.80, 2.55, .92)),
        "b": ((1.55, 3.80, 1.88), (2.90, 2.55, .92)),
        "lens": 30,
    },
    {
        "title": "GROUND FLOOR | BATHROOM",
        "floor": 0,
        "a": ((2.48, 5.15, 1.95), (1.25, 6.10, .88)),
        "b": ((1.65, 5.05, 1.82), (1.22, 6.19, .90)),
        "lens": 28,
    },
    {
        "title": "GROUND FLOOR | PUJA ROOM",
        "floor": 0,
        "a": ((6.75, 8.50, 2.05), (7.78, 9.28, 1.18)),
        "b": ((6.90, 9.55, 1.92), (7.82, 9.32, 1.20)),
        "lens": 31,
    },
    {
        "title": "STAIRCASE | GROUND TO FIRST FLOOR",
        "floor": 0,
        "a": ((2.50, 6.40, 2.18), (1.50, 8.90, 1.20)),
        "b": ((2.05, 8.25, 2.28), (1.50, 9.70, 2.45)),
        "lens": 28,
    },
    {
        "title": "FIRST FLOOR | FULL ROOM LAYOUT",
        "floor": 1,
        "a": ((4.57, 5.56, 15.8), (4.57, 5.56, 3.14)),
        "b": ((4.57, 5.56, 14.2), (4.57, 5.56, 3.14)),
        "lens": 14,
    },
    {
        "title": "FIRST FLOOR | FAMILY LOUNGE",
        "floor": 1,
        "a": ((7.45, 7.35, 5.10), (4.85, 5.75, 4.08)),
        "b": ((6.05, 6.85, 4.85), (5.05, 5.65, 4.15)),
        "lens": 26,
    },
    {
        "title": "FIRST FLOOR | MASTER BEDROOM",
        "floor": 1,
        "a": ((4.20, 4.10, 5.15), (2.93, 2.59, 4.03)),
        "b": ((1.55, 4.25, 4.92), (2.92, 2.60, 4.02)),
        "lens": 29,
    },
    {
        "title": "FIRST FLOOR | BEDROOM 2",
        "floor": 1,
        "a": ((7.90, 4.05, 5.10), (6.92, 2.62, 4.03)),
        "b": ((7.85, 3.45, 4.85), (6.90, 2.65, 4.05)),
        "lens": 29,
    },
    {
        "title": "FIRST FLOOR | BEDROOM 3",
        "floor": 1,
        "a": ((7.75, 7.45, 5.10), (6.61, 8.59, 4.05)),
        "b": ((4.95, 7.45, 4.95), (6.62, 8.58, 4.05)),
        "lens": 29,
    },
    {
        "title": "FIRST FLOOR | BATHROOM",
        "floor": 1,
        "a": ((4.35, 5.25, 4.95), (3.65, 6.20, 4.05)),
        "b": ((3.55, 5.00, 4.85), (3.70, 6.18, 4.03)),
        "lens": 28,
    },
    {
        "title": "STAIRCASE | FIRST FLOOR TO TERRACE",
        "floor": 1,
        "a": ((2.45, 6.50, 5.20), (1.55, 8.95, 4.35)),
        "b": ((2.00, 8.20, 5.60), (1.55, 9.70, 5.65)),
        "lens": 28,
    },
    {
        "title": "ROOF LEVEL | PAVILION + TERRACE LAYOUT",
        "floor": 2,
        "a": ((4.57, 5.56, 18.8), (4.57, 5.56, 6.19)),
        "b": ((4.57, 5.56, 17.1), (4.57, 5.56, 6.19)),
        "lens": 14,
    },
    {
        "title": "ROOF PAVILION | YOGA + MUSIC LOUNGE",
        "floor": 2,
        "a": ((5.55, 5.35, 8.35), (3.28, 4.42, 7.05)),
        "b": ((3.25, 3.65, 7.95), (3.42, 2.75, 6.45)),
        "lens": 29,
    },
    {
        "title": "TERRACE | LOUNGE + OUTDOOR DINING",
        "floor": 2,
        "a": ((6.05, 7.55, 8.45), (7.30, 6.10, 7.03)),
        "b": ((8.05, 9.55, 8.30), (7.15, 8.14, 7.00)),
        "lens": 29,
    },
]

FINAL_EXTERIOR = INTERIOR_START + len(ROOMS) * SHOT_GAP
END = FINAL_EXTERIOR + 72


def set_constant_visibility(obj, states):
    """Key discrete render visibility changes at scene section cuts."""
    for frame, visible in states:
        obj.hide_render = not visible
        obj.keyframe_insert(data_path="hide_render", frame=frame)
    action = obj.animation_data.action if obj.animation_data else None
    curves = getattr(action, "fcurves", ()) if action else ()
    for curve in curves:
        if curve.data_path == "hide_render":
            for point in curve.keyframe_points:
                point.interpolation = "CONSTANT"


def key_energy(light, keys, interpolation="BEZIER"):
    for frame, energy in keys:
        light.data.energy = energy
        light.data.keyframe_insert(data_path="energy", frame=frame)
    action = light.data.animation_data.action if light.data.animation_data else None
    for curve in getattr(action, "fcurves", ()) if action else ():
        for point in curve.keyframe_points:
            point.interpolation = interpolation


def key_socket(socket, keys):
    for frame, value in keys:
        socket.default_value = value
        socket.keyframe_insert(data_path="default_value", frame=frame)
    owner = socket.id_data
    action = owner.animation_data.action if owner.animation_data else None
    for curve in getattr(action, "fcurves", ()) if action else ():
        for point in curve.keyframe_points:
            point.interpolation = "BEZIER"


def add_emission_material(name, color, strength=1.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    emission = nodes.new("ShaderNodeEmission")
    emission.name = name + " shader"
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = strength
    output = nodes.new("ShaderNodeOutputMaterial")
    material.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material, emission.inputs["Strength"]


def set_camera_pose(camera, aim, frame, location, target, lens):
    camera.location = location
    camera.keyframe_insert(data_path="location", frame=frame)
    aim.location = target
    aim.keyframe_insert(data_path="location", frame=frame)
    camera.data.lens = lens
    camera.data.keyframe_insert(data_path="lens", frame=frame)


def animate_camera_curves(camera, aim, hold_frames):
    for animated in (camera, aim, camera.data):
        action = animated.animation_data.action if animated.animation_data else None
        for curve in getattr(action, "fcurves", ()) if action else ():
            for point in curve.keyframe_points:
                frame = round(point.co.x)
                point.interpolation = "CONSTANT" if frame in hold_frames else "BEZIER"


def make_title(scene, camera, material, text, visible_frames, plate_material, compact=False):
    visibility = list(visible_frames)
    if not visibility or visibility[0][0] > 1:
        visibility.insert(0, (1, False))
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    plate = bpy.context.object
    plate.name = "TOUR | title plate | " + text
    width, height = ((.285, .042) if compact else (.22, .036))
    plate.dimensions = (width, height, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    plate.data.materials.append(plate_material)
    plate.parent = camera
    plate.matrix_parent_inverse = Matrix.Identity(4)
    card_x = .25 if compact else .18
    card_y = .20 if compact else .145
    plate.location = (card_x, card_y, -.50)
    set_constant_visibility(plate, visibility)

    curve = bpy.data.curves.new("Tour title lettering", "FONT")
    curve.body = text
    curve.size = .0105 if compact else .0088
    curve.extrude = .001
    obj = bpy.data.objects.new("TOUR | title | " + text, curve)
    scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.parent = camera
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = (card_x - width / 2 + .010, card_y - height / 2 + .006, -.48)
    set_constant_visibility(obj, visibility)


def add_lamp_glows(scene, start_frame, end_frame):
    bulb_material, bulb_strength = add_emission_material(
        "TOUR | warm amber streetlamp", (1.0, .48, .15, 1.0), 0.0
    )
    glow_keys = [
        (1, 0.0), (start_frame - 1, 0.0), (start_frame + 12, .8),
        (start_frame + 26, 3.0), (start_frame + 42, 5.5), (end_frame, 5.5),
    ]
    key_socket(bulb_strength, glow_keys)

    poles = [obj for obj in bpy.data.objects if obj.name.startswith("CONTEXT | streetlight pole")]
    for index, pole in enumerate(poles):
        x, y, _ = pole.location
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=8, radius=.085,
            location=(x - .88, y, 4.37),
        )
        bulb = bpy.context.object
        bulb.name = f"TOUR | streetlight bulb {index + 1:02d}"
        bulb.data.materials.append(bulb_material)

        bpy.ops.object.light_add(type="POINT", location=(x - .88, y, 4.36))
        light = bpy.context.object
        light.name = f"TOUR | streetlight pool {index + 1:02d}"
        light.data.color = (1.0, .62, .32)
        light.data.energy = 0.0
        light.data.shadow_soft_size = .9
        key_energy(light, [
            (1, 0.0), (start_frame - 1, 0.0), (start_frame + 12, 250.0),
            (start_frame + 26, 1150.0), (start_frame + 42, 1650.0),
            (end_frame, 1650.0),
        ])

    return bulb_strength


def add_room_lights(scene):
    lights = {}
    z_floors = (2.85, 5.90, 8.95)
    for level, z in enumerate(z_floors):
        bpy.ops.object.light_add(type="AREA", location=(4.75, 5.40, z))
        light = bpy.context.object
        light.name = f"TOUR | soft interior light | level {level}"
        light.data.energy = 0.0
        light.data.color = (1.0, .82, .66)
        light.data.shape = "DISK"
        light.data.size = 5.0
        light.rotation_euler = (0.0, 0.0, 0.0)
        lights[level] = light

    first_floor_start = INTERIOR_START + FLOOR1_SHOT * SHOT_GAP
    roof_start = INTERIOR_START + FLOOR2_SHOT * SHOT_GAP
    ground_end = INTERIOR_START + (FLOOR1_SHOT - 1) * SHOT_GAP + ROOM_MOVE_FRAMES
    first_floor_end = INTERIOR_START + (FLOOR2_SHOT - 1) * SHOT_GAP + ROOM_MOVE_FRAMES
    roof_end = INTERIOR_START + (len(ROOMS) - 1) * SHOT_GAP + ROOM_MOVE_FRAMES
    floor_windows = {
        0: [(1, 0.0), (INTERIOR_START - 1, 0.0), (INTERIOR_START, 850.0),
            (ground_end, 850.0), (first_floor_start, 0.0), (FINAL_EXTERIOR, 0.0)],
        1: [(1, 0.0), (first_floor_start - 1, 0.0),
            (first_floor_start, 850.0), (first_floor_end, 850.0),
            (roof_start, 0.0), (FINAL_EXTERIOR, 0.0)],
        2: [(1, 0.0), (roof_start - 1, 0.0), (roof_start, 850.0),
            (roof_end, 850.0),
            (FINAL_EXTERIOR, 0.0)],
    }
    for level, light in lights.items():
        key_energy(light, floor_windows[level])

    return lights


def setup_visibility(scene):
    outside_names = (
        "CONTEXT |", "East street", "East-side car pad", "Car", "Compact car |",
        "Boundary wall", "East boundary pier", "Entry stepping stone",
        "NE tulsi court", "Tulsi pedestal", "Northwest tree", "Southwest garden tree",
    )
    shell_names = (
        "South facade", "East facade", "North facade", "West facade",
        "South window", "East window", "East entry", "East sandstone pilaster",
        "North clerestory glass", "North window cap",
        "Pavilion south wall", "Pavilion west wall", "Pavilion north wall",
        "Pavilion east glazing", "Pavilion glazing frame", "Pavilion roof",
        "East balcony", "O.H. tank",
    )
    terrace_names = ("Pergola", "Roof terrace parapet", "Terrace bench")
    outside_states = [(1, True), (INTERIOR_START, False), (FINAL_EXTERIOR, True)]
    shell_states = [(1, True), (INTERIOR_START, False), (FINAL_EXTERIOR, True)]
    first_floor_start = INTERIOR_START + FLOOR1_SHOT * SHOT_GAP
    roof_start = INTERIOR_START + FLOOR2_SHOT * SHOT_GAP
    terrace_states = [
        (1, True), (INTERIOR_START, False),
        (roof_start, True), (FINAL_EXTERIOR, True),
    ]

    level_states = {
        0: [(1, True), (INTERIOR_START, True),
            (first_floor_start, False), (FINAL_EXTERIOR, True)],
        1: [(1, True), (INTERIOR_START, False),
            (first_floor_start, True), (roof_start, False), (FINAL_EXTERIOR, True)],
        2: [(1, True), (INTERIOR_START, False),
            (roof_start, True), (FINAL_EXTERIOR, True)],
    }
    slab_states = {
        0: level_states[0],
        1: level_states[1],
        2: level_states[2],
    }

    for obj in list(scene.objects):
        name = obj.name
        if name.startswith(outside_names):
            set_constant_visibility(obj, outside_states)
        if name.startswith(shell_names):
            set_constant_visibility(obj, shell_states)
        if name.startswith(terrace_names):
            set_constant_visibility(obj, terrace_states)

        if name.startswith("INTERIOR | L0 |"):
            set_constant_visibility(obj, level_states[0])
        elif name.startswith("INTERIOR | L1 |"):
            set_constant_visibility(obj, level_states[1])
        elif name.startswith("INTERIOR | L2 |"):
            set_constant_visibility(obj, level_states[2])

        for level in (0, 1, 2):
            slab_name = (f"Level {level} | floor slab" if level < 2 else "Terrace level | slab")
            if name.startswith(slab_name):
                set_constant_visibility(obj, slab_states[level])


def animate_day_to_night(scene):
    light_objects = (
        (bpy.data.objects.get("Warm late-morning sun"),
         [(1, 1800.0), (INTERIOR_START, 1400.0), (FINAL_EXTERIOR, 1050.0),
          (FINAL_EXTERIOR + 24, 140.0), (END, 90.0)]),
        (bpy.data.objects.get("Soft sky fill"),
         [(1, 1100.0), (INTERIOR_START, 950.0), (FINAL_EXTERIOR, 780.0),
          (FINAL_EXTERIOR + 24, 180.0), (END, 120.0)]),
    )
    for light, keys in light_objects:
        if light:
            key_energy(light, keys)

    world = scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background:
        key_socket(background.inputs["Color"], [
            (1, (.55, .61, .68, 1.0)), (FINAL_EXTERIOR, (.40, .48, .62, 1.0)),
            (FINAL_EXTERIOR + 24, (.12, .18, .31, 1.0)), (END, (.09, .13, .23, 1.0)),
        ])
        key_socket(background.inputs["Strength"], [
            (1, .45), (INTERIOR_START, .42), (FINAL_EXTERIOR, .32),
            (FINAL_EXTERIOR + 24, .14), (END, .12),
        ])


def setup_title_card(scene, camera):
    text_material, _ = add_emission_material("TOUR | title lettering", (1.0, .88, .68, 1.0), 1.2)
    plate_material, _ = add_emission_material("TOUR | title card dark", (.012, .022, .035, 1.0), .7)
    make_title(scene, camera, text_material,
               "VASTU HOME | 37.5 x 37 FT",
               [(1, True), (OPENING_END + 1, False)], plate_material)
    make_title(scene, camera, text_material, "ARRIVING AT THE EAST-FACING ENTRY",
               [(ARRIVAL_START, True), (ARRIVAL_END + 1, False)], plate_material)
    for index, shot in enumerate(ROOMS):
        start = INTERIOR_START + index * SHOT_GAP
        make_title(scene, camera, text_material, shot["title"],
                   [(start, True), (start + SHOT_GAP, False)], plate_material,
                   compact=shot["lens"] < 20)
    make_title(scene, camera, text_material, "EVENING | STREETLIGHTS ON",
               [(FINAL_EXTERIOR, True), (END + 1, False)], plate_material)


def main():
    bpy.ops.wm.open_mainfile(filepath=SOURCE)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = END
    scene.render.fps = FPS
    scene.render.fps_base = 1.0

    camera = bpy.data.objects.get("Camera | full neighborhood overview")
    if camera is None:
        raise RuntimeError("The full neighborhood camera is missing from the house scene.")
    camera.data.type = "PERSP"
    camera.data.lens = 24
    camera.data.dof.use_dof = False
    scene.camera = camera
    bpy.ops.object.empty_add(type="SPHERE", location=(10.0, 6.5, 3.0))
    aim = bpy.context.object
    aim.name = "TOUR | camera look target"
    aim.empty_display_size = .22
    aim.hide_render = True
    track = camera.constraints.new(type="TRACK_TO")
    track.name = "TOUR | follow animated look target"
    track.target = aim
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # Establish the neighborhood and approach the entrance before the room tour.
    set_camera_pose(camera, aim, 1, (50.0, -45.0, 38.0), (10.0, 6.5, 3.0), 24)
    set_camera_pose(camera, aim, OPENING_END - 4, (24.0, -20.0, 16.0), (9.0, 6.0, 2.8), 28)
    set_camera_pose(camera, aim, ARRIVAL_START, (22.0, -14.0, 10.0), (7.0, 5.2, 3.2), 30)
    set_camera_pose(camera, aim, ARRIVAL_END - 3, (13.0, -1.7, 3.5), (8.1, 1.5, 1.45), 38)

    markers = [("NEIGHBORHOOD", 1), ("EAST-FACING ENTRY", ARRIVAL_START)]
    for index, shot in enumerate(ROOMS):
        start = INTERIOR_START + index * SHOT_GAP
        end_move = start + ROOM_MOVE_FRAMES
        set_camera_pose(camera, aim, start, shot["a"][0], shot["a"][1], shot["lens"])
        set_camera_pose(camera, aim, end_move, shot["b"][0], shot["b"][1], shot["lens"])
        markers.append((shot["title"], start))

    set_camera_pose(camera, aim, FINAL_EXTERIOR, (48.0, -42.0, 31.0), (10.0, 6.5, 2.8), 24)
    set_camera_pose(camera, aim, FINAL_EXTERIOR + 66, (43.0, -35.0, 24.0), (11.0, 7.0, 2.3), 27)
    markers.append(("DUSK | STREETLIGHTS GLOW", FINAL_EXTERIOR))
    animate_camera_curves(camera, aim, {OPENING_END - 4, ARRIVAL_END - 3,
                                   *(INTERIOR_START + i * SHOT_GAP + ROOM_MOVE_FRAMES for i in range(len(ROOMS))),
                                   FINAL_EXTERIOR + 66})
    for label, frame in markers:
        scene.timeline_markers.new(label[:40], frame=frame)

    setup_visibility(scene)
    add_room_lights(scene)
    add_lamp_glows(scene, FINAL_EXTERIOR, END)
    animate_day_to_night(scene)
    setup_title_card(scene, camera)

    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 24
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.media_type = "VIDEO"
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.filepath = OUTPUT_VIDEO
    scene.render.use_file_extension = True
    scene.render.film_transparent = False
    scene.render.use_compositing = False

    # Open the project at the first frame with the camera framing visible.
    scene.camera = camera
    scene.frame_set(1)
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.region_3d.view_perspective = "CAMERA"

    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)

    if "--preview-only" in sys.argv:
        preview_frame = (INTERIOR_START + 21 if "--overview-preview" in sys.argv
                         else INTERIOR_START + 2 * SHOT_GAP + 21)
        scene.frame_set(preview_frame)
        scene.render.image_settings.media_type = "IMAGE"
        scene.render.image_settings.file_format = "PNG"
        scene.render.resolution_x = 1800
        scene.render.resolution_y = 1000
        scene.render.resolution_percentage = 100
        scene.render.filepath = PREVIEW
        bpy.ops.render.render(write_still=True)
        print("Rendered camera-check preview:", PREVIEW)
        return

    bpy.ops.render.render(animation=True)

    # Leave an easy-to-open still of the main living/dining view for review.
    scene.frame_set(INTERIOR_START + 2 * SHOT_GAP + 21)
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.filepath = PREVIEW
    bpy.ops.render.render(write_still=True)

    scene.frame_set(1)
    scene.render.image_settings.media_type = "VIDEO"
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.filepath = OUTPUT_VIDEO
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    print("Saved room-tour Blender file:", OUTPUT_BLEND)
    print("Rendered room-tour video:", OUTPUT_VIDEO)
    print("Rendered interior preview:", PREVIEW)


if __name__ == "__main__":
    main()
