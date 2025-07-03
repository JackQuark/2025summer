# _summary_
# author: Quark
# ==================================================
import sys
import os
import numpy     as np
import xarray    as xr
import matplotlib.pyplot  as plt

sys.path.append("/home/Quark/2025summer/tools")
from dycore_reader import Dataset
# ==================================================
# calc. the mean state of atm from 1000 ~ 2000d data

def save_mean_state(ds: Dataset):
    """wrong version"""
    meanp_tot  = np.zeros((20, 64))
    meanT_tot  = np.zeros((20, 64))
    meanqv_tot = np.zeros((20, 64))
    count = 0
    for iday in range(1000, 2000, 25):
        f  = ds.open_HDF5(iday)
        p  = f['grid_p_full_xyzt'][:]
        T  = f['grid_t_c_xyzt'][:]
        qv = f['grid_tracers_c_xyzt'][:]
        
        meanp_tot  += np.mean(p, axis=(0, 3))
        meanT_tot  += np.mean(T, axis=(0, 3))
        meanqv_tot += np.mean(qv, axis=(0, 3))
        count += 1
        f.close()
    
    meanp_tot  /= count
    meanT_tot  /= count
    meanqv_tot /= count
    np.save("meanp.npy",  meanp_tot)
    np.save("meanT.npy",  meanT_tot)
    np.save("meanqv.npy", meanqv_tot)

def lin_interp(x, xp, fp):
    if x[-1] > xp[-1]:
        s = (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
        right_val = fp[-1] + (x[-1] - xp[-1]) * s
    else:
        right_val = fp[-1]
    return np.interp(x, xp, fp, right=right_val)

def main():
    datadir = "/data92/Quark/ctrl_2000d/HSt42_20"
    ds = Dataset(datadir)
    p_ref = xr.DataArray(np.linspace(2000, 100000, 20), dims='pref')

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
            p_ref, p, t,
            input_core_dims=[['pref'], ['lev'], ['lev']],
            output_core_dims=[['pref']],
            vectorize=True,            
            output_dtypes=[t.dtype]
            ).to_numpy().transpose(0, 3, 1, 2)
        qv_interp = xr.apply_ufunc(
            lin_interp,
            p_ref, p, qv,
            input_core_dims=[['pref'], ['lev'], ['lev']],
            output_core_dims=[['pref']],
            vectorize=True,            
            output_dtypes=[qv.dtype]
            ).to_numpy().transpose(0, 3, 1, 2)

        tavg  += np.mean(t_interp, axis=(0, 3))
        qvavg += np.mean(qv_interp, axis=(0, 3))
        count += 1
        # t_interp = lin_interp(p_ref, p[0, :, 32, 0], t[0, :, 32, 0])
        # qv_interp = lin_interp(p_ref, p[0, :, 32, 0], qv[0, :, 32, 0])
        # test
        # fig, axs = plt.subplots(1, 2, figsize=(10, 10), sharey=True)
        # axs[0].plot(t_interp[0, 32, 0, 15:], p_ref[15:], '.-', label='interp')
        # axs[0].plot(t[0, 15:, 32, 0], p[0, 15:, 32, 0], '.-', label='raw')
        # axs[1].plot(qv_interp[0, 32, 0, 15:], p_ref[15:], label='interp')
        # axs[1].plot(qv[0, 15:, 32, 0], p[0, 15:, 32, 0], label='raw')
        # axs[1].invert_yaxis()
    
    tavg  /= count
    qvavg /= count
    # save
    np.save("tavg.npy", tavg)
    np.save("qvavg.npy", qvavg)
    
# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
