# Tfuncs is a custom functions package


from .generic_menu import menu as gmenu
from .rofi_integration import Rofi as rofi
from .generic_input import (Questions as qst,
                            Inputs as inpt,
                            Outputs as oupt)
from .terminal_font import (Fformat as ffmt,
                            Fcolor as fcol,
                            Bcolor as bcol)

__all__ = [
        'generic_menu',
        'terminal_font',
        'generic_input',
        'rofi_integration'
        ]
