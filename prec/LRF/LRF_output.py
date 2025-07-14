# _summary_
# author: Quark
# ==================================================
import sys
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
# ==================================================
# zonal mean temp., qv, pressure (20, 64)
ref_T  = np.load("/home/Quark/2025summer/prec/dycore/avg_t.npy") # K
ref_qv = np.load("/home/Quark/2025summer/prec/dycore/avg_qv.npy") # kg/kg
ref_p  = np.loadtxt("/home/Quark/2025summer/prec/dycore/mean_p_full.dat") / 100 # to hPa

def main():
    total_LRF = np.load("/home/Quark/2025summer/prec/LRF/LRF_qvpert.npy")    
    
    # with h5py.File("/home/Quark/2025summer/prec/LRF/LRF_output.dat", "r") as f:
    #     print(f.keys())
    #     for key in f.keys():
    #         data = f[key][:]
    #         print(key, data.shape)
        
    #     LRF_total = f["LRF_qv"][:]       
    # plt.pcolormesh(ref_p, ref_p, LRF_total[32, :, :], cmap='RdBu_r')
 
    total_LRF[:, 0:4, 0:4] = 0.
    # total_LRF = np.where(abs(total_LRF) > 10000., 0, total_LRF)
 
    with h5py.File("/home/Quark/2025summer/prec/LRF/LRF_output.dat", "w") as f:
        f.create_dataset("LRF_qv", data=total_LRF)
        f.create_dataset("ref_t", data=ref_T)
        f.create_dataset("ref_qv", data=ref_qv)
    
    c = plt.pcolormesh(ref_p, ref_p, total_LRF[32, :, :], cmap='RdBu_r')
    cbar = plt.colorbar(c)
    print(total_LRF.shape)
    
    nlat, nlon = (64, 128)
    
    dlat   = 180.0 / nlat 
    lat    = -90 + dlat/2 + np.arange(nlat) * dlat
    θc     = np.deg2rad(lat)
    
    # total_LRF.astype(np.float64).tofile("LRF_qv.dat")

        
# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
