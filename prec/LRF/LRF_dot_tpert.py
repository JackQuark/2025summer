# _summary_
# author: Quark
# ==================================================
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from metpy.calc import moist_lapse
from metpy.units import units
import climlab
# ==================================================
# zonal mean temp., qv, pressure (20, 64)
zonal_T  = np.load("/home/Quark/2025summer/prec/dycore/meanT.npy")
zonal_qv = np.load("/home/Quark/2025summer/prec/dycore/meanqv.npy")
zonal_p  = np.load("/home/Quark/2025summer/prec/dycore/meanp.npy") / 100.

def main():
    grid_data_shape = (20, 64, 128)    
    total_LRF = np.load("/home/Quark/2025summer/prec/LRF/LRF_Tpert.npy")

    t_pert = np.random.normal(0, 0.1, size=grid_data_shape)

    t_pert_T = t_pert.transpose(1, 0, 2) # (64, 20, 128)
    heating_T = np.matmul(total_LRF, t_pert_T)
    heating_rate = heating_T.transpose(1, 0, 2)
    print(heating_rate.shape)

    # heating_rate_test = np.zeros((20, 64, 128))
    # for i in range(64):
    #     heating_rate_test[:, i, :] = total_LRF[i, :, :] @ t_pert[:, i, :]
    # print(np.sum(np.where(heating_rate_test!= heating_rate, 1, 0)))

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
