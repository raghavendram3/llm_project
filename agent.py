from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Tuple, Optional

from .parsing import parse_query, QueryParams
from .tools import (
    MaterialsProjectTool,
    structure_to_atoms,
    build_slab,
    apply_supercell,
    save_outputs,
    pmg_slab_with_thickness_to_ase,
)


@dataclass
class SlabResult:
    query: str
    source: str  # "mp_id" or "formula"
    mp_id: Optional[str]
    formula: Optional[str]
    miller: Tuple[int, int, int]
    layers: int
    vacuum: float
    supercell: Tuple[int, int]
    thickness: Optional[float]
    base_name: str
    outdir: str
    file_paths: List[str]
    natoms: int


def _sanitize_name(s: str) -> str:
    s = s.replace(" ", "")
    s = s.replace("/", "-")
    s = s.replace("\\", "-")
    s = s.replace("Å", "A")
    return s


def _hkl_to_str(hkl: Tuple[int, int, int]) -> str:
    def fmt(x: int) -> str:
        return f"m{abs(x)}" if x < 0 else str(x)

    h, k, l = hkl
    return f"{fmt(h)}_{fmt(k)}_{fmt(l)}"


class SlabAgent:
    """
    Orchestrates: parse -> fetch bulk -> convert -> build slab -> supercell -> save
    """

    def __init__(self, mp_api_key: Optional[str] = None, prefer_mp_api: bool = True):
        self.mpt = MaterialsProjectTool(api_key=mp_api_key, prefer_mp_api=prefer_mp_api)

    def run(self, query: str, outdir: str = "slabs_out", *, thickness: Optional[str] = None) -> SlabResult:
        params: QueryParams = parse_query(query)

        if not params.mp_id and not params.formula:
            raise ValueError(
                "Could not determine a material from the query. "
                "Please include a chemical formula (e.g., Si, SrTiO3) or an MP ID (e.g., mp-149)."
            )

        # Fetch structure
        mp_id: Optional[str] = None
        formula: Optional[str] = None
        if params.mp_id:
            source = "mp_id"
            mp_id = params.mp_id
            struct = self.mpt.get_structure_by_mp_id(mp_id)
            try:
                formula = struct.composition.reduced_formula
            except Exception:
                formula = None
        else:
            source = "formula"
            assert params.formula is not None
            struct, mp_id = self.mpt.get_structure_by_formula(params.formula)
            try:
                formula = struct.composition.reduced_formula
            except Exception:
                formula = params.formula

        # If thickness requested, build via pymatgen SlabGenerator using target thickness (Å)
        eff_thickness: Optional[float] = None
        if thickness is not None:
            # thickness can be a plain number in Å, or a factor times d_hkl specified as '<factor>d'
            t_str = str(thickness).strip().lower()
            try:
                if t_str.endswith("d"):
                    factor = float(t_str[:-1])
                    dhkl = struct.lattice.d_hkl(params.miller)
                    eff_thickness = max(0.01, factor * dhkl)
                else:
                    eff_thickness = float(t_str)
            except Exception:
                raise ValueError(f"Could not parse --thickness value '{thickness}'. Use numeric Å (e.g., 7.5) or '<factor>d' (e.g., 1.5d).")

        if eff_thickness is not None:
            # Build using pymatgen thickness (Å)
            slab = pmg_slab_with_thickness_to_ase(
                struct,
                params.miller,
                eff_thickness,
                params.vacuum,
            )
        else:
            # Convert to ASE and build using ASE surface() with integer layers
            bulk_atoms = structure_to_atoms(struct)
            slab = build_slab(
                bulk_atoms,
                params.miller,
                layers=params.layers,
                vacuum=params.vacuum,
            )

        # Apply supercell if needed
        nx, ny = params.supercell
        if (nx, ny) != (1, 1):
            slab = apply_supercell(slab, nx, ny)

        # Base name and save
        id_or_formula = mp_id or (formula or "material")
        base_name = _sanitize_name(
            f"{id_or_formula}_hkl{_hkl_to_str(params.miller)}_L{params.layers}_V{int(round(params.vacuum))}_S{nx}x{ny}"
        )
        file_paths = save_outputs(slab, outdir, base_name=base_name)

        return SlabResult(
            query=query,
            source=source,
            mp_id=mp_id,
            formula=formula,
            miller=params.miller,
            layers=params.layers,
            vacuum=params.vacuum,
            supercell=params.supercell,
            thickness=eff_thickness,
            base_name=base_name,
            outdir=outdir,
            file_paths=file_paths,
            natoms=len(slab),
        )
