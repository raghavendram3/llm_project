# llm_project: Slab Agent

An agent that uses Materials Project (mp-api/pymatgen) and ASE to generate slab models from a natural-language query.

Features:
- Fetch a bulk structure by MP ID (e.g., mp-149) or chemical formula (e.g., Si, SiO2) using Materials Project
- Convert fetched structure (pymatgen Structure) to ASE Atoms
- Build a surface/slab via ASE with configurable Miller indices, number of layers, vacuum, and in-plane supercell
- Save slabs to CIF and POSCAR formats
- Simple CLI for queries like:
  - "Create a Si (111) slab with 6 layers, 15 Å vacuum, 2x2 supercell"
  - "mp-149 (100), 8 layers, 12 A vacuum"

## Installation

1) Create and activate a virtual environment (recommended)

   macOS/Linux:
   - python3 -m venv .venv
   - source .venv/bin/activate

   Windows (PowerShell):
   - py -m venv .venv
   - .venv\\Scripts\\Activate.ps1

2) Install dependencies

   pip install -r requirements.txt

3) Set your Materials Project API key

   - Copy `.env.example` to `.env` and place your key there, or export it as an environment variable.

   echo "MP_API_KEY=YOUR_KEY_HERE" > .env

   Or export:
   export MP_API_KEY=YOUR_KEY_HERE

   You can obtain an API key from: https://materialsproject.org/api

## Usage

Basic example (formula-based):
- python -m llm_project.cli "Create a Si (111) slab with 6 layers and 15 Å vacuum"

With explicit options:
- python -m llm_project.cli "Si (111) 6 layers 15 Å vacuum 2x2" -o outputs

Using an MP ID:
- python -m llm_project.cli "mp-149 (100) 8 layers 12 A vacuum"

This will:
1) Fetch a bulk structure from Materials Project
2) Convert to ASE Atoms
3) Build the surface slab
4) Save CIF and POSCAR files to the output folder (default: `slabs_out/`)

## Natural-language parameters parsed

- Formula or MP ID:
  - Examples: "Si", "SiO2", "SrTiO3", "mp-149"
- Miller indices:
  - Examples: "(1 1 1)", "(100)", "(1, 1, -1)", or "111"
- Layers:
  - Examples: "6 layers", "layers 8" (default: 6)
- Vacuum:
  - Examples: "15 Å vacuum", "12 A vacuum", "vacuum 20" (default: 15 Å)
- Supercell (in-plane):
  - Examples: "2x2", "3×2", "repeat 2 3" (default: 1x1)

## Outputs

- CIF: saved as `<formula_or_id>_hkl_layers_vacuum_supercell.cif`
- POSCAR: saved as `POSCAR_<formula_or_id>_hkl_layers_vacuum_supercell`

## Notes

- This agent prefers the newer `mp-api` client. If unavailable, it may fall back to `pymatgen`'s `MPRester` if present.
- Conversion uses `pymatgen.io.ase.AseAtomsAdaptor`.
- Slab building is via `ase.build.surface` and in-plane replication via `Atoms.repeat((nx, ny, 1))`.

## Development

Project structure:
- llm_project/
  - cli.py           # CLI entrypoint
  - agent.py         # Orchestrates query -> MP fetch -> ASE slab -> save
  - parsing.py       # Simple query parser for hkl, layers, vacuum, supercell
  - tools/
    - materials_project.py  # Fetch structures from Materials Project
    - ase_tools.py          # Convert to ASE, build slab, save files
  - __init__.py

## Example queries

- "Create a Si (111) slab with 8 layers and 20 Å vacuum, 2x2 supercell"
- "mp-149 (100) 6 layers 15 A vacuum"
- "SrTiO3 (1 0 0) layers 7 vacuum 18 Å 3x2"
