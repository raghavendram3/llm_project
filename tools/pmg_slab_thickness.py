from __future__ import annotations

from typing import Tuple

from ase.atoms import Atoms
from pymatgen.core import Structure
from pymatgen.core.surface import SlabGenerator
from pymatgen.io.ase import AseAtomsAdaptor


def pmg_slab_with_thickness_to_ase(
    struct: Structure,
    miller: Tuple[int, int, int],
    thickness: float,
    vacuum: float,
    *,
    center: bool = True,
) -> Atoms:
    """
    Build a slab using pymatgen's SlabGenerator with a target slab thickness (Angstrom).
    Returns an ASE Atoms object for downstream handling.
    """
    if thickness <= 0:
        raise ValueError("thickness must be > 0 Angstrom.")

    if vacuum <= 0:
        raise ValueError("vacuum must be > 0 Angstrom.")

    gen = SlabGenerator(
        initial_structure=struct,
        miller_index=miller,
        min_slab_size=thickness,
        min_vacuum_size=vacuum,
        center_slab=center,
        primitive=True,
    )
    slabs = gen.get_slabs(symmetrize=False)
    if not slabs:
        raise RuntimeError("SlabGenerator did not return any slabs; try increasing thickness or adjusting inputs.")
    chosen = slabs[0]
    adaptor = AseAtomsAdaptor()
    return adaptor.get_atoms(chosen)
