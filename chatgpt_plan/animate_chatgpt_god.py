"""Add an 8-second neighborhood-to-house animation to the Blender concept scene.

Run with Blender 5.2:
    blender --background --python animate_chatgpt_god.py

Outputs are kept beside this script. The original static .blend remains untouched.
"""
import bpy
import os
from mathutils import Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
SOURCE=os.path.join(ROOT,"chatgpt_god.blend")
OUTPUT_BLEND=os.path.join(ROOT,"chatgpt_god_animation.blend")
OUTPUT_VIDEO=os.path.join(ROOT,"chatgpt_god_animation.mp4")
START, MID, END=1, 97, 193  # 8 seconds at 24 fps


def rig_objects(name, members):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0,0,0))
    rig=bpy.context.object
    rig.name="ANIMATION | "+name
    rig.empty_display_size=.55
    for ob in members:
        world=ob.matrix_world.copy()
        ob.parent=rig
        ob.matrix_world=world
    return rig


def animate_axis(rig, axis, keys):
    for frame,value in keys:
        rig.location[axis]=value
        rig.keyframe_insert(data_path="location",index=axis,frame=frame)


def set_key_interpolation(rig_names, interpolation):
    """Set interpolation where Blender exposes the curve collection directly."""
    for name in rig_names:
        ob=bpy.data.objects.get(name)
        action=ob.animation_data.action if ob and ob.animation_data else None
        curves=getattr(action,"fcurves",()) if action else ()
        for curve in curves:
            for point in curve.keyframe_points:
                point.interpolation=interpolation


def main():
    bpy.ops.wm.open_mainfile(filepath=SOURCE)
    scene=bpy.context.scene
    scene.frame_start=START
    scene.frame_end=END
    scene.render.fps=24
    scene.render.fps_base=1.0

    # Cars travel in opposite lanes and meet side by side at the center of the shot.
    car_rigs=[]
    for prefix,name,direction in (
        ("CONTEXT | northbound car |","Northbound car",1),
        ("CONTEXT | southbound car |","Southbound car",-1),
    ):
        members=[ob for ob in bpy.data.objects if ob.name.startswith(prefix)]
        rig=rig_objects(name,members)
        animate_axis(rig,1,[(START,-13*direction),(MID,0),(END,13*direction)])
        car_rigs.append(rig.name)
    set_key_interpolation(car_rigs,"LINEAR")

    # A few sidewalk residents walk slowly along the street.
    walkers=[]
    for number in (1,2,3,4,5,11,12,13,*range(18,35)):
        prefix=f"CONTEXT | Resident {number:02d} |"
        members=[ob for ob in bpy.data.objects if ob.name.startswith(prefix)]
        if not members:
            continue
        rig=rig_objects(f"Resident {number:02d}",members)
        animate_axis(rig,1,[(START,0),(MID,.8),(END,1.6)])
        walkers.append(rig.name)
    set_key_interpolation(walkers,"LINEAR")

    # Three people cross the marked junction from the west curb toward the shop.
    crossers=[]
    for number in (15,16,17):
        prefix=f"CONTEXT | Resident {number:02d} |"
        members=[ob for ob in bpy.data.objects if ob.name.startswith(prefix)]
        if not members:
            continue
        rig=rig_objects(f"Crossing resident {number:02d}",members)
        animate_axis(rig,0,[(START,-1.8),(MID,0),(END,1.8)])
        crossers.append(rig.name)
    set_key_interpolation(crossers,"LINEAR")

    # Push the neighborhood camera toward the house, then settle on its facade.
    camera=bpy.data.objects.get("Camera | full neighborhood overview")
    if camera is None:
        raise RuntimeError("The neighborhood overview camera is missing from the scene.")
    camera.rotation_mode="QUATERNION"
    camera_keys=[
        (START,(50.0,-45.0,38.0),(10.0,6.5,3.0),96.0),
        (MID,(32.0,-29.0,22.0),(8.0,5.8,3.5),44.0),
        (END,(24.0,-23.5,18.0),(7.3,5.5,3.5),31.0),
    ]
    for frame,location,target,scale in camera_keys:
        camera.location=location
        camera.rotation_quaternion=(Vector(target)-Vector(location)).to_track_quat("-Z","Y")
        camera.keyframe_insert(data_path="location",frame=frame)
        camera.keyframe_insert(data_path="rotation_quaternion",frame=frame)
        camera.data.ortho_scale=scale
        camera.data.keyframe_insert(data_path="ortho_scale",frame=frame)

    for marker_name,frame in (("NEIGHBORHOOD",START),("TRAFFIC + CROSSING",MID),("THE HOUSE",END)):
        scene.timeline_markers.new(marker_name,frame=frame)

    scene.camera=camera
    scene.frame_set(START)
    scene.render.engine="BLENDER_EEVEE"
    scene.eevee.taa_render_samples=24
    scene.render.resolution_x=1280
    scene.render.resolution_y=960
    scene.render.resolution_percentage=100
    scene.render.image_settings.media_type="VIDEO"
    scene.render.image_settings.file_format="FFMPEG"
    scene.render.image_settings.color_mode="RGB"
    scene.render.ffmpeg.format="MPEG4"
    scene.render.ffmpeg.codec="H264"
    scene.render.ffmpeg.constant_rate_factor="MEDIUM"
    scene.render.filepath=OUTPUT_VIDEO
    scene.render.use_file_extension=True
    scene.render.film_transparent=False

    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    bpy.ops.render.render(animation=True)
    scene.frame_set(START)
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    print("Saved animated Blender file:",OUTPUT_BLEND)
    print("Rendered animation:",OUTPUT_VIDEO)


if __name__=="__main__":
    main()
