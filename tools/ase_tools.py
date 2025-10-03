import os
from typing import Tuple, List

from ase.atoms import Atoms
from ase.build import surface
from ase.io import write
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor


def structure_to_atoms(struct: Structure) -> Atoms:
    """
    Convert a pymatgen Structure to an ASE Atoms object.
    """
    adaptor = AseAtomsAdaptor()
    return adaptor.get_atoms(struct)


def build_slab(
    bulk: Atoms,
    miller: Tuple[int, int, int],
    layers: int = 6,
    vacuum: float = 15.0,
    center: bool = True,
) -> Atoms:
    """
    Build a surface slab from a bulk Atoms object using ASE.

    Parameters:
        bulk: ASE Atoms bulk structure
        miller: Miller indices (h, k, l)
        layers: Number of atomic layers
        vacuum: Vacuum thickness in Angstrom
        center: Whether to center the slab in the cell (ASE centers by default)

    Returns:
        ASE Atoms slab
    """
    h, k, l = miller
    slab = surface(bulk, (h, k, l), layers=layers, vacuum=vacuum, periodic=True)
    # ASE's surface() already centers slab along z with vacuum. Return as-is.
    return slab


def apply_supercell(atoms: Atoms, nx: int, ny: int) -> Atoms:
    """
    Apply in-plane supercell repetition.
    """
    if nx <= 0 or ny <= 0:
        raise ValueError("Supercell repeats must be positive integers.")
    return atoms.repeat((nx, ny, 1))


def save_outputs(atoms: Atoms, outdir: str, base_name: str) -> List[str]:
    """
    Save slab to CIF and POSCAR (VASP) formats.

    Returns list of file paths.
    """
    os.makedirs(outdir, exist_ok=True)
    paths: List[str] = []

    cif_path = os.path.join(outdir, f"{base_name}.cif")
    write(cif_path, atoms)
    paths.append(cif_path)

    poscar_path = os.path.join(outdir, f"POSCAR_{base_name}")
    write(poscar_path, atoms, format="vasp")
    paths.append(poscar_path)

    return paths
