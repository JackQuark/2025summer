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
    
    
    def __str__(self):
        msg = (
            f"Dataset: {self.expname}\n"
            f"Day interval: {self.day_interval}\n"
            f"Valid days: {self.valid_days}\n"
        )
        return msg
        
# ==================================================

def main():
    datadir = "/data92/Quark/ctrl_2000d/HSt42_20"
    ds = Dataset(datadir)
    f = ds.open_HDF5(1000)
    p = f['grid_p_full_xyzt'][:]
    
    print(np.mean(p, axis=(0, 3)))
    pass

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
