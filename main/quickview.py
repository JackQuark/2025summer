


# _summary_
# author: Quark
# ==================================================
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

import h5py

sys.path.append("/home/Quark/2025summer/tools")
from dycore_dataset import Dataset
from ufunc import *
# ==================================================
g = 9.80665 # m/s^2     
# ==================================================

def LRFrun_output():
    nλ, nθ = (128, 64)
    λc, θc = calc_center_λθ(nλ, nθ, 'deg')

    iday = 500

    datadir = "/data92/Quark/ctrl_2000d/HSt42_20"    
    ds = Dataset(datadir)
    f = ds.open_HDF5(iday)
    run_ctrl = {
        'qv': f['grid_tracers_c_xyzt'][:],
        'T': f['grid_t_c_xyzt'][:],
        'p_half': f['grid_p_half_xyzt'][:]
    }
    f.close()
    datadir = "/data92/Quark/LRF1_2000d/HSt42_20"
    ds = Dataset(datadir)
    f = ds.open_HDF5(iday)
    run_lrf: dict[str, np.ndarray] = {
        'qv': f['grid_tracers_c_xyzt'][:],
        'T': f['grid_t_c_xyzt'][:],
        'p_half': f['grid_p_half_xyzt'][:]
    }
    f.close()
    run_ctrl['dp'] = np.diff(run_ctrl['p_half'], axis=1)
    run_lrf['dp'] = np.diff(run_lrf['p_half'], axis=1)
    run_ctrl['CWV'] = np.sum(run_ctrl['qv'] * run_ctrl['dp'], axis=1) / g 
    run_lrf['CWV'] = np.sum(run_lrf['qv'] * run_lrf['dp'], axis=1) / g
    
    sel_var = 'CWV'
    maxima = np.max(np.hstack([run_ctrl[sel_var], run_lrf[sel_var]]))
    minima = np.min(np.hstack([run_ctrl[sel_var], run_lrf[sel_var]]))
    # norm = plt.Normalize(vmin=minima, vmax=maxima)
    norm = None
    print(maxima, minima)
    # return 
    fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True, sharey=True)
    c1 = axs[0].pcolormesh(λc, θc, run_ctrl[sel_var][0, :, :], cmap='jet', norm=norm)
    c2 = axs[1].pcolormesh(λc, θc, run_lrf[sel_var][0, :, :], cmap='jet', norm=norm)
    cbar = plt.colorbar(c1, ax=axs)
    axs[0].set_title('Control')
    axs[1].set_title('LRF')
    fig.suptitle('day 500 qv', fontsize=14, y=0.95)

def LRFrun_cwp():
    nλ, nθ = (128, 64)
    λc, θc = calc_center_λθ(nλ, nθ, 'deg')
    g = 9.81  # m/s^2
    
    datadir = "/data92/Quark/LRFws/HSt42_20_ws500d_gLRF"
    ds = Dataset(datadir)
    iday = 1000
    f = ds.open_HDF5(iday)
    qv_all = f['grid_tracers_c_xyzt'][:, :, :, :]     # shape: [ntime, nlev, nlat, nlon]
    p_half_all = f['grid_p_half_xyzt'][:, :, :, :]    # shape: [ntime, nlev+1, nlat, nlon]
    f.close()

    qv0 = qv_all[0, :, :, :]                          # [lev, lat, lon]
    p_half0 = p_half_all[0, :, :, :]                  # [lev+1, lat, lon]
    dp0 = np.diff(p_half0, axis=0)                    # [lev, lat, lon]
    CWV0 = np.sum(qv0 * dp0, axis=0) / g              # [lat, lon]

    fig, ax = plt.subplots(figsize=(6, 4), sharex=True, sharey=True)
    c1 = ax.pcolormesh(λc, θc, CWV0, cmap='jet', shading='auto')
    cbar = plt.colorbar(c1, ax=ax)
    title = fig.suptitle('', fontsize=14, y=0.95)

    ndays = 25
    nsteps = 100
    total_steps = 8000  # frames
    iday = 0

    def update_frame(i):
        nonlocal iday, qv_all, p_half_all

        print(f"tstep: {i}", end='\r')

        if i % nsteps == 0:
            iday = (i // nsteps) * ndays
            f = ds.open_HDF5(iday)
            ds.show_current_file()
            qv_all = f["grid_tracers_c_xyzt"][:]
            p_half_all = f["grid_p_half_xyzt"][:]
            f.close()

        ti = i % nsteps
        qv = qv_all[ti, :, :, :]
        p_half = p_half_all[ti, :, :, :]
        dp = np.diff(p_half, axis=0)
        CWV = np.sum(qv * dp, axis=0) / g

        c1.set_array(CWV.ravel())
        title.set_text(f"{i // 4} day")
        return c1, title

    anim = FuncAnimation(fig, update_frame, frames=range(0, total_steps), blit=False)
    writer = FFMpegWriter(fps=50)
    anim.save("outputLRFrun_CWV.mp4", dpi=100, writer=writer)

def main():
    t = np.array([])
    for i in range(500, 1500, 25):
        print(i)
        fpath = "/data92/Quark/LRFws/HSt42_20_ws500d_gLRF/data/RH80_L20_1500day_startfrom_{:d}day.dat".format(i)
        with h5py.File(fpath, 'r') as f:
            T = f['grid_t_c_xyzt'][...]
            t = np.append(t, np.mean(T[:, 19, :, :], axis=(1, 2)))

    plt.plot(t)
    plt.yticks(np.arange(np.min(t), np.max(t), .005))

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    # LRFrun_output()
    LRFrun_cwp()
    # main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
