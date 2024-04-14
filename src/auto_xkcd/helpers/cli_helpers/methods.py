from __future__ import annotations

from os import name, system

def clear():

    ## Windows
    if name == "nt":
        _: int = system("cls")

    ## POSIX
    else:
        _: int = system("clear")
