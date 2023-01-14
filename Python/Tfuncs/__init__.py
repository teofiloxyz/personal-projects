# Tfuncs is a custom functions package


from .menu import Menu
from .rofi_integration import Rofi as rofi
from .generic_input import Questions as qst
from .terminal_font import Fformat as ffmt, Fcolor as fcol, Bcolor as bcol

__all__ = ["menu", "terminal_font", "generic_input", "rofi_integration"]
