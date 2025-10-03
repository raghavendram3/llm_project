from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from dotenv import load_dotenv

from .agent import SlabAgent


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="llm_project.cli",
        description="Agent that generates surface/slab models using Materials Project and ASE from a natural-language query.",
    )
    p.add_argument(
        "query",
        type=str,
        help='Natural-language query, e.g. "Create a Si (111) slab with 6 layers and 15 A vacuum 2x2"',
    )
    p.add_argument(
        "-o",
        "--outdir",
        type=str,
        default="slabs_out",
        help="Output directory for generated structures (default: slabs_out)",
    )
    p.add_argument(
        "--mp-api-key",
        type=str,
        default=None,
        help="Materials Project API key (overrides MP_API_KEY/MAPI_KEY env vars if provided)",
    )
    p.add_argument(
        "--no-mp-api",
        action="store_true",
        help="Disable mp-api usage and force legacy pymatgen MPRester if available.",
    )
    p.add_argument(
        "--thickness",
        type=str,
        default=None,
        help="Target slab thickness in Angstroms or '<factor>d' times d_hkl (e.g., 7.5 or 1.5d). Overrides integer layers."
    )
    return p


def main(argv: Optional[list[str]] = None) -> int:
    # Load MP_API_KEY from root .env and package .env (llm_project/.env) if present
    load_dotenv()
    try:
        package_env = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(package_env):
            load_dotenv(package_env, override=False)
    except Exception:
        # Non-fatal; proceed if package .env isn't accessible
        pass
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    agent = SlabAgent(
        mp_api_key=args.mp_api_key,
        prefer_mp_api=not args.no_mp_api,
    )

    try:
        result = agent.run(
            query=args.query,
            outdir=args.outdir,
            thickness=args.thickness,
        )
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    print("Slab generation completed.")
    print(f"- Query: {result.query}")
    print(f"- Source: {result.source}")
    print(f"- MP ID: {result.mp_id or 'N/A'}")
    print(f"- Formula: {result.formula or 'N/A'}")
    print(f"- Thickness (A): {result.thickness if result.thickness is not None else 'N/A'}")
    h, k, l = result.miller
    print(f"- Miller indices: ({h} {k} {l})")
    print(f"- Layers: {result.layers}")
    print(f"- Vacuum (A): {result.vacuum}")
    nx, ny = result.supercell
    print(f"- Supercell: {nx}x{ny}")
    print(f"- Atoms in slab: {result.natoms}")
    print(f"- Output directory: {result.outdir}")
    print("- Files:")
    for p in result.file_paths:
        print(f"  * {p}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
