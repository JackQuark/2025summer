# _summary_
# author: Quark
# ==================================================
import os
import re
import numpy as np
import h5py
# ==================================================
__all__ = ["Dataset"]
# ==================================================

class Dataset(object):
    def __init__(
        self, exp_dirpath: str,
        pattern: str = re.compile(r"startfrom_(\d+)day"),
        ):
        if not os.path.exists(exp_dirpath):
            raise ValueError(f"Experiment directory '{exp_dirpath}' not found.")

        self._exp_name = os.path.basename(exp_dirpath)
        self._L = int(open(os.path.join(exp_dirpath, "Latent_heat.txt")).read())
        self._day_interval = int(open(os.path.join(exp_dirpath, "day_interval.txt")).read())

        subdirs = [d for d in os.listdir(exp_dirpath) if os.path.isdir(os.path.join(exp_dirpath, d))]
        assert len(subdirs) == 1
        self.dat_dir = os.path.join(exp_dirpath, subdirs[0])
        dat_names = [f for f in os.listdir(self.dat_dir) if f.endswith(".dat")]
        
        # mapping: start_day -> full_path
        self.start_day_to_path = {}
        for fname in dat_names:
            match = pattern.search(fname)
            if match:
                start_day = int(match.group(1))
                self.start_day_to_path[start_day] = os.path.join(self.dat_dir, fname)
        
        self.valid_days = sorted(self.start_day_to_path.keys())
        self._get_basic_info()
        
    def _get_basic_info(self):
        f = self.open_HDF5(self.valid_days[0])
        self._nt, self._nlev, self._ny, self._nx = f['grid_p_full_xyzt'].shape
        self._time_interval = self.of_interval / self._nt * 86400
        f.close()
        pass
    
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
    
    @property
    def expname(self):
        return self._exp_name    
    @property
    def L(self):
        return self._L
    @property
    def of_interval(self):
        "interval of each output file [day]"
        return self._day_interval
    @property
    def time_interval(self) -> float:
        "interval of each time step [s]"
        return self._time_interval
    @property
    def space_shape(self) -> tuple[int, int, int]:
        return (self._nlev, self._ny, self._nx)
    
    def __str__(self):
        msg = (
            f"Dataset: {self.expname}\n"
            f"Day interval: {self.of_interval}"
            # f"Valid days: {self.valid_days}\n"
        )
        return msg
        
# ==================================================

def main():
    datadir = "/data92/Quark/ctrl_2000d"
    ds = Dataset(datadir)
    f = ds.open_HDF5(ds.valid_days[0])


# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
