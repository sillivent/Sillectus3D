# Sillectus3D

One Blender 5.2 LTS script that builds a V5 Starship + Super Heavy launch complex.

`v5_starship_full.py` is the only current script. Run that file. Do not paste shell commands into Blender's Python console.

## How to run

1. Download `v5_starship_full.py` (or clone this repo).
2. Blender → **Scripting** workspace → **Text → Open** → select the file.
3. **Run Script** (Alt+P).

The script clears the scene and rebuilds it. z = 0 is the concrete the trucks stand on.

## What the scene is

| Side | What is there |
|---|---|
| +X | Passenger tower, glass lobby, jetway, cockpit, four rows of horizontal oval cabin windows, 5 m cargo door |
| ±Y | Four stabilizer flaps. Forward flaps have no hinge cans. |
| −X | Ceramic heat-shield belly. Mechazilla stands on this side. Fuel umbilicals meet the hull at 100°, off the tiles. |

The booster skirt is clamped by the orbital launch mount at pad level. The bells hang into the flame trench. The ship sits on the booster; one sleeve crosses the joint. There is no gap and no floating interstage ring.

Passenger elevator is inside the crew tower and opens into the glass lobby. The jetway leaves that lobby and docks on the ship between cabin rows, so it does not cover a window. The cargo elevator is an open steel box on cables, with a deck out to the cargo door.

## License

MIT
