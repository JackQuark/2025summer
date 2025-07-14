# _summary_
# author: Quark
# ==================================================
import sys
import os
import numpy     as np
import xarray    as xr
import matplotlib.pyplot  as plt

sys.path.append("/home/Quark/2025summer/tools")
from dycore_dataset import Dataset
from ufunc import *
# ==================================================
# calc. the mean state of atm from 1000 ~ 2000d data
def save_mean_ps(ds: Dataset):
    """global mean ps"""    
    meanps = 0
    count = 0
    for iday in range(1000, 2000, 25):
        print(f"processing start from {iday} day", end='\r')
        f = ds.open_HDF5(iday)
        meanps += np.mean(f['grid_ps_c_xyzt'][:])
        count += 1
        f.close()
    meanps /= count
    with open("meanps.txt", "w") as f:
        f.write(f"{meanps:.5f}")
    print(f"mean surface pressure: {meanps:.2f} Pa")
    
def lin_interp(x, xp, fp):
    if x[-1] > xp[-1]:
        s = (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
        right_val = fp[-1] + (x[-1] - xp[-1]) * s
    else:
        right_val = fp[-1]
    return np.interp(x, xp, fp, right=right_val)

def interp_2_refp(ref_p: np.ndarray):
    datadir = "/data92/Quark/ctrl_2000d/HSt42_20"
    ds = Dataset(datadir)
    tavg = np.zeros((20, 64))
    qvavg = np.zeros((20, 64))
    count = 0
    for iday in range(1000, 2000, 25):
        print(f"processing start from {iday} day", end='\r')
        f = ds.open_HDF5(iday)
        # (time, lev, lat, lon)
        # (100, 20, 64, 128)       
        p  = xr.DataArray(f['grid_p_full_xyzt'][:], dims=('time','lev','lat','lon'))
        t  = xr.DataArray(f['grid_t_c_xyzt'][:],    dims=('time','lev','lat','lon'))
        qv = xr.DataArray(f['grid_tracers_c_xyzt'][:], dims=('time','lev','lat','lon'))

        # like np.apply_along_axis but more flexible :D
        t_interp: np.ndarray = xr.apply_ufunc(
            lin_interp,
            ref_p, p, t,
            input_core_dims=[['pref'], ['lev'], ['lev']],
            output_core_dims=[['pref']],
            vectorize=True,            
            output_dtypes=[t.dtype]
            ).to_numpy().transpose(0, 3, 1, 2)
        qv_interp = xr.apply_ufunc(
            lin_interp,
            ref_p, p, qv,
            input_core_dims=[['pref'], ['lev'], ['lev']],
            output_core_dims=[['pref']],
            vectorize=True,            
            output_dtypes=[qv.dtype]
            ).to_numpy().transpose(0, 3, 1, 2)

        tavg  += np.mean(t_interp, axis=(0, 3))
        qvavg += np.mean(qv_interp, axis=(0, 3))
        count += 1
        f.close()
        
    tavg  /= count
    qvavg /= count
    # save
    np.save("avg_t.npy", tavg)
    np.save("avg_qv.npy", qvavg)

def main():
    datadir = "/data92/Quark/ctrl_2000d"
    ds = Dataset(datadir)
    
    with open("mean_ps.txt", "r") as f:
        meanps = float(f.read())    

    ref_p_full = ps_to_p_full(meanps)
    
    print(ref_p_full)
    
    # np.savetxt("mean_p_full.dat", ref_p_full)
    # interp_2_refp(ref_p=ref_p_full)

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
