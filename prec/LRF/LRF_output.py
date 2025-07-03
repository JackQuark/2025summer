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

def LRF_calc_qv(p, t, qv, t_surf=288.):
    nlev = len(p)
    qvs  = climlab.utils.thermo.qsat(t, p)
    
    state = climlab.column_state(lev=p, water_depth=1.0)
    state['Tatm'][:] = t
    state['Ts'][:] = t_surf
    
    rad_base = climlab.radiation.RRTMG(
        name='Rad_base',
        state=state,
        specific_humidity=qvs,
        albedo=0.3
        )

    rad_base.compute_diagnostics()
    LW_ref = rad_base.diagnostics['TdotLW'].copy()
    SW_ref = rad_base.diagnostics['TdotSW'].copy()

    kernel_LW = np.zeros((nlev, nlev))
    kernel_SW = np.zeros((nlev, nlev))
      
    for k in range(nlev):
        # qv perturbation at k lev (-20%RH)
        tmp = qvs.copy()
        deltaqv = qvs[k] * -0.2
        tmp[k] += deltaqv

        # Fresh radiation model per perturbation
        rad_pert = climlab.radiation.RRTMG(name=f'Rad_pert_{k}',
                                        state=state,
                                        specific_humidity=tmp,
                                        albedo=0.3)
        rad_pert.compute_diagnostics()
        LW_pert = rad_pert.diagnostics['TdotLW'].copy()
        SW_pert = rad_pert.diagnostics['TdotSW'].copy()

        # Compute kernel column (response at all levels to impulse at level k)
        kernel_LW[:, k] = (LW_pert - LW_ref) # / deltaqv
        kernel_SW[:, k] = (SW_pert - SW_ref) # / deltaqv
    
    fig, axs = plt.subplots(1, 2, figsize=(10, 5), sharex=True, sharey=True)
    cs1 = axs[0].pcolormesh(p, p, (kernel_LW), cmap='RdBu_r',
                            vmin=-0.5, vmax=0.5)
    cs2 = axs[1].pcolormesh(p, p, (kernel_SW), cmap='RdBu_r',
                            vmin=-0.5, vmax=0.5)
    cbar = fig.colorbar(cs1, ax=axs)
    for ax in axs:
        ax.set_aspect('equal')
    del ax
    axs[0].set_xlim([1000, 10])
    axs[0].set_ylim([1000, 10])
    axs[0].set_xlabel('Perturbation level [hPa]')
    axs[0].set_ylabel('Response level [hPa]')
    axs[0].set_title('R_LW from qv [K/day per -20%RH]')
    axs[1].set_title('R_SW from qv [K/day per -20%RH]')
    
    return kernel_LW, kernel_SW

def LRF_calc_T(p, t, qv, t_surf=288., ofname='LRF_kernel.png'):
    nlev = len(p)
    qvs  = climlab.utils.thermo.qsat(t, p)
    
    state = climlab.column_state(lev=p, water_depth=1.0)
    state['Tatm'][:] = t
    state['Ts'][:] = t_surf
    print(state)
    
    rad_base = climlab.radiation.RRTMG(name='Rad_base',
                                    state=state,
                                    specific_humidity=qvs,
                                    albedo=0.3)

    rad_base.compute_diagnostics()
    LW_ref = rad_base.diagnostics['TdotLW'].copy()
    SW_ref = rad_base.diagnostics['TdotSW'].copy()

    kernel_LW = np.zeros((nlev, nlev))
    kernel_SW = np.zeros((nlev, nlev))
    
    delta_T = 1. # [K]
    state_pert = climlab.column_state(lev=p, water_depth=1.0)
    state_pert['Tatm'][:] = t
    state_pert['Ts'][:]   = t_surf

    for k in range(nlev):
        # Temp perturbation at k lev
        tmp = t.copy()
        tmp[k] += delta_T
        state_pert['Tatm'][:] = tmp

        # Fresh radiation model per perturbation
        rad_pert = climlab.radiation.RRTMG(name=f'Rad_pert_{k}',
                                        state=state_pert,
                                        specific_humidity=qvs,
                                        albedo=0.3)
        rad_pert.compute_diagnostics()
        LW_pert = rad_pert.diagnostics['TdotLW'].copy()
        SW_pert = rad_pert.diagnostics['TdotSW'].copy()

        # Compute kernel column (response at all levels to impulse at level k)
        kernel_LW[:, k] = (LW_pert - LW_ref) / delta_T
        kernel_SW[:, k] = (SW_pert - SW_ref) / delta_T

    fig, axs = plt.subplots(1, 2, figsize=(10, 5), sharex=True, sharey=True)
    cs1 = axs[0].pcolormesh(p, p, (kernel_LW), cmap='RdBu_r',
                            vmin=-0.5, vmax=0.5)
    cs2 = axs[1].pcolormesh(p, p, (kernel_SW), cmap='RdBu_r',
                            vmin=-0.5, vmax=0.5)
    cbar = fig.colorbar(cs1, ax=axs)
    for ax in axs:
        ax.set_aspect('equal')
    del ax
    axs[0].set_xlim([1000, 10])
    axs[0].set_ylim([1000, 10])
    axs[0].set_xlabel('Perturbation level [hPa]')
    axs[0].set_ylabel('Response level [hPa]')
    axs[0].set_title('R_LW from T [K/day per K]')
    axs[1].set_title('R_SW from T [K/day per K]')
    
    return kernel_LW, kernel_SW
    # fig.savefig(ofname, dpi=150, bbox_inches='tight')

def main():
    total_LRF = np.zeros((64, 20, 20))
    nlat, nlon = (64, 128)
    dlat = 180.0 / nlat 
    lat_centers = -90 + dlat/2 + np.arange(nlat) * dlat
    
    
    for ilat in range(32, 64, 8):
        LW, SW =  LRF_calc_qv(
            zonal_p[:, ilat], 
            zonal_T[:, ilat], 
            zonal_qv[:, ilat]
            )
        total_LRF[ilat, ...] = LW + SW
        
        continue
        LW, SW =  LRF_calc_T(
            zonal_p[:, ilat], 
            zonal_T[:, ilat], 
            zonal_qv[:, ilat],
            ofname=f'./figs/LRF_kernel_{ilat}.png'
            )        
        total_LRF[ilat, ...] = LW + SW
    
    # total_LRF[:32, ...] = np.flip(total_LRF[32:, ...], axis=0)
    # np.save('/home/Quark/2025summer/prec/LRF/LRF_Tpert.npy', total_LRF)

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
