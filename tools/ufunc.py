# _summary_
# author: Quark
# ==================================================
import numpy     as np
from dycore_dataset import Dataset
from dycore_info import *

from typing import Literal
# ==================================================
__all__ = ['calc_center_λθ', 'calc_mean_state', 'ps_to_p_half', 'ps_to_p_full']
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

def calc_mean_state(
    ds: Dataset, var_name: str | list[str], 
    start_day: int, end_day: int,
    axis = (0, 2, 3)
    ): 
    if isinstance(var_name, str):
        var_name = [var_name]
        
    if start_day < 0: raise ValueError("start_day must be non-negative")    
    res = {}
    # 1 file 
    f = ds.open_HDF5(start_day)
    for v in var_name: 
        res[v] = np.mean(f[v][4 * (start_day % ds.of_interval):, ...], axis=axis)
    f.close()

    # 2~-2 files 
    iday = np.arange((start_day//ds.of_interval+1)*ds.of_interval,
                     (end_day//ds.of_interval)*ds.of_interval, ds.of_interval)
    for i in iday:
        f = ds.open_HDF5(i)
        for v in var_name:
            res[v] += np.mean(f[v][...], axis=axis)
        f.close()

    # -1 file
    f = ds.open_HDF5(end_day)
    for v in var_name:
        res[v] += np.mean(f[v][:4 * (end_day % ds.of_interval + 1), ...], axis=axis)
    f.close()
    
    for k, v in res.items():
        print(k, v.shape)
    return res

def ps_to_p_half(ps, nd: int=20):
    """convert surface pressure to level boundary pressure"""
    ak = np.zeros(nd+1)
    bk = np.linspace(0, 1, nd+1)
    return ak + bk * ps

def ps_to_p_full(ps, nd: int=20):
    """convert surface pressure to column pressure"""
    p_half = ps_to_p_half(ps, nd)
    Δp     = p_half[1:] - p_half[:-1]
    lnp_half = np.log(p_half, where=p_half!=0)
    lnp_full = lnp_half[1:] + \
        p_half[:-1] * (lnp_half[1:] - lnp_half[:-1]) / Δp - 1.0
    
    lnp_half[0] = 0.0
    lnp_full[0] = lnp_half[1] - 1.0
    return np.exp(lnp_full)

def main():
    expdir = "/data92/Quark/ctrl_2000d"
    ds = Dataset(expdir)
    calc_mean_state(ds, 'grid_t_c_xyzt', 500, 999)

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
