import os
import time

import simnibs
from simnibs.mesh_tools import mesh_io
from simnibs.optimization.tdcs_optimization import TDCSavoid, TDCStarget


def main():
    # Initialize structure
    opt = simnibs.opt_struct.TDCSoptimize()
    opt.leadfield_hdf = "leadfield/ernie_leadfield_EEG10-10_Cutini_2011.hdf5"
    opt.name = "TI_leadfield_optimize/test"
    opt.max_total_current = 0.005
    opt.max_individual_current = 0.003
    opt.max_active_electrodes = 3
    target1 = TDCStarget()
    target1.positions = [-50.7, 5.1, 55.5]
    target1.directions = None
    target1.indexes = None
    target1.intensity = 0.2
    target1.max_angle = None
    # 0相当于靶点，非0相当于核团，单位mm
    target1.radius = 2
    # target区域内哪些tissues会在优化过程中被使用
    target1.tissues = None
    target2 = TDCStarget()
    target2.positions = [-30.3, 5.4, 71.6]
    target2.directions = None
    target2.indexes = None
    # 数值填的很大就是focality,应该是改变了目标函数
    target2.intensity = 100
    target2.max_angle = None
    target2.radius = 0
    target2.tissues = None
    # 尝试了多目标，但导致了约束问题误解
    opt.target = [target1]
    avoid = TDCSavoid()
    avoid.positions = [-39.7, 7.5, 65.6]
    avoid.weight = 1500
    avoid.indexes = None
    avoid.radius = 5
    avoid.tissues = None
    opt.avoid = [avoid]
    # 用时 81.88 seconds
    # cpu即使填了8也占不满
    # 而且这里强制打开gmsh看结果
    simnibs.run_simnibs(opt, cpus=8)


if __name__ == "__main__":
    t1 = time.time()
    main()
    t2 = time.time()
    print(f"TI leadfield computation time: {t2 - t1:.2f} seconds")
