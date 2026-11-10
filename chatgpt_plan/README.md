# ChatGPT Vastu Home

This folder contains the 37.5 x 37 ft Vastu home concept, its neighborhood scene, and a narrated camera tour through the interior.

## Main files

- `chatgpt_god.py` builds the house and neighborhood scene.
- `chatgpt_god.blend` is the editable Blender scene.
- `animate_chatgpt_god_rooms.py` builds and renders the detailed room tour.
- `chatgpt_god_room_tour.blend` is the animated Blender project.
- `chatgpt_god_room_tour.mp4` is the finished 1280 x 720, 24 fps tour, with the streetlights glowing at dusk.
- `chatgpt_god_room_tour_preview.png` is a still from the living and dining room.
- `Chatgpt_plan.dxf` and `Chatgpt_plan.svg` are plan drawings.
- `expand_chatgpt_city.py` adds outer city blocks around the home scene without changing the house objects.
- `chatgpt_god_expanded_city.blend` is the expanded city project; `chatgpt_god_expanded_city.png` is its overview and `chatgpt_god_city_detail.png` is a closer view.

## Re-render the room tour

With Blender 5.2 installed, run this from the folder:

```powershell
blender --background --python animate_chatgpt_god_rooms.py
```

The script reads `chatgpt_god.blend` and writes the tour project, MP4, and preview beside itself.

This is a visualization concept. Have a local architect and structural engineer review the plans before construction.

## Rebuild the expanded city

```powershell
blender --background --python expand_chatgpt_city.py
```

The city expansion reads `chatgpt_god.blend` and writes new files with the `chatgpt_god_expanded_city` prefix. The original scene remains intact.
