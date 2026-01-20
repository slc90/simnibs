"""Automated testing of the examples

Copyright (c) 2019-2024 SimNIBS developers. Licensed under the GPL v3.
"""

import glob
import os
import shutil
import stat
import subprocess
import sys

import pytest

import simnibs
from simnibs.utils.file_finder import path2bin

EXAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def replace_gmsh():
    fn_gmsh = path2bin("gmsh")
    fn_gmsh_tmp = path2bin("gmsh_tmp")
    # move
    if sys.platform == "win32":
        fn_gmsh += ".exe"
    shutil.move(fn_gmsh, fn_gmsh_tmp)
    # replace
    if sys.platform == "win32":
        # replace gmsh with an .exe that does not to anything
        shutil.copy(r"C:\Windows\System32\rundll32.exe", fn_gmsh)
    else:
        with open(fn_gmsh, "w") as f:
            f.write("#! /bin/bash -e\n")
            f.write('"echo" "$@"')
        os.chmod(
            fn_gmsh,
            os.stat(fn_gmsh).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
        )
    yield
    shutil.move(fn_gmsh_tmp, fn_gmsh)


class TestPythonErnie:
    def run_script(self, script_folder, script_name, clean=None):
        if clean is not None and os.path.exists(clean):
            shutil.rmtree(clean)
        fn = os.path.join(EXAMPLES_DIR, script_folder, script_name)
        print(fn)
        return subprocess.run([sys.executable, fn])

    def test_transform_coordinates(self, example_dataset):
        os.chdir(example_dataset)
        ret = self.run_script("utilities", "transform_coordinates.py")
        assert ret.returncode == 0

    def test_transform_coilpos(self, example_dataset):
        os.chdir(example_dataset)
        ret = self.run_script("utilities", "transform_coilpos.py")
        assert ret.returncode == 0

    def test_roi_definition(self, example_dataset):
        os.chdir(example_dataset)
        ret = self.run_script("utilities", "roi_definition.py")
        assert ret.returncode == 0

    def test_tDCS(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("simulations", "tDCS.py", "tdcs_simu")
        assert ret.returncode == 0

    def test_roi_analysis_surf(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        simnibs.utils.transformations.middle_gm_interpolation(
            "tdcs_simu/ernie_TDCS_1_scalar.msh",
            "m2m_ernie",
            "tdcs_simu/subject_overlays",
        )
        ret = self.run_script("analysis", "roi_analysis_surf.py")
        assert ret.returncode == 0

    def test_roi_analysis_mni(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("analysis", "roi_analysis_mni.py")
        assert ret.returncode == 0

    def test_TMS(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("simulations", "TMS.py", "tms_simu")
        assert ret.returncode == 0

    def test_TMS_MNI(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("simulations", "TMS_MNI.py", "tms_hand")
        assert ret.returncode == 0

    def test_TI(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("simulations", "TI.py", "TI")
        assert ret.returncode == 0

    def test_tDCS_ring(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("simulations", "tDCS_ring.py", "tdcs_ring")
        assert ret.returncode == 0

    def test_tDCS_advanced(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("simulations", "tDCS_advanced.py", "tdcs_advanced_simu")
        assert ret.returncode == 0

    def test_tDCS_Nx1(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("simulations", "tDCS_Nx1.py", "tdcs_Nx1")
        assert ret.returncode == 0

    def test_tACSchallenge(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("simulations", "tACSchallenge.py", "TACSchallenge")
        assert ret.returncode == 0

    def test_leadfield(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("optimization", "leadfield.py", "leadfield")
        assert ret.returncode == 0

    def test_tdcs_optimize(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("optimization", "tdcs_optimize.py")
        assert ret.returncode == 0

    def test_tdcs_optimize_multi_target(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("optimization", "tdcs_optimize_multi_target.py")
        assert ret.returncode == 0

    def test_tdcs_optimize_avoid(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("optimization", "tdcs_optimize_avoid.py")
        assert ret.returncode == 0

    def test_tdcs_optimize_mni(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("optimization", "tdcs_optimize_mni.py")
        assert ret.returncode == 0

    def test_tdcs_optimize_strength(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("optimization", "tdcs_optimize_strength.py")
        assert ret.returncode == 0

    def test_tdcs_optimize_distributed(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        shutil.copy(
            os.path.join(
                simnibs.SIMNIBSDIR,
                "_internal_resources",
                "testing_files",
                "ID03_MOTOR_ICA.nii.gz",
            ),
            example_dataset,
        )
        ret = self.run_script("optimization", "tdcs_optimize_distributed.py")
        assert ret.returncode == 0

    def test_tms_optimize_with_region(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("optimization", "tms_optimization_with_region.py")
        assert ret.returncode == 0

    def test_tms_optimize_ADM(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script(
            "optimization", "tms_optimization_adm.py", "tms_optimization_adm"
        )
        assert ret.returncode == 0

    def test_tms_flex_fig8coil_emag(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script(
            "tms_flex_optimization", "tms_flex_fig8coil_emag.py", "tms_optimization"
        )
        assert ret.returncode == 0

    def test_tms_flex_roundcoil_distance(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script(
            "tms_flex_optimization",
            "tms_flex_roundcoil_distance.py",
            "tms_optimization",
        )
        assert ret.returncode == 0

    def test_tms_flex_Brainsway_H1_distance(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script(
            "tms_flex_optimization",
            "tms_flex_Brainsway_H1_distance.py",
            "tms_optimization_H1",
        )
        assert ret.returncode == 0

    def test_tms_flex_MagVenture_MST_emag(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script(
            "tms_flex_optimization",
            "tms_flex_MagVenture_MST_emag.py",
            "tms_optimization_MSTemag",
        )
        assert ret.returncode == 0


class TestTESflexoptimize:
    def run_script(self, script_folder, script_name, clean=None):
        if clean is not None and os.path.exists(clean):
            shutil.rmtree(clean)
        fn = os.path.join(EXAMPLES_DIR, script_folder, script_name)
        print(fn)
        return subprocess.run([sys.executable, fn])

    def test_tes_flex_hdtes_focality(self, example_dataset):
        os.chdir(example_dataset)
        ret = self.run_script(
            "tes_flex_optimization",
            "tes_flex_4x1tes_focality.py",
            "tes_optimze_4x1tes_focality",
        )
        assert ret.returncode == 0

    def test_tes_flex_hdtes_intensity(self, example_dataset):
        os.chdir(example_dataset)
        ret = self.run_script(
            "tes_flex_optimization",
            "tes_flex_4x1tes_intensity.py",
            "tes_optimze_4x1tes_intensity",
        )
        assert ret.returncode == 0

    def test_tes_flex_ttf_intensity(self, example_dataset):
        os.chdir(example_dataset)
        ret = self.run_script(
            "tes_flex_optimization",
            "tes_flex_ttf_intensity.py",
            "tes_flex_ttf_intensity",
        )
        assert ret.returncode == 0

    def test_tes_flex_ti_intensity(self, example_dataset):
        os.chdir(example_dataset)
        ret = self.run_script(
            "tes_flex_optimization", "tes_flex_ti_intensity.py", "tes_flex_ti_intensity"
        )
        assert ret.returncode == 0

    def test_tes_flex_tes_Enormal_intensity(self, example_dataset):
        os.chdir(example_dataset)
        ret = self.run_script(
            "tes_flex_optimization",
            "tes_flex_tes_Enormal_intensity.py",
            "tes_flex_tes_Enormal_intensity",
        )
        assert ret.returncode == 0


class TestCoils:
    def run_script(self, script_folder, script_name, clean=None):
        if clean is not None and os.path.exists(clean):
            shutil.rmtree(clean)
        fn = os.path.join(EXAMPLES_DIR, script_folder, script_name)
        print(fn)
        return subprocess.run([sys.executable, fn])

    def test_create_deformable_figure_of_8_coil(self, replace_gmsh):
        ret = self.run_script(
            "coils", "create_deformable_figure_of_8_coil.py", "coil_example"
        )
        shutil.rmtree("coil_example")
        assert ret.returncode == 0

    def test_create_simple_circular_coil(self, replace_gmsh):
        ret = self.run_script("coils", "create_simple_circular_coil.py", "coil_example")
        shutil.rmtree("coil_example")
        assert ret.returncode == 0

    def test_create_simple_figure_of_8_coil(self, replace_gmsh):
        ret = self.run_script(
            "coils", "create_simple_figure_of_8_coil.py", "coil_example"
        )
        shutil.rmtree("coil_example")
        assert ret.returncode == 0

    def test_create_two_stimulator_coil(self, replace_gmsh):
        ret = self.run_script("coils", "create_two_stimulator_coil.py", "coil_example")
        shutil.rmtree("coil_example")
        assert ret.returncode == 0

    def test_tms_multi_stimulator_simulation(self, example_dataset, replace_gmsh):
        os.chdir(example_dataset)
        ret = self.run_script("coils", "tms_multi_stimulator_simulation.py", "tms_simu")
        assert ret.returncode == 0
