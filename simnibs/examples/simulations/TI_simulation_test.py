import os
import time
from copy import deepcopy

import numpy as np

from simnibs import run_simnibs, sim_struct
from simnibs.mesh_tools import mesh_io
from simnibs.simulation.sim_struct import ELECTRODE, TDCSLIST
from simnibs.utils import TI_utils as TI
from simnibs.utils.mesh_element_properties import ElementTags


def create_electrode(
    centre,
    pos_ydir,
    shape,
    dimensions,
    thickness,
    channelnr,
    dimensions_sponge,
    vertices,
    definition,
    holes,
    plug,
):
    electrode = ELECTRODE()
    electrode.channelnr = channelnr
    electrode.centre = centre
    electrode.pos_ydir = pos_ydir
    electrode.shape = shape
    electrode.dimensions = dimensions
    electrode.thickness = thickness
    electrode.dimensions_sponge = dimensions_sponge
    electrode.vertices = vertices
    electrode.definition = definition
    electrode.holes = holes
    electrode.plug = plug
    return electrode


def set_conductivity(
    tdcs_list: TDCSLIST, anisotropy_type, aniso_maxratio, aniso_maxcond
):
    tdcs_list.anisotropy_type = anisotropy_type
    tdcs_list.aniso_maxratio = aniso_maxratio
    tdcs_list.aniso_maxcond = aniso_maxcond


def forward_compute():
    # 正向计算，会产生msh文件
    session = sim_struct.SESSION()
    session.subpath = "data/m2m_ernie"
    session.fnamehead = "data/m2m_ernie/ernie.msh"
    # 输出到的文件夹
    session.pathfem = "ti_simulation_test"
    session.fields = "eE"
    session.open_in_gmsh = False
    session.map_to_surf = False
    session.map_to_fsavg = False
    session.map_to_vol = False
    session.map_to_MNI = False
    # FEM算出来的电场插值到nifti的体素时需要在哪些组织上才插值
    # 上面的map_to_vol设置为True才有意义
    # 默认的'2'是灰质
    session.tissues_in_niftis = "all"  # pyright: ignore[reportAttributeAccessIssue]
    # 各向异性时的导电率文件
    session.fname_tensor = "data/m2m_ernie/DTI_coregT1_tensor.nii.gz"
    # 电极位置
    session.eeg_cap = "data/m2m_ernie/eeg_positions/EEG10-10_Cutini_2011.csv"
    # 增加simulation，添加多个不同的TDCSLIST，就是执行不同条件下的simulation
    tdcs_list1 = TDCSLIST()
    # 添加电极，这一组里有3个电极
    tdcs_list1.currents = [0.001, 0.002, -0.003]
    electrode_1 = create_electrode(
        centre="AF4",
        pos_ydir="F6",
        shape="rect",
        dimensions=[50, 70],
        thickness=[5],
        channelnr=1,
        dimensions_sponge=None,
        vertices=[],
        definition="plane",
        holes=[],
        plug=[],
    )
    tdcs_list1.add_electrode(electrode_1)
    electrode_2 = create_electrode(
        centre="Fp1",
        pos_ydir="Fp2",
        shape="ellipse",
        dimensions=[50, 70],
        thickness=[5, 2],
        channelnr=2,
        dimensions_sponge=None,
        vertices=[],
        definition="plane",
        holes=[],
        plug=[],
    )
    tdcs_list1.add_electrode(electrode_2)
    electrode_3 = create_electrode(
        centre="PO8",
        pos_ydir="PO7",
        shape="ellipse",
        dimensions=[40, 40],
        thickness=[4, 2, 4],
        channelnr=3,
        dimensions_sponge=[100, 100],
        vertices=[],
        definition="plane",
        holes=[],
        plug=[],
    )
    tdcs_list1.add_electrode(electrode_3)
    # 设置导电率
    set_conductivity(
        tdcs_list=tdcs_list1,
        anisotropy_type="scalar",
        aniso_maxratio=10,
        aniso_maxcond=2,
    )
    # 设置求解器
    # Parallel Direct Sparse Solver
    # 使用 Intel MKL 可能有商业问题？
    tdcs_list1.solver_options = "pardiso"  # pyright: ignore[reportAttributeAccessIssue]
    tdcs_list2 = TDCSLIST()
    tdcs_list2.currents = [0.001, -0.001]
    electrode_4 = create_electrode(
        centre="CPz",
        pos_ydir="CP1",
        shape="ellipse",
        dimensions=[40, 40],
        thickness=[5, 2],
        channelnr=1,
        dimensions_sponge=None,
        vertices=[],
        definition="plane",
        holes=[],
        plug=[],
    )
    tdcs_list2.add_electrode(electrode_4)
    electrode_5 = create_electrode(
        centre="PO8",
        pos_ydir="PO7",
        shape="rect",
        dimensions=[40, 60],
        thickness=[5, 2, 3],
        channelnr=2,
        dimensions_sponge=[80, 80],
        vertices=[],
        definition="plane",
        holes=[],
        plug=[],
    )
    tdcs_list2.add_electrode(electrode_5)
    set_conductivity(
        tdcs_list=tdcs_list2,
        anisotropy_type="dir",
        aniso_maxratio=8,
        aniso_maxcond=1.5,
    )
    # 使用 PETSc
    # Portable, Extensible Toolkit for Scientific Computation
    # 这玩意在windows上很难编译，还好SimNIBS自己打包了一个wheel
    tdcs_list2.solver_options = "hypre"  # pyright: ignore[reportAttributeAccessIssue]
    # 两个一起跑用时 870.42 seconds
    # 单独跑这个 481.61 seconds
    session.add_tdcslist(tdcs_list1)
    # 单独跑这个 466.02 seconds
    session.add_tdcslist(tdcs_list2)
    # 设置为了8也没看到任务管理器中CPU占用增加
    run_simnibs(session, cpus=8)


