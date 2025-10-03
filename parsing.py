from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple

from pymatgen.core.composition import Composition


@dataclass
class QueryParams:
    mp_id: Optional[str]
    formula: Optional[str]
    miller: Tuple[int, int, int]
    layers: int
    vacuum: float
    supercell: Tuple[int, int]


DEFAULT_MILLER: Tuple[int, int, int] = (1, 0, 0)
DEFAULT_LAYERS = 6
DEFAULT_VACUUM = 15.0
DEFAULT_SUPERCELL: Tuple[int, int] = (1, 1)

STOPWORDS = {
    "create",
    "make",
    "build",
    "a",
    "an",
    "the",
    "with",
    "and",
    "for",
    "surface",
    "slab",
    "supercell",
    "vacuum",
    "layers",
    "layer",
    "repeat",
    "of",
    "to",
}


def parse_miller(text: str) -> Tuple[int, int, int]:
    """
    Parse Miller indices (hkl) from text.
    Accepts forms:
      - (1 1 1), (1, 1, 1), (1,1,1)
      - (100)
      - 111 (less reliable, only used if unambiguous)
    """
    # Prefer explicit parentheses
    m = re.search(r"\(\s*([-\d,\s]+)\s*\)", text)
    if m:
        inner = m.group(1).replace(",", " ").strip()
        parts = [p for p in inner.split() if p]
        if len(parts) == 3:
            try:
                h, k, l = (int(parts[0]), int(parts[1]), int(parts[2]))
                return (h, k, l)
            except ValueError:
                pass
        elif len(parts) == 1:
            token = parts[0]
            # Allow compact form e.g. "111"
            if re.fullmatch(r"\d{3}", token):
                return (int(token[0]), int(token[1]), int(token[2]))

    # Fallback: look for standalone compact form like "111"
    m2 = re.search(r"\b(\d{3})\b", text)
    if m2:
        tok = m2.group(1)
        return (int(tok[0]), int(tok[1]), int(tok[2]))

    return DEFAULT_MILLER


def parse_layers(text: str, default: int = DEFAULT_LAYERS) -> int:
    m = re.search(r"(\d+)\s*layers?", text, flags=re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    # Allow "layers 8"
    m2 = re.search(r"layers?\s*(\d+)", text, flags=re.IGNORECASE)
    if m2:
        try:
            return int(m2.group(1))
        except ValueError:
            pass
    return default


def parse_vacuum(text: str, default: float = DEFAULT_VACUUM) -> float:
    # Pattern: "15 Å vacuum" or "15 A vacuum"
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:Å|A)\s*vacuum", text, flags=re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    # Pattern: "vacuum 15"
    m2 = re.search(r"vacuum\s*(\d+(?:\.\d+)?)", text, flags=re.IGNORECASE)
    if m2:
        try:
            return float(m2.group(1))
        except ValueError:
            pass
    return default


def parse_supercell(text: str, default: Tuple[int, int] = DEFAULT_SUPERCELL) -> Tuple[int, int]:
    # Pattern: "2x3", "2×3"
    m = re.search(r"(\d+)\s*[x×]\s*(\d+)", text, flags=re.IGNORECASE)
    if m:
        try:
            return int(m.group(1)), int(m.group(2))
        except ValueError:
            pass
    # Pattern: "repeat 2 3"
    m2 = re.search(r"repeat\s+(\d+)\s+(\d+)", text, flags=re.IGNORECASE)
    if m2:
        try:
            return int(m2.group(1)), int(m2.group(2))
        except ValueError:
            pass
    return default




def parse_mp_id(text: str) -> Optional[str]:
    m = re.search(r"\bmp-\d+\b", text, flags=re.IGNORECASE)
    return m.group(0) if m else None


def _validate_formula(token: str) -> bool:
    try:
        # This will raise if token is not a valid chemical formula
        Composition(token)
        return True
    except Exception:
        return False


def parse_formula(text: str) -> Optional[str]:
    """
    Heuristically parse a chemical formula from text.
    Strategy:
      - If token immediately before "(...)" looks like a formula and validates, use it.
      - Else, scan tokens that start with uppercase letters, validate via pymatgen Composition.
      - Skip common stopwords.
    """
    # Try token before parentheses
    before_paren = re.search(r"([A-Za-z][A-Za-z0-9]*)\s*\(", text)
    if before_paren:
        tok = before_paren.group(1)
        if tok.lower() not in STOPWORDS and _validate_formula(tok):
            return tok

    # General scan
    for tok in re.findall(r"\b[A-Za-z][A-Za-z0-9]*\b", text):
        if tok.lower() in STOPWORDS:
            continue
        # Prefer tokens starting uppercase (chemical symbols)
        if not tok[0].isupper():
            continue
        # Keep token length reasonable
        if len(tok) > 20:
            continue
        if _validate_formula(tok):
            return tok

    return None


def parse_query(query: str) -> QueryParams:
    """
    Parse a natural-language query into structured parameters.
    """
    mp_id = parse_mp_id(query)
    formula = None if mp_id else parse_formula(query)
    miller = parse_miller(query)
    layers = parse_layers(query)
    vacuum = parse_vacuum(query)
    supercell = parse_supercell(query)

    return QueryParams(
        mp_id=mp_id,
        formula=formula,
        miller=miller,
        layers=layers,
        vacuum=vacuum,
        supercell=supercell,
    )
