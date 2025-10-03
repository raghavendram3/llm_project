# Slab Agent

A natural language-driven tool for generating crystallographic surface slabs from bulk structures using Materials Project and ASE.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Slab Agent simplifies the process of creating surface slab models for computational materials science. Simply describe what you need in natural language, and the tool will:

1. Fetch bulk crystal structures from Materials Project
2. Generate surface slabs with specified Miller indices
3. Configure layers, vacuum spacing, and supercell dimensions
4. Export to standard crystallography formats (CIF, POSCAR)

### Key Features

- **Natural Language Queries**: No need to remember complex command syntax
- **Materials Project Integration**: Access to 150,000+ crystal structures
- **Flexible Surface Generation**: Customize Miller indices, layers, vacuum, and supercell
- **Multiple Output Formats**: Automatically generates CIF and POSCAR files
- **Simple CLI**: Easy to integrate into workflows and scripts

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/raghavendram3/llm_project.git
cd llm_project
```

### 2. Set Up Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Materials Project API Key

Obtain your free API key from [Materials Project](https://materialsproject.org/api).

**Option 1: Environment File (Recommended)**
```bash
cp .env.example .env
# Edit .env and add your key:
# MP_API_KEY=your_api_key_here
```

**Option 2: Environment Variable**
```bash
export MP_API_KEY=your_api_key_here
```

## Usage

### Basic Examples

**Create a silicon (111) surface:**
```bash
python -m llm_project.cli "Create a Si (111) slab with 6 layers and 15 Å vacuum"
```

**Use a Materials Project ID:**
```bash
python -m llm_project.cli "mp-149 (100) 8 layers 12 A vacuum"
```

**Add in-plane supercell:**
```bash
python -m llm_project.cli "SrTiO3 (100) 7 layers 18 Å vacuum 3x2 supercell"
```

**Specify custom output directory:**
```bash
python -m llm_project.cli "Si (111) 6 layers 15 Å vacuum 2x2" -o my_outputs
```

### Query Syntax Guide

The tool intelligently parses natural language queries. You can mix and match these parameters:

| Parameter | Examples | Default |
|-----------|----------|---------|
| **Material** | `Si`, `SiO2`, `SrTiO3`, `mp-149` | Required |
| **Miller Indices** | `(111)`, `(100)`, `(1,1,-1)`, `110` | Required |
| **Layers** | `6 layers`, `layers 8` | 6 |
| **Vacuum** | `15 Å vacuum`, `12 A vacuum`, `vacuum 20` | 15 Å |
| **Supercell** | `2x2`, `3×2`, `repeat 2 3` | 1×1 |

### More Query Examples

```bash
# Complex oxide surface
python -m llm_project.cli "Create a SrTiO3 (100) slab with 8 layers and 20 Å vacuum, 2x2 supercell"

# Using Materials Project ID
python -m llm_project.cli "mp-149 (110) 10 layers 18 A vacuum 3x3"

# Minimal specification (uses defaults)
python -m llm_project.cli "Si (111)"

# Non-standard Miller indices
python -m llm_project.cli "GaAs (1,1,-1) 7 layers 16 Å vacuum"
```

## Output Files

Generated files are saved to `slabs_out/` (or your specified directory) with descriptive names:

```
<material>_<hkl>_<layers>L_<vacuum>A_<supercell>.cif
POSCAR_<material>_<hkl>_<layers>L_<vacuum>A_<supercell>
```

**Example:**
```
slabs_out/
├── Si_111_6L_15A_2x2.cif
└── POSCAR_Si_111_6L_15A_2x2
```

## Project Structure

```
llm_project/
├── cli.py                      # Command-line interface
├── agent.py                    # Main orchestration logic
├── parsing.py                  # Natural language parser
├── tools/
│   ├── materials_project.py   # Materials Project API integration
│   └── ase_tools.py           # ASE slab generation and file I/O
└── __init__.py
```

## Technical Details

### Dependencies

- **mp-api**: Modern Materials Project API client
- **pymatgen**: Materials analysis and structure manipulation
- **ASE** (Atomic Simulation Environment): Surface slab generation
- **python-dotenv**: Environment variable management

### Workflow

1. **Query Parsing**: Extracts material, Miller indices, and parameters from natural language
2. **Structure Retrieval**: Fetches bulk structure from Materials Project using formula or MP ID
3. **Format Conversion**: Converts pymatgen Structure to ASE Atoms via `AseAtomsAdaptor`
4. **Slab Generation**: Creates surface using `ase.build.surface()` with specified parameters
5. **Supercell Expansion**: Replicates in-plane unit cells using `Atoms.repeat((nx, ny, 1))`
6. **File Export**: Saves to CIF and POSCAR formats

## Requirements

- Python 3.8 or higher
- Valid Materials Project API key
- Internet connection (for structure retrieval)

## Common Use Cases

- **Surface Chemistry Studies**: Generate clean surfaces for adsorption calculations
- **Catalysis Research**: Model catalyst surfaces with different facets
- **DFT Calculations**: Prepare input structures for VASP, Quantum ESPRESSO, etc.
- **Material Screening**: Rapidly generate surface models for high-throughput studies

## Troubleshooting

**Issue**: `MP_API_KEY not found`
- **Solution**: Ensure your `.env` file exists and contains `MP_API_KEY=your_key` or export the environment variable

**Issue**: Material not found
- **Solution**: Verify the chemical formula or check the MP ID at [Materials Project website](https://materialsproject.org)

**Issue**: Import errors
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License.

## Citation

If you use this tool in your research, please cite:
- [Materials Project](https://materialsproject.org)
- [ASE](https://wiki.fysik.dtu.dk/ase/)
- [Pymatgen](https://pymatgen.org)

## Acknowledgments

Built with:
- [Materials Project API](https://github.com/materialsproject/api) for structure data
- [Atomic Simulation Environment (ASE)](https://wiki.fysik.dtu.dk/ase/) for slab generation
- [Pymatgen](https://pymatgen.org) for materials analysis
