"""Example of a SimNIBS tDCS leadfield in Python
Run with:

simnibs_python leadfield.py

Copyright (c) 2019 SimNIBS developers. Licensed under the GPL v3.

place script in the main folder of the example dataset
"""

import time

from simnibs import run_simnibs, sim_struct
from simnibs.simulation.sim_struct import ELECTRODE
from simnibs.utils.mesh_element_properties import ElementTags


def main():
    tdcs_lf = sim_struct.TDCSLEADFIELD()
    tdcs_lf.fnamehead = "data/m2m_ernie/ernie.msh"
    tdcs_lf.pathfem = "leadfield"
    tdcs_lf.field = "E"
    tdcs_lf.eeg_cap = "data/m2m_ernie/eeg_positions/EEG10-10_Cutini_2011.csv"
    # 这三的关系不明白
    tdcs_lf.interpolation = None
    tdcs_lf.tissues = [ElementTags.WM, ElementTags.GM]
    tdcs_lf.interpolation_tissue = []
    # EEG10-10_Cutini_2011.csv中的电极都用这个属性
    tdcs_lf.electrode = ELECTRODE()
    tdcs_lf.electrode.shape = "ellipse"
    tdcs_lf.electrode.dimensions = [10, 10]
    tdcs_lf.electrode.thickness = [4]
    tdcs_lf.anisotropy_type = "scalar"
    tdcs_lf.aniso_maxratio = 10
    tdcs_lf.aniso_maxcond = 2
    tdcs_lf.fname_tensor = "data/m2m_ernie/DTI_coregT1_tensor.nii.gz"
    tdcs_lf.solver_options = "pardiso"
    # Windows下因为multiprocessing导致的错误(leadfield没法pickle序列化)，只能用一个cpu
    # 总共用时 1121.58 seconds
    run_simnibs(tdcs_lf, cpus=1)


if __name__ == "__main__":
    t1 = time.time()
    main()
    t2 = time.time()
    print(f"Forward computation time: {t2 - t1:.2f} seconds")
