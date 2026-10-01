"""
hitung_luas_lingkaran.py

Utility module containing a single function to calculate the area of a circle.

The function validates its input and raises informative exceptions for
invalid arguments. It uses the built‑in `math` module for the constant π.

Example
-------
>>> hitung_luas_lingkaran(2)
12.566370614359172
"""

from __future__ import annotations

import math
from typing import Union


def hitung_luas_lingkaran(radius: Union[int, float]) -> float:
    """
    Calculate the area of a circle given its radius.

    Parameters
    ----------
    radius : int | float
        The radius of the circle. Must be a non‑negative real number.

    Returns
    -------
    float
        The area of the circle (π·r²).

    Raises
    ------
    TypeError
        If ``radius`` is not an ``int`` or ``float``.
    ValueError
        If ``radius`` is negative.

    Notes
    -----
    The function deliberately avoids any heavy or unsafe imports.
    It uses ``math.pi`` for the value of π, which provides sufficient
    precision for typical applications.

    The return type is always ``float`` even when the input is an ``int``.
    """
    # Type validation
    if not isinstance(radius, (int, float)):
        raise TypeError(
            f"radius must be an int or float, got {type(radius).__name__!r}"
        )

    # Value validation
    if radius < 0:
        raise ValueError("radius cannot be negative")

    # Compute area
    area: float = math.pi * (float(radius) ** 2)
    return area


# --------------------------------------------------------------------------- #
# Optional: simple command‑line interface for quick manual testing.
# This block is ignored when the module is imported.
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import sys

    def _print_usage() -> None:
        prog = sys.argv[0]
        print(f"Usage: python {prog} <radius>")
        print("Calculate the area of a circle with the given radius.")
        print("Example: python {prog} 3.5")

    if len(sys.argv) != 2:
        _print_usage()
        sys.exit(1)

    try:
        r_input = float(sys.argv[1])
        result = hitung_luas_lingkaran(r_input)
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"Radius: {r_input}")
    print(f"Area  : {result}")