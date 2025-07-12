# _summary_
# author: Quark
# ==================================================
import sys
import os
import numpy     as np
import matplotlib.pyplot  as plt

from typing import Literal, Union, Tuple, List, Dict, Any, Optional
# ==================================================
__all__ = ['calc_center_λθ']
# ==================================================
def calc_center_λθ(nλ, nθ, unit: Literal['rad', 'deg']='rad'):
    """calc. grid center of longitude and latitude"""
    dλ = 360/nλ
    dθ = 180/nθ
    λc = -180 + dλ/2 + np.arange(nλ)*dλ
    θc = -90 + dθ/2 + np.arange(nθ)*dθ
    if unit == 'rad':
        λc = np.deg2rad(λc)
        θc = np.deg2rad(θc)
    return λc, θc


def main():
    pass

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
