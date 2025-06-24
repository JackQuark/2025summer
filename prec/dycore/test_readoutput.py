# _summary_
# author: Quark
# ==================================================
import os
import re
import numpy as np
import h5py

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
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
                        
        # u  = f["grid_u_c_xyzt"][:]     # Zonal wind
        # v  = f["grid_v_c_xyzt"][:]     # Meridional wind
        t  = f["grid_t_c_xyzt"][:]     # Temperature
        p  = f["grid_p_full_xyzt"][:]  # 3D pressure        
        qv = f["grid_tracers_c_xyzt"][:] # specific humidity
        # ps = f["grid_ps_c_xyzt"][:]    # Surface pressure
        # w  = f["grid_w_full_xyzt"][:]  # Vertical velocity
        # phi = f["grid_geopots_xyzt"][:]  # Geopotential
        
    return t, p, qv
        
    # return u, v, t, p, ps, w, phi

def quickview2D(grid):
    """"""
    fig, ax = plt.subplots(figsize=(8, 6))

    nx = grid.shape[1]
    ny = grid.shape[0]
    lon = np.linspace(0, 360, nx)
    lat = np.linspace(90, -90, ny)

    c = ax.pcolormesh(lon, lat, grid, cmap='RdBu_r', shading='auto')
    cbar = fig.colorbar(c, ax=ax)
    return fig, ax, c

class Dataset(object):
    def __init__(self, exp_dirpath):
        if not os.path.exists(exp_dirpath):
            raise ValueError(f"Experiment directory '{exp_dirpath}' not found.")

        self.expname = os.path.basename(exp_dirpath)
        self.day_interval = int(open(os.path.join(exp_dirpath, "day_interval.txt")).read())
        
        fnames = [f for f in os.listdir(exp_dirpath) if f.endswith(".dat")]
        pattern = re.compile(r"startfrom_(\d+)day")
        
        # mapping: start_day -> full_path
        self.start_day_to_path = {}
        for fname in fnames:
            match = pattern.search(fname)
            if match:
                start_day = int(match.group(1))
                self.start_day_to_path[start_day] = os.path.join(exp_dirpath, fname)
        
        sorted_start_day = sorted(self.start_day_to_path.keys())
        self.valid_days = np.arange(sorted_start_day[0], sorted_start_day[-1]+1, self.day_interval)
        
    def find_start_day(self, day):
        i = np.searchsorted(self.valid_days, day, side='right') - 1
        return self.valid_days[i]

    def open_HDF5(self, day):
        """
        Open the corresponding HDF5 file that contains the given day.
        """
        if hasattr(self, "current_file"):
            self.current_file.close()
            
        start_day = self.find_start_day(day)
        filepath = self.start_day_to_path[start_day]
        
        self.current_file = h5py.File(filepath, "r")
        return self.current_file

    def show_current_file(self):
        if not hasattr(self, "current_file"): print("No file opened yet.")
        else: print(f"Current file: {self.current_file.filename}")



def test():
    ds = Dataset("/data92/Quark/HSt42_20")
    
    
    return 

def main():
    ds = Dataset("/data92/Quark/HSt42_20")
    ds.open_HDF5(990)
    fig, ax = plt.subplots(figsize=(8, 6))
    title   = ax.set_title("")

    qv_cache = ds.current_file["grid_tracers_c_xyzt"][:, 0, ...]
    ny, nx = qv_cache.shape[1:]
    
    lat = np.linspace(90, -90, ny)
    lon = np.linspace(0, 360, nx)
    
    c = ax.pcolormesh(lon, lat, qv_cache[0, ...], cmap='jet', 
                      shading='auto', vmin=0, vmax=6e-7)
    cbar = fig.colorbar(c, ax=ax)
    
    ax.set_yticks(np.arange(-90, 91, 30))
    ax.set_xticks(np.arange(0, 361, 45))
    
    iday = 0
    def update_frame(i):
        nonlocal iday, qv_cache
        print(f"tstep: {i}", end='\r')

        if i % 100 == 0:
            iday = (i // 100) * 25
            ds.open_HDF5(iday)
            ds.show_current_file()
            qv_cache = ds.current_file["grid_tracers_c_xyzt"][:, 0, ...]

        _qv = qv_cache[i % 100, ...]
        c.set_array(_qv.ravel())
        
        title.set_text(f"{i//4}day")
        return c, title
        
    anim = FuncAnimation(fig, update_frame, frames=range(0, 4000), blit=False)
    writer = FFMpegWriter(fps=50, metadata=dict(artist='Me'), bitrate=1800)
    anim.save("output.mp4", dpi=100, writer=writer)
        
# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    # test()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
