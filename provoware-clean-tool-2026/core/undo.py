"""Wrapper for undo functionality.

This module exposes the `undo_last` function from `core.executor` to provide
a stable import path. Using a separate module prevents circular imports
between GUI code and executor logic.
"""

from .executor import undo_last  # re‑export for convenience

__all__ = ["undo_last"]
