import os
from typing import Optional, Tuple

from dotenv import load_dotenv

try:
    # Preferred modern client (required)
    from mp_api.client import MPRester as MPAPIMPRester  # type: ignore
except Exception:
    MPAPIMPRester = None  # type: ignore

from pymatgen.core import Structure


def _load_api_key(provided: Optional[str] = None) -> Optional[str]:
    """
    Load MP API key from provided argument or environment.
    Looks for MP_API_KEY (preferred) or MAPI_KEY (legacy).
    """
    load_dotenv()
    return provided or os.getenv("MP_API_KEY") or os.getenv("MAPI_KEY")


class MaterialsProjectTool:
    """
    Wrapper around Materials Project APIs using mp-api exclusively.
    Legacy pymatgen MPRester fallback is not used due to removed/limited methods in recent versions.
    """

    def __init__(self, api_key: Optional[str] = None, prefer_mp_api: bool = True):
        self.api_key = _load_api_key(api_key)

    # ---- Internal helpers ----
    def _require_mp_api(self):
        if MPAPIMPRester is None:
            raise ImportError(
                "mp-api is not installed. Please install 'mp-api' to use Materials Project tools."
            )

    def _get_mp_api_client(self):
        self._require_mp_api()
        return MPAPIMPRester(self.api_key) if self.api_key else MPAPIMPRester()

    def _ensure_api_key(self):
        if not self.api_key:
            raise RuntimeError(
                "Materials Project API key not found. Set MP_API_KEY (preferred) or MAPI_KEY "
                "in your environment or .env file."
            )

    # ---- Public API ----
    def get_structure_by_mp_id(self, mp_id: str) -> Structure:
        """
        Fetch a Pymatgen Structure by MP material ID, e.g., 'mp-149'.
        """
        mp_id = mp_id.strip()
        self._require_mp_api()
        self._ensure_api_key()

        try:
            with self._get_mp_api_client() as mpr:
                results = mpr.materials.summary.search(
                    material_ids=[mp_id],
                    fields=["material_id", "structure"],
                )
                if not results:
                    raise RuntimeError(f"No structure found for {mp_id}")
                doc = results[0]
                try:
                    struct = getattr(doc, "structure")
                except Exception:
                    struct = doc.get("structure")
                if struct is None:
                    raise RuntimeError(f"No structure found for {mp_id}")
                return struct
        except Exception as e:
            msg = str(e)
            if "Invalid or old API key" in msg or "401" in msg:
                raise RuntimeError(
                    "Invalid or old Materials Project API key. Obtain a new key from "
                    "https://materialsproject.org/dashboard and set MP_API_KEY."
                ) from e
            raise RuntimeError(
                f"Failed to fetch structure for {mp_id} via mp-api. Error: {e}"
            ) from e

    def get_structure_by_formula(self, formula: str) -> Tuple[Structure, str]:
        """
        Fetch the most stable (lowest energy above hull) structure by formula.
        Returns (Structure, material_id).
        """
        formula = formula.strip()
        self._require_mp_api()
        self._ensure_api_key()

        try:
            with self._get_mp_api_client() as mpr:
                results = mpr.materials.summary.search(
                    formula=formula,
                    fields=["material_id", "energy_above_hull", "structure"],
                )
                if not results:
                    raise RuntimeError(f"No materials found for formula '{formula}'")

                # Choose entry with the lowest energy_above_hull if available
                def _get(doc, attr):
                    try:
                        return getattr(doc, attr)
                    except Exception:
                        try:
                            return doc.get(attr)  # type: ignore[attr-defined]
                        except Exception:
                            return None

                results_sorted = sorted(
                    results,
                    key=lambda d: (float("inf") if _get(d, "energy_above_hull") is None else _get(d, "energy_above_hull"))
                )
                top = results_sorted[0]
                mp_id = _get(top, "material_id")
                if not mp_id:
                    raise RuntimeError("materials.summary.search did not return a material_id")
                # Extract structure directly from summary results
                try:
                    struct = getattr(top, "structure")
                except Exception:
                    struct = top.get("structure")
                if struct is None:
                    raise RuntimeError(f"No structure found for material_id {mp_id}")
                return struct, mp_id
        except Exception as e:
            msg = str(e)
            if "Invalid or old API key" in msg or "401" in msg:
                raise RuntimeError(
                    "Invalid or old Materials Project API key. Obtain a new key from "
                    "https://materialsproject.org/dashboard and set MP_API_KEY."
                ) from e
            raise RuntimeError(
                f"Failed to fetch structure for formula '{formula}' via mp-api. Error: {e}"
            ) from e
