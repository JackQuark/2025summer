# _summary_
# author: Quark
# ==================================================
import sys
import os
import numpy     as np
import matplotlib.pyplot  as plt

sys.path.append("/home/Quark/2025summer/tools")
from dycore_reader import Dataset
# ==================================================
# calc. the mean state of atm from 1000 ~ 2000d data

def save_mean_state(ds: Dataset):
    f = ds.open_HDF5(1000)
    meanT_tot = np.zeros((20, 64))
    meanqv_tot = np.zeros((20, 64))
    count = 0
    for iday in range(1000, 2000, 25):
        f  = ds.open_HDF5(iday)
        T  = f['grid_t_c_xyzt'][:]
        qv = f['grid_tracers_c_xyzt'][:]
        meanT_tot += np.mean(T, axis=(0, 3))
        meanqv_tot += np.mean(qv, axis=(0, 3))
        count += 1
        f.close()
    
    meanT_tot /= count
    meanqv_tot /= count
    
    np.save("meanT.npy", meanT_tot)
    np.save("meanqv.npy", meanqv_tot)
    
    
def test():
    datadir = "/data92/Quark/ctrl_2000d/HSt42_20"
    ds = Dataset(datadir)
    f = ds.open_HDF5(1000)

    meanp_tot = np.zeros((20, 64))
    count = 0
    for iday in range(1000, 2000, 25):
        f = ds.open_HDF5(iday)
        p = f['grid_p_full_xyzt'][:]
        tmp = np.mean(p, axis=(0, 3))
        
        meanp_tot += tmp
        
        print(tmp[0])
        
        count += 1
        f.close()
    
    meanp_tot /= count
    # np.save("meanp.npy", meanp_tot)

def interp_to_ref(x, xp, fp):
    # data points (xp, fp), evaluated at x    
    def calc_right(x, xp, fp):
        assert x[-1] > xp[-1]
        dx = x[-1] - xp[-1]
        s = (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
        return fp[-1] + dx * s
    
    return np.interp(x, xp, fp, right=calc_right(x, xp, fp))

def main():
    datadir = "/data92/Quark/ctrl_2000d/HSt42_20"
    ds = Dataset(datadir)
    p_ref = np.linspace(2000, 100000, 20)

    for iday in range(1000, 2000, 25):
        f = ds.open_HDF5(iday)
        # (time, lev, lat, lon)
        # (200, 20, 64, 128)
        p = f['grid_p_full_xyzt'][:]
        t = f['grid_t_c_xyzt'][:]
        qv = f['grid_tracers_c_xyzt'][:]
        
        res = (
            interp_to_ref(p_ref, p[0, :, 32, 0], t[0, :, 32, 0]),
            interp_to_ref(p_ref, p[0, :, 32, 0], qv[0, :, 32, 0])
        )
        
        # fig, axs = plt.subplots(1, 2, figsize=(10, 10), sharey=True)
        # axs[0].plot(res[0][15:], p_ref[15:], '.-', label='interp')
        # axs[0].plot(t[0, 15:, 32, 0], p[0, 15:, 32, 0], '.-', label='raw')
        # axs[1].plot(res[1][15:], p_ref[15:], label='interp')
        # axs[1].invert_yaxis()
                            

    
# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
