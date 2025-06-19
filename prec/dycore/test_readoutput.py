# _summary_
# author: Quark
# ==================================================
import numpy as np
import matplotlib.pyplot as plt
import h5py
# ==================================================

def read_Dycore_data(filepath, print_var=False):
    """
    Load Dycore data from HDF5 file.
    
    Parameters:
        filepath (str): Path to the Dycore HDF5 file.
        print_var (bool): If True, print available variable names.
    
    Returns:
        tuple: u, v, t, p, ps, w, phi arrays
    """
    with h5py.File(filepath, "r") as f:
        if print_var:            
            for key in f.keys():
                print(f[key])
                        
        u  = f["grid_u_c_xyzt"][:]     # Zonal wind
        v  = f["grid_v_c_xyzt"][:]     # Meridional wind
        t  = f["grid_t_c_xyzt"][:]     # Temperature
        p  = f["grid_p_full_xyzt"][:]  # 3D pressure
        ps = f["grid_ps_c_xyzt"][:]    # Surface pressure
        w  = f["grid_w_full_xyzt"][:]  # Vertical velocity
        phi = f["grid_geopots_xyzt"][:]  # Geopotential
        
    return u, v, t, p, ps, w, phi

def main():
    fname = "/home/Quark/Moist_Dycore/IdealizeSpetral/exp/HSt42/50day_PR10_for_check_warmstart_all.dat"
    
    u, v, t, p, ps, w, phi = read_Dycore_data(fname, print_var=False)
    pass

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
