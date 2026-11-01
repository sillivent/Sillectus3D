# Sillectus3D

Procedural Blender 5.2 LTS Python scripts for a detailed futuristic V5 Starship / Super Heavy launch complex.

## Contents

- `v5_starship_full.py` — Complete single-file scene generator (patched).
- `objects/` — Modular per-object scripts that share the same helpers and materials.

## Key Fixes in This Version

- Heat shield now covers the true belly (negative-Y windward side) instead of the side.
- Cockpit windows raised and moved to the leeward side.
- Four rows of more oval, horizontally-oriented cabin windows on the leeward face.
- Cargo bay door (≈5 m tall) placed on the leeward side below the cabin windows.
- Stabilizer fins retained on the lateral (±X) positions appropriate for a belly-flop vehicle.
- Launch pad / trench relationship tightened.
- Separate Mechazilla + passenger/cargo tower with jetway, elevator, and terminal.

## Usage

1. Open Blender 5.2 LTS.
2. Switch to the Scripting tab.
3. Open or paste `v5_starship_full.py`.
4. Run the script (Alt+P or the Run Script button).

The scene purges itself and rebuilds the full complex.

## License

MIT