def post_process(output_folder: str):
    # 后处理
    # 得到leadfield
    m1 = mesh_io.read_msh(os.path.join(output_folder, "ernie_TDCS_1_scalar.msh"))
    m2 = mesh_io.read_msh(os.path.join(output_folder, "ernie_TDCS_2_dir.msh"))
    # remove all tetrahedra and triangles belonging to the electrodes so that
    # the two meshes have same number of elements
    tags_keep = np.hstack(
        (
            np.arange(ElementTags.TH_START, ElementTags.SALINE_START - 1),
            np.arange(
                ElementTags.TH_SURFACE_START, ElementTags.SALINE_TH_SURFACE_START - 1
            ),
        )
    )
    m1 = m1.crop_mesh(tags=tags_keep)
    m2 = m2.crop_mesh(tags=tags_keep)
    # calculate the maximal amplitude of the TI envelope
    ef1 = m1.field["E"]
    ef2 = m2.field["E"]
    TImax = TI.get_maxTI(ef1.value, ef2.value)
    # make a new mesh for visualization of the field strengths
    # and the amplitude of the TI envelope
    mout = deepcopy(m1)
    mout.elmdata = []
    mout.add_element_field(ef1.norm(), "magnE - pair 1")
    mout.add_element_field(ef2.norm(), "magnE - pair 2")
    mout.add_element_field(TImax, "TImax")
    mesh_io.write_msh(mout, os.path.join(output_folder, "TI.msh"))
    v = mout.view(
        visible_tags=[1002, 1006],
        visible_fields="TImax",
    )
    v.write_opt(os.path.join(output_folder, "TI.msh"))


if __name__ == "__main__":
    # t1 = time.time()
    # forward_compute()
    # t2 = time.time()
    # print(f"Forward computation time: {t2 - t1:.2f} seconds")
    post_process("ti_simulation_test")
