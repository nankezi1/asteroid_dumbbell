"""Plot the data from explore_main

Extended description of the module

Notes
-----
    This is an example of an indented section. It's like any other section,
    but the body is indented to help it stand out from surrounding text.

If a section is indented, then a section break is created by
resuming unindented text.

Attributes
----------
module_level_variable1 : int
    Descrption of the variable

Author
------
Shankar Kulumani		GWU		skulumani@gwu.edu
"""
import pdb
import numpy as np
import os
import h5py
import argparse

from point_cloud import wavefront
from visualization import graphics
import utilities

def exploration_generate_plots(data_path, img_path='/tmp/diss_explore', 
                               magnification=1, step=10):
    """Given a HDF5 file generated by explore (C++) this will generate some plots
    """

    if not os.path.exists(img_path):
        os.makedirs(img_path)

    with h5py.File(data_path, 'r') as hf:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate plots from explore",
                                     formatter_class=argparse.RawTextHelpFormatter)

    # add options
    parser.add_argument("hdf5_file", help="The data file to read", type=str)
    parser.add_argument("img_path", help="The path to save images", type=str)

    args = parser.parse_args()

    exploration_generate_plots(args.hdf5_file, args.img_path);



