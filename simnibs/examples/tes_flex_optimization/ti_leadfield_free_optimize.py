"""
Example to run TESoptimize for Temporal Interference (TI) to optimize the
focality in the ROI vs non-ROI

Copyright (c) 2024 SimNIBS developers. Licensed under the GPL v3.
"""

import time

import numpy as np

from simnibs import opt_struct
from simnibs.optimization.tes_flex_optimization.electrode_layout import (
    CircularArray,
    ElectrodeArrayPair,
)
from simnibs.utils.region_of_interest import RegionOfInterest


def custom_goal_function(e_field):
    """
    e_field: List[List[np.ndarray]]
    shape: [n_channel_stim][n_roi]
    """
    # 我们只考虑第一个通道和两个 ROI 举例
    # ROI1 = e_field[0][0], ROI2 = e_field[0][1]

    roi1_mean = np.mean(e_field[0][0])
    roi2_max = np.max(e_field[0][1])

    # 我们希望 roi1_mean 大，roi2_max 小
    # 返回一个标量，SimNIBS 会尝试最大化它
    score = roi1_mean - roi2_max
    return score


def main():
    opt = opt_struct.TesFlexOptimization()
    opt.subpath = "data/m2m_ernie"
    opt.output_folder = "ti_leadfield_free_optimize_3"
    # optimize the focality of "max_TI" in the ROI ("max_TI" defined by e_postproc)
    # 这里可以自定义优化目标
    opt.goal = "focality"
    # opt.goal = custom_goal_function
    # define threshold(s) of the electric field in V/m in the non-ROI and the ROI:
    # if one threshold is defined, it is the goal that the e-field in the non-ROI is lower than this value and higher than this value in the ROI
    # if two thresholds are defined, the first one is the threshold of the non-ROI and the second one is for the ROI
    opt.threshold = [
        0.1,
        0.2,
    ]
    # postprocessing of e-fields
    # "max_TI": maximal envelope of TI field magnitude
    # "dir_TI": directional sensitive maximum envelope for temporal interference fields (requires surface ROIS)
    opt.e_postproc = "max_TI"
    opt.min_electrode_distance = 7.0
    opt.constrain_electrode_locations = False
    # 电极之间分散一些
    opt.overlap_factor = 0.8
    # Pair of TES electrode arrays (here: 1 electrode per array)
    # TI只能是固定两个电极组,多了也是用前2个,但这样优化过程就是错的
    electrode_layout: ElectrodeArrayPair = opt.add_electrode_layout(
        "ElectrodeArrayPair"
    )
    electrode_layout.radius = [12]
    electrode_layout.current = [0.002, -0.002]
    electrode_layout.current_estimator_method = "gpc"
    electrode_layout: ElectrodeArrayPair = opt.add_electrode_layout(
        "ElectrodeArrayPair"
    )
    electrode_layout.radius = [10]
    electrode_layout.current = [0.002, -0.002]
    electrode_layout.current_estimator_method = "gpc"
    # 目标函数为focality或focality_inv时，必须是固定一个roi,一个non-roi
    # 自定义目标函数时应该可以多个roi,和函数要对应,此时opt.threshold也无用了
    # 先加入的是roi,后加入的是non-roi
    roi: RegionOfInterest = opt.add_roi()
    # define ROI on central GM surfaces
    roi.method = "surface"
    roi.surface_type = "central"
    roi.roi_sphere_center_space = "subject"
    # center of spherical ROI in subject space (in mm)
    roi.roi_sphere_center = [
        -41.0,
        -13.0,
        66.0,
    ]
    # radius of spherical ROI (in mm)
    roi.roi_sphere_radius = 20
    # uncomment for visual control of ROI:
    # roi.subpath = opt.subpath
    # roi.write_visualization('','roi.msh')
    # all of GM surface except a spherical region with 25 mm around roi center
    non_roi: RegionOfInterest = opt.add_roi()
    non_roi.method = "surface"
    non_roi.surface_type = "central"
    non_roi.roi_sphere_center_space = "subject"
    non_roi.roi_sphere_center = [-41.0, -13.0, 66.0]
    non_roi.roi_sphere_radius = 25
    # take difference between GM surface and the sphere region
    non_roi.roi_sphere_operator = ["difference"]
    # uncomment for visual control of non-ROI:
    # non_roi.subpath = opt.subpath
    # non_roi.write_visualization("", "non-roi.msh")
    # opt.optimizer = "differential_evolution"
    opt.optimizer = "direct"
    opt.polish = False
    opt.run_final_electrode_simulation = True
    opt.anisotropy_type = "scalar"
    opt.disable_SPR_for_volume_roi = True
    # 把优化得到的电极映射到10-10
    opt.map_to_net_electrodes = True
    opt.run_mapped_electrodes_simulation = True
    opt.net_electrode_file = "data/m2m_ernie/eeg_positions/EEG10-10_Cutini_2011.csv"
    # debug
    opt.detailed_results = True
    # 6624.82 seconds
    opt.run(cpus=8, save_mat=False)


if __name__ == "__main__":
    t1 = time.time()
    main()
    t2 = time.time()
    print(f"TI leadfield-free computation time: {t2 - t1:.2f} seconds")
