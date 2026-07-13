"""
Type stub for pya_resolver.py

Pylance cannot statically resolve the try/except import pattern:
    try:
        import pya          # KLayout Editor session
    except ImportError:
        import klayout.db as pya   # Standalone session

This stub tells Pylance to always treat `pya` as `klayout.db`
so the shipped klayout stubs (dbcore.pyi) are used for type resolution.
"""

import klayout.db as pya
import klayout.lay as lay

def is_standalone_session() -> bool: ...
def klayout_executable_command() -> str | None: ...

__all__ = ["pya", "lay", "is_standalone_session", "klayout_executable_command"]