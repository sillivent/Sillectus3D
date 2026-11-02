# Sillectus3D

One Blender 5.2 LTS script that builds a V5 Starship and Super Heavy launch complex.

`v5_starship_full.py` is the file to run. The numbered scripts are the same code, one object at a time, cut from that file so they cannot drift. Each numbered file clears the scene and builds only its object.

## How to run

1. Download `v5_starship_full.py`, or clone this repo.
2. Blender → **Scripting** workspace → **Text → Open** → select the file.
3. **Run Script**.

Do not paste the script into the Python console. Do not paste shell commands into the Python console. Those are not Blender commands and they raise `NameError` or `SyntaxError`.

The script clears the scene and rebuilds it. z = 0 is the concrete the trucks stand on.

## Datum

| | |
|---|---|
| Hull diameter | 30 m, so a Tesla Semi with trailer fits in the cargo bay |
| Booster | 60% of the vehicle stack (192 m), skirt at z = 3.2 |
| Ship | 40% of the vehicle stack (128 m), sitting flush on the booster |
| Pad | OLM ring stays at pad height. Its columns reach the trench floor |

## What the scene is

| Side | What is there |
|---|---|
| +X | Passenger tower and its own podium, glass lobby, jetway on a truss tied to the tower columns, horseshoe cockpit, seven cabin decks, engineering ports, wide cargo door. The cargo elevator rails run inside the tower and a bridge meets the door. The terminal sits beside the tower and connects with a concourse. |
| ±Y | Stabilizer fins, 25% larger and scaled with the hull. Forward fins have no hinge cans. |
| −X | Heat-shield tiles from fin hinge to fin hinge. Mechazilla stands on this side. Above the cockpit the tiles wrap a smooth von Karman nose. Fuel umbilicals dogleg around the tiles and meet the hull on the steel. |

The booster skirt is clamped by the orbital launch mount. The bells hang into the flame trench. One sleeve crosses the joint. There is no gap and no floating interstage.

The upper half of the ship is the flight deck plus nine decks: seven passenger decks, then engineering and life support, then the cargo bay. The lower half is tankage.

## License

MIT
