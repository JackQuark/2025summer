# _summary_
# author: Quark
# ==================================================
import sys
import os
import numpy     as np
import matplotlib.pyplot  as plt
# ==================================================

def main():
    pass

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
