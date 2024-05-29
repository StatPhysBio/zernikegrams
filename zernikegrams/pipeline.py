
from zernikegrams.structural_info import get_structural_info_fn
from zernikegrams.neighborhoods import get_neighborhoods_fn
from zernikegrams.holograms import get_holograms_fn

from typing import *

# @profile
def get_zernikegrams_from_pdbfile(pdbfile: str,
                                     get_structural_info_kwargs: Dict,
                                     get_neighborhoods_kwargs: Dict,
                                     get_zernikegrams_kwargs: Dict):

    proteins = get_structural_info_fn(pdbfile, **get_structural_info_kwargs)
    
    neighborhoods = get_neighborhoods_fn(proteins, **get_neighborhoods_kwargs)

    zernikegrams = get_holograms_fn(neighborhoods, **get_zernikegrams_kwargs)

    return zernikegrams



