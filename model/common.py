from typing import Dict, List

from .masks import Mask

Grouping = Dict[Mask, List[str]]
Space = Dict[str, Grouping]

def load_file_as_list(filename: str) -> List[str]:
    with open(filename, "r") as infile:
        return infile.read().splitlines()


__all__ = ['Grouping', 'Space', 'load_file_as_list']
