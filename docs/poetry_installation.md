## 执行摘要

本指南提供了一种使用 **Poetry** 而非 Conda 的 SimNIBS 替代安装方法。虽然基于 Conda 的官方安装 (`environment_win.yml`) 自动处理所有系统依赖项，但基于 Poetry 的方法提供了：

### 主要优势
- **更好的 Python 依赖管理**：使用 Poetry 的锁文件和版本解析功能
- **对环境更强的控制**：无需 Conda 的庞大资源占用
- **直接的系统库集成**：适用于高级用户
- **与现有 Python 工作流的兼容性**：便于集成到 CI/CD 管道中

### 权衡
- **需要手动安装系统依赖项**：如 CGAL、FreeGLUT、MKL 等
- **更复杂的构建过程**：C++ 扩展的构建较为复杂
- **需要平台特定配置**：每个操作系统都需要单独配置

### 适用人群
- **熟悉系统库管理的高级 Python 开发者**
- **因组织限制无法使用 Conda 的用户**
- **将 SimNIBS 集成到大型 Python 项目中的开发者**
- **已建立 Poetry 的 CI/CD 环境**

### 快速决策指南
- **如果以下情况，请使用 Conda (environment_win.yml)**：您想要最简单、最可靠的安装
- **如果以下情况，请使用 Poetry (本指南)**：您需要 Poetry 的依赖管理功能或无法使用 Conda

## 目录
- [快速开始](#快速开始)
- [先决条件](#先决条件)
  - [1. 系统依赖项 (Windows)](#1-系统依赖项-windows)
  - [2. Python 要求](#2-python-要求)
- [安装步骤](#安装步骤)
- [第三方库功能说明](#第三方库功能说明)
- [平台特定说明](#平台特定说明)
- [故障排除](#故障排除)
- [使用 Poetry 进行开发](#使用-poetry-进行开发)
- [替代方案：混合方法](#替代方案-混合方法)
- [替代方案：包装脚本方法](#替代方案-包装脚本方法)
- [结论](#结论)
- [参考资料](#参考资料)

## 快速开始

对于希望快速安装的有经验用户：

1. **安装系统依赖项**（详见以下详细说明）：
   ```bash
   # 使用 vcpkg（推荐）
   vcpkg install cgal:x64-windows freeglut:x64-windows zlib:x64-windows tbb:x64-windows
   ```

2. **设置环境变量**：
   ```bash
   set CGAL_DIR=C:\path\to\cgal
   set TBB_ROOT=C:\path\to\tbb
   ```

3. **使用 Poetry 安装**：
   ```bash
   poetry install
   poetry run python setup.py build_ext --inplace
   ```

4. **安装特殊依赖项**：
   ```bash
   poetry run pip install https://github.com/simnibs/petsc4py/releases/download/v3.21.5/petsc4py-3.21.5-cp311-cp311-win_amd64.whl
   # 可选：安装 GUI 组件
   poetry install --with gui
   # 可选：安装 MUMPS 求解器（如果需要）
   poetry install --with mumps
   ```

本指南提供了使用 Poetry 而非 Conda 安装 SimNIBS 的说明。Poetry 管理 Python 依赖项，但 SimNIBS 还需要安装几个系统级库。

## 先决条件

### 1. 系统依赖项 (Windows)

SimNIBS 需要以下系统库。请在进行下一步之前安装它们：

#### 选项 A：使用 vcpkg（推荐用于开发者）
```bash
# 如果尚未安装 vcpkg，请先安装
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat

# 安装必需的库
.\vcpkg install cgal:x64-windows
.\vcpkg install freeglut:x64-windows
.\vcpkg install zlib:x64-windows
.\vcpkg install tbb:x64-windows
.\vcpkg install mpir:x64-windows  # GMP/MPFR 替代方案
.\vcpkg install eigen3:x64-windows
```

#### 选项 B：手动安装
- **CGAL**：从 https://github.com/CGAL/cgal/releases 下载
- **FreeGLUT**：从 http://freeglut.sourceforge.net/ 下载
- **MKL**：从 https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html 安装 Intel oneAPI Base Toolkit
- **TBB**：从 https://github.com/oneapi-src/oneTBB 下载
- **zlib**：从 https://zlib.net/ 下载
- **VS2015 Runtime**：从 Microsoft 官方源安装

### 2. Python 要求
- Python 3.11 或更高版本（推荐 3.11.10）
- 全局安装 Poetry：`pip install poetry` 或使用官方安装程序

## 安装步骤

### 步骤 1: 克隆代码库
```bash
git clone https://github.com/simnibs/simnibs.git
cd simnibs
```

### 步骤 2: 设置环境变量

设置以下环境变量以帮助构建系统找到依赖项：

```bash
# Windows (命令提示符)
set CGAL_DIR=C:\path\to\cgal
set BOOST_ROOT=C:\path\to\boost
set EIGEN3_INCLUDE_DIR=C:\path\to\eigen3
set TBB_ROOT=C:\path\to\tbb
set ZLIB_ROOT=C:\path\to\zlib

# Windows (PowerShell)
$env:CGAL_DIR = "C:\path\to\cgal"
$env:BOOST_ROOT = "C:\path\to\boost"
$env:EIGEN3_INCLUDE_DIR = "C:\path\to\eigen3"
$env:TBB_ROOT = "C:\path\to\tbb"
$env:ZLIB_ROOT = "C:\path\to\zlib"

# Linux/macOS
export CGAL_DIR=/path/to/cgal
export BOOST_ROOT=/path/to/boost
export EIGEN3_INCLUDE_DIR=/path/to/eigen3
export TBB_ROOT=/path/to/tbb
export ZLIB_ROOT=/path/to/zlib
```

### 步骤 3: 转换 pyproject.toml 为 Poetry 兼容格式

现有的 `pyproject.toml` 使用 setuptools。创建一个 Poetry 兼容的版本：

```bash
# 为 Poetry 创建新的 pyproject.toml
cp pyproject.toml pyproject.toml.backup
```

编辑 `pyproject.toml` 以包含 `[tool.poetry]` 部分：

```toml
[tool.poetry]
name = "simnibs"
version = "0.0.0"  # 将由 setuptools-scm 设置
description = "Simulation of Non-Invasive Brain Stimulation"
authors = ["SimNIBS developers <support@simnibs.org>"]
license = "GPL3"
readme = "README.md"
homepage = "http://simnibs.org"
repository = "https://github.com/simnibs/simnibs"
documentation = "https://simnibs.github.io/simnibs"
keywords = ["neuroscience", "brain-stimulation", "fem", "tms", "tdcs"]

[tool.poetry.dependencies]
python = ">=3.11,<3.12"
fmm3dpy = "1.0.0"
h5py = ">=3.11.0"
jsonschema = ">=4.23.0"
nibabel = ">=5.2.1"
numba = ">=0.60.0"
numpy = ">=1.26.4,<2.0.0"
petsc4py = ">=3.21.5"
pillow = ">=10.4.0"
pygpc = "0.4.1"
requests = ">=2.32.3"
samseg = "0.4a0"
scipy = ">=1.14.1"
matplotlib = ">=3.9.2"

# 平台特定依赖项
mkl = { version = ">=2024.2.1", markers = "sys_platform != 'darwin'" }
tbb = { version = ">=2021.13.0", markers = "sys_platform != 'darwin'" }

[tool.poetry.group.test.dependencies]
pytest = ">=8.3.3"
mock = ">=5.1.0"

[tool.poetry.group.mumps.dependencies]
python-mumps = ">=0.0.2"  # 可选：用于 MUMPS 求解器支持

[tool.poetry.scripts]
charm = "simnibs.cli.charm:main"
add_tissues_to_upsampled = "simnibs.cli.add_tissues_to_upsampled:main"
calc_B = "simnibs.cli.calc_B:main"
coil2nifti = "simnibs.cli.coil2nifti:main"
charm_tms = "simnibs.cli.charm_tms:main"
convert_3_to_4 = "simnibs.cli.convert_3_to_4:main"
download_coils = "simnibs.cli.download_coils:main"
eeg_positions = "simnibs.cli.eeg_positions:main"
expand_to_center_surround = "simnibs.cli.expand_to_center_surround:main"
get_eeg_positions = "simnibs.cli.get_eeg_positions:main"
get_fields_at_coordinates = "simnibs.cli.get_fields_at_coordinates:main"
maskmesh = "simnibs.cli.maskmesh:main"
meshmesh = "simnibs.cli.meshmesh:main"
mni2subject_coords = "simnibs.cli.mni2subject_coords:main"
mni2subject = "simnibs.cli.mni2subject:main"
msh2cortex = "simnibs.cli.msh2cortex:main"
msh2nii = "simnibs.cli.msh2nii:main"
nii2msh = "simnibs.cli.nii2msh:main"
postinstall_simnibs = "simnibs.cli.postinstall_simnibs:main"
prepare_eeg_forward = "simnibs.cli.prepare_eeg_forward:main"
prepare_eeg_montage = "simnibs.cli.prepare_eeg_montage:main"
prepare_tdcs_leadfield = "simnibs.cli.prepare_tdcs_leadfield:main"
register = "simnibs.cli.register:main"
simnibs = "simnibs.cli.run_simnibs:main"
simnibs_gui = "simnibs.cli.simnibs_gui:main"
subject2mni_coords = "simnibs.cli.subject2mni_coords:main"
subject2mni = "simnibs.cli.subject2mni:main"
subject_atlas = "simnibs.cli.subject_atlas:main"

[build-system]
requires = [
    "setuptools>=68",
    "wheel",
    "build",
    "numpy>=1.26,<2",
    "cython>=3.0.11",
    "setuptools-scm>=8"
]
build-backend = "setuptools.build_meta"

[tool.setuptools]
zip-safe = false
include-package-data = true

[tool.setuptools.packages.find]
where = ["."]
exclude = ["packing*", "docs*"]
```

### 第三方库功能说明

以下是 SimNIBS 依赖的主要第三方库及其功能：

| 库名称 | 功能说明 |
|--------|----------|
| **fmm3dpy** | 快速多极方法（Fast Multipole Method）的 Python 接口，用于高效的远场计算 |
| **h5py** | HDF5 文件格式的 Python 接口，用于存储和读取大型科学数据集 |
| **jsonschema** | JSON 模式验证库，用于验证配置文件和数据结构 |
| **nibabel** | 神经影像学数据读写库，支持 NIfTI、DICOM、MGH 等多种医学影像格式 |
| **numba** | JIT（即时）编译器，加速 Python 代码执行，特别适合数值计算 |
| **numpy** | 基础数值计算库，提供多维数组和数学函数支持 |
| **petsc4py** | PETSc（可移植扩展科学计算工具包）的 Python 接口，用于并行数值求解 |
| **pillow** | Python 图像处理库，用于读取和处理图像文件 |
| **pygpc** | 广义多项式混沌（Generalized Polynomial Chaos）库，用于不确定性量化 |
| **requests** | HTTP 客户端库，用于发送网络请求和下载数据 |
| **samseg** | 医学图像分割工具，用于脑部 MRI 图像分割 |
| **scipy** | 科学计算库，提供优化、积分、插值、信号处理等算法 |
| **matplotlib** | 绘图和可视化库，用于创建静态、动态和交互式图表 |
| **mkl** | Intel Math Kernel Library，提供高性能数学函数（线性代数、FFT 等） |
| **tbb** | Intel Threading Building Blocks，提供并行编程支持 |

### 可选功能组依赖库

| 库名称 | 所属功能组 | 功能说明 |
|--------|------------|----------|
| **pytest** | test | Python 测试框架，用于编写和运行测试用例 |
| **mock** | test | 测试辅助库，用于创建模拟对象和打桩 |
| **python-mumps** | mumps | MUMPS（多用途稀疏求解器）的 Python 接口，用于线性方程组求解 |

### 平台特定依赖库

| 库名称 | 平台 | 功能说明 |
|--------|------|----------|
| **mkl** | Windows/Linux | Intel 数学核心库，提供高性能数学运算（macOS 除外） |
| **tbb** | Windows/Linux | Intel 线程构建块，提供并行编程支持（macOS 除外） |

### 步骤 4: 初始化 Poetry 环境
```bash
# 创建新的 Poetry 虚拟环境
poetry env use python3.11

# 安装依赖项（包括构建依赖项）
poetry install --no-root

# 以开发模式安装包
poetry install
```

### 步骤 5: 构建 C++ 扩展

由于 CGAL 依赖关系，C++ 扩展需要特殊处理：

```bash
# 首先，确保所有系统依赖项都可访问
# 然后构建扩展
poetry run python setup.py build_ext --inplace

# 替代方案：使用禁用构建隔离的 pip 安装
# 这确保在编译过程中找到系统库
pip install --no-build-isolation -e .
```

### 步骤 6: 安装特殊依赖项

某些依赖项有特殊的安装要求：

```bash
# petsc4py（平台特定的 wheel 文件）
# Windows
poetry run pip install https://github.com/simnibs/petsc4py/releases/download/v3.21.5/petsc4py-3.21.5-cp311-cp311-win_amd64.whl

# Linux
poetry run pip install https://github.com/simnibs/petsc4py/releases/download/v3.21.5/petsc4py-3.21.5-cp311-cp311-manylinux_2_28_x86_64.whl

# macOS（检查可用的 wheel 文件或从源代码构建）
# poetry run pip install petsc4py

# python-mumps（可选但推荐用于 MUMPS 求解器）
# 注意：python-mumps 最容易通过 Conda 安装。对于 Poetry 安装：
# 选项 1：在单独的环境中通过 Conda 安装（混合方法）
# 选项 2：从源代码构建（高级）
# 选项 3：使用系统包管理器（仅限 Linux）
# 对于 Ubuntu/Debian：sudo apt-get install libmumps-dev
# 然后安装 Python 包装器：
poetry run pip install python-mumps  # 可能需要系统范围内安装 MUMPS 库

# pyopengl（用于 GUI 功能）
# 已包含在 [tool.poetry.group.gui.dependencies] 部分中
# 使用以下命令安装：poetry install --with gui
```

### 步骤 7: 运行后安装脚本
```bash
poetry run python simnibs/cli/postinstall_simnibs.py
poetry run python simnibs/cli/link_external_progs.py
```

## 平台特定说明

### Windows

#### 1. 构建工具和编译器
- **Visual Studio 2019 或 2022**：安装带有 "Desktop development with C++" 工作负载
  - 必需组件：MSVC v142/v143、Windows 10/11 SDK、C++ CMake 工具
  - 社区版免费：https://visualstudio.microsoft.com/downloads/
- **替代方案**：Visual Studio Build Tools（独立，无 IDE）
- **CMake 3.20+**：构建 CGAL 和其他 C++ 依赖项所需
  - 从 https://cmake.org/download/ 下载
  - 在安装期间添加到 PATH

#### 2. 系统库安装
**选项 A：使用 vcpkg（推荐）**
```bash
# 安装 vcpkg
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat

# 安装必需的库
.\vcpkg install cgal[core,header-only]:x64-windows
.\vcpkg install freeglut:x64-windows
.\vcpkg install zlib:x64-windows
.\vcpkg install tbb:x64-windows
.\vcpkg install mpir:x64-windows        # GMP/MPFR 替代方案
.\vcpkg install eigen3:x64-windows
.\vcpkg install boost-headers:x64-windows
```

**选项 B：手动安装**
- **CGAL 5.5+**：从 https://github.com/CGAL/cgal/releases 下载
- **Eigen 3.4+**：从 http://eigen.tuxfamily.org/ 下载
- **Boost 1.82+**：从 https://www.boost.org/users/download/ 下载
- **TBB 2021+**：从 https://github.com/oneapi-src/oneTBB/releases 下载
- **FreeGLUT 3.2+**：从 http://freeglut.sourceforge.net/ 下载
- **zlib 1.3+**：从 https://zlib.net/ 下载

#### 3. Intel MKL 安装
**选项 A：Intel oneAPI Base Toolkit**（推荐用于性能）
- 从 https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html 下载
- 使用默认选项安装
- 设置环境变量（通常自动完成）：
  - `MKLROOT`：MKL 安装路径（例如：`C:\Program Files (x86)\Intel\oneAPI\mkl\latest`）
  - 将 `%MKLROOT%\bin\intel64` 添加到 `PATH`

**选项 B：Conda MKL**（更简单但优化较少）
```bash
# 通过 conda 安装 MKL（即使在 Poetry 环境中）
conda install -c conda-forge mkl
```

**选项 C：pip 包**（功能有限）
```bash
pip install mkl
```

#### 4. 环境变量配置
设置以下环境变量（系统或用户变量）：

```cmd
rem CGAL 所需
set CGAL_DIR=C:\path\to\cgal
set BOOST_ROOT=C:\path\to\boost
set EIGEN3_INCLUDE_DIR=C:\path\to\eigen3

rem TBB 所需
set TBB_ROOT=C:\path\to\tbb

rem 常规编译所需
set INCLUDE=%CGAL_DIR%\include;%BOOST_ROOT%;%EIGEN3_INCLUDE_DIR%;%INCLUDE%
set LIB=%CGAL_DIR%\lib;%TBB_ROOT%\lib\intel64\vc14;%LIB%

rem 对于 vcpkg 安装
set VCPKG_ROOT=C:\path\to\vcpkg
set CMAKE_TOOLCHAIN_FILE=%VCPKG_ROOT%\scripts\buildsystems\vcpkg.cmake
```

#### 5. Python 开发工具
- **Python 3.11.10**：从 https://www.python.org/downloads/ 下载
  - 在安装期间勾选 "Add Python to PATH"
  - 为所有用户安装（推荐）
- **Microsoft Visual C++ Redistributable**： 
  - VS2015-2022 可再发行组件：https://aka.ms/vs/17/release/vc_redist.x64.exe

#### 6. 验证
测试您的设置：
```cmd
# 检查编译器
cl.exe

# 检查 CMake
cmake --version

# 检查 Python
python --version

# 检查环境变量
echo %CGAL_DIR%
echo %TBB_ROOT%
```

### Linux
```bash
# Ubuntu/Debian
sudo apt-get install libcgal-dev libboost-all-dev freeglut3-dev zlib1g-dev libtbb-dev

# CentOS/RHEL/Fedora
sudo yum install CGAL-devel boost-devel freeglut-devel zlib-devel tbb-devel

# 设置库路径
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

### macOS
```bash
# 使用 Homebrew
brew install cgal boost freeglut zlib tbb

# 设置库路径
export DYLD_LIBRARY_PATH=/usr/local/lib:$DYLD_LIBRARY_PATH
```

## 故障排除

### 常见问题

1. **CGAL 未找到**
   ```
   Error: CGAL library not found
   ```
   **解决方案**：将 `CGAL_DIR` 环境变量设置为 CGAL 安装目录。

2. **MKL 未找到**
   ```
   Error: MKL library not found
   ```
   **解决方案**：安装 Intel MKL 或使用 Conda 的 MKL：`conda install mkl`（即使在 Poetry 环境中）。

3. **Python-mumps 安装**
   ```
   Error: python-mumps requires Conda
   ```
   **解决方案**： 
   - **选项 A（推荐）**：在单独的环境中通过 Conda 安装（混合方法）
     ```bash
     conda install -c conda-forge python-mumps
     ```
   - **选项 B**：安装系统 MUMPS 库并构建 python-mumps
     ```bash
     # Ubuntu/Debian
     sudo apt-get install libmumps-dev
     pip install python-mumps
     ```
   - **选项 C**：使用具有 MUMPS 支持的 PETSc（如果可用）
   - **选项 D**：如果 MUMPS 非必需，使用不同的求解器（pardiso 或 hypre）

4. **PyOpenGL 安装**
   ```
   Error: Could not find OpenGL headers
   ```
   **解决方案**：安装系统 OpenGL 开发库：
   ```bash
   # Windows：已包含在图形驱动程序中
   # Ubuntu/Debian
   sudo apt-get install freeglut3-dev libgl1-mesa-dev libglu1-mesa-dev
   # macOS：已包含
   # 然后安装 pyopengl
   poetry install --with gui
   ```

5. **C++ 扩展构建失败**
   ```
   Error: undefined reference to CGAL::...
   ```
   **解决方案**：确保所有系统依赖项都正确链接。修改 `setup.py` 以使用系统路径而不是 Conda 路径。

### 修改 setup.py 以适应系统库

如果使用系统库而非 Conda 进行构建，可能需要修改 `setup.py`。以下是适用于 Windows 的全面修改：

```python
# 移除或修改开头的 Conda 依赖检查
# 原始行：
# is_conda = 'CONDA_PREFIX' in os.environ
# if not is_conda:
#     raise Exception("Cannot run setup without conda")

# 替换为系统库检测
import os
import sys
import numpy as np

# 辅助函数用于查找系统库
def get_system_lib_paths():
    """从环境变量或默认位置获取系统库路径"""
    paths = {}
    
    # CGAL 路径
    paths['cgal_dir'] = os.environ.get('CGAL_DIR', 'C:/Program Files/CGAL')
    paths['cgal_lib'] = os.environ.get('CGAL_LIB_DIR', os.path.join(paths['cgal_dir'], 'lib'))
    paths['cgal_include'] = os.environ.get('CGAL_INCLUDE_DIR', os.path.join(paths['cgal_dir'], 'include'))
    
    # Eigen 路径
    paths['eigen_include'] = os.environ.get('EIGEN3_INCLUDE_DIR', 'C:/Program Files/eigen3')
    
    # TBB 路径
    paths['tbb_dir'] = os.environ.get('TBB_ROOT', 'C:/Program Files/oneAPI/tbb/latest')
    paths['tbb_lib'] = os.environ.get('TBB_LIB_DIR', os.path.join(paths['tbb_dir'], 'lib', 'intel64', 'vc14'))
    
    # Boost 路径
    paths['boost_dir'] = os.environ.get('BOOST_ROOT', 'C:/local/boost_1_82_0')
    paths['boost_include'] = os.environ.get('BOOST_INCLUDE_DIR', os.path.join(paths['boost_dir'], 'boost'))
    
    # MPFR/GMP 路径（通常与 CGAL 一起安装）
    paths['mpfr_dir'] = os.environ.get('MPFR_DIR', paths['cgal_dir'])
    paths['gmp_dir'] = os.environ.get('GMP_DIR', paths['cgal_dir'])
    
    return paths

# 获取系统路径
sys_paths = get_system_lib_paths()

# 平台特定配置
if sys.platform == 'win32':
    # Windows 的 CGAL 配置
    cgal_dirs = [
        sys_paths['cgal_lib'],
        sys_paths['tbb_lib'],
        os.environ.get('SYSTEM_LIB_PATH', 'C:/Windows/System32')
    ]
    
    cgal_libs = ['mpfr', 'gmp', 'zlib', 'tbb', 'tbbmalloc']
    
    cgal_include = [
        np.get_include(),
        sys_paths['cgal_include'],
        sys_paths['eigen_include'],
        sys_paths['boost_include'],
        # 额外的包含路径
        os.path.join(sys_paths['cgal_include'], 'CGAL'),
    ]
    
    # 编译器参数
    cgal_compile_args = [
        '/Zi', '/WX-', '/diagnostics:classic', '/Ob0', '/Oy',
        '/D WIN32', '/D _WINDOWS', '/D _SCL_SECURE_NO_DEPRECATE',
        '/D _SCL_SECURE_NO_WARNINGS', '/D BOOST_ALL_DYN_LINK=1',
        '/D _MBCS',
        # 添加系统特定的定义
        '/D CGAL_CONCURRENT_MESH_3',
        '/D CGAL_LINKED_WITH_TBB',
        '/D CGAL_EIGEN3_ENABLED',
        '/D CGAL_USE_ZLIB=1',
        '/D NOMINMAX',  # 防止 min/max 宏
    ]
    
    cgal_link_args = [
        '/LIBPATH:' + sys_paths['cgal_lib'],
        '/LIBPATH:' + sys_paths['tbb_lib'],
    ]
    
    cgal_mesh_macros = [
        ('CGAL_MESH_3_NO_DEPRECATED_SURFACE_INDEX', None),
        ('CGAL_MESH_3_NO_DEPRECATED_C3T3_ITERATORS', None),
        ('CGAL_EIGEN3_ENABLED', None),
        ('CGAL_USE_ZLIB', 1),
        ('CGAL_CONCURRENT_MESH_3', None),
        ('CGAL_LINKED_WITH_TBB', None),
    ]

elif sys.platform == 'linux':
    # Linux 的类似修改
    cgal_dirs = ['/usr/local/lib', '/usr/lib/x86_64-linux-gnu']
    cgal_libs = ['mpfr', 'gmp', 'z', 'tbb', 'tbbmalloc', 'pthread']
    cgal_include = [
        np.get_include(),
        '/usr/local/include',
        '/usr/include/eigen3',
        '/usr/include',
    ]
    cgal_compile_args = [
        '-Os', '-flto',
        '-frounding-math',
        '-std=gnu++14',
        '-D CGAL_CONCURRENT_MESH_3',
        '-D CGAL_LINKED_WITH_TBB',
        '-D NOMINMAX',
    ]
    cgal_link_args = None
    cgal_mesh_macros += [
        ('CGAL_CONCURRENT_MESH_3', None),
        ('CGAL_LINKED_WITH_TBB', None),
        ('NOMINMAX', None),
    ]

elif sys.platform == 'darwin':
    # macOS 的类似修改
    cgal_dirs = ['/usr/local/lib', '/opt/homebrew/lib']
    cgal_libs = ['mpfr', 'gmp', 'z']
    cgal_include = [
        np.get_include(),
        '/usr/local/include',
        '/opt/homebrew/include/eigen3',
        '/opt/homebrew/include',
    ]
    cgal_compile_args = [
        '-std=gnu++14',
        '-stdlib=libc++',
        '-D NOMINMAX',
    ]
    cgal_mesh_macros += [('NOMINMAX', None)]
    cgal_link_args = ['-stdlib=libc++']
```

### 完整的 setup.py 替代方案

要获得完整的解决方案，您可以创建一个适用于系统库的新 `setup_poetry.py`：

```python
#!/usr/bin/env python
"""
setup_poetry.py - 用于基于 Poetry 安装的替代 setup.py
在使用系统库时使用此文件替代原始 setup.py。
"""

from setuptools import setup, Extension
import os
import sys
import numpy as np
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize

# 您修改的配置在这里...
# [包含上面的完整修改配置]

if __name__ == '__main__':
    setup(
        ext_modules=cythonize(extensions),
        cmdclass={'build_ext': build_ext},
        # 其他 setup 参数...
    )
```

使用此替代设置文件：
```bash
# 使用修改后的设置文件构建
poetry run python setup_poetry.py build_ext --inplace

# 或者使用替代设置通过 pip 安装
pip install --no-build-isolation -e . --config-settings="--global-option=build_ext" --config-settings="--global-option=-I/path/to/include"
```

## 使用 Poetry 进行开发

### 添加依赖项
```bash
# 添加主要依赖项
poetry add package-name

# 添加开发依赖项
poetry add --group dev package-name

# 添加 GUI 依赖项
poetry add --group gui package-name

# 添加 MUMPS 求解器依赖项（可选）
poetry add --group mumps python-mumps

# 添加特定版本的依赖项
poetry add "package-name>=1.0,<2.0"
```

### 运行 SimNIBS 命令
```bash
# 运行任何 SimNIBS 命令
poetry run simnibs --help
poetry run charm --help

# 激活 Poetry shell 进行交互式使用
poetry shell
simnibs --help
```

### 更新依赖项
```bash
# 更新所有依赖项
poetry update

# 更新特定依赖项
poetry update package-name
```

## 替代方案：混合方法

如果系统依赖项安装太复杂，可以考虑混合方法：

1. **仅使用 Conda 安装系统库**：
   ```bash
   conda create -n simnibs-libs -c conda-forge \
     cgal-cpp freeglut zlib tbb-devel mkl python=3.11
   conda activate simnibs-libs
   ```

2. **使用 Poetry 安装 Python 包**：
   ```bash
   # 在 Conda 环境中安装 Poetry
   pip install poetry
   
   # 初始化 Poetry（它将使用 Conda 环境）
   poetry init
   poetry install
   ```

## 替代方案：包装脚本方法

为了获得更自动化的解决方案，您可以创建处理系统依赖项安装和 Poetry 设置的包装脚本：

### 1. Windows 安装包装脚本 (`install_simnibs_poetry.bat`)

```batch
@echo off
REM SimNIBS Poetry 安装包装脚本 for Windows
setlocal enabledelayedexpansion

echo ========================================
echo SimNIBS Poetry 安装脚本
echo ========================================

REM 检查先决条件
echo 检查先决条件...

REM 1. 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: 未找到 Python。请安装 Python 3.11+
    exit /b 1
)

REM 2. 检查 Visual Studio 构建工具
echo 检查 Visual Studio 构建工具...
where cl.exe >nul 2>&1
if errorlevel 1 (
    echo WARNING: 在 PATH 中未找到 Visual Studio 构建工具。
    echo 请安装带有 C++ 桌面开发工作负载的 Visual Studio 2019/2022。
)

REM 3. 安装 vcpkg 和依赖项
echo 通过 vcpkg 安装系统依赖项...
if not exist "vcpkg" (
    git clone https://github.com/Microsoft/vcpkg.git
    cd vcpkg
    call bootstrap-vcpkg.bat
    vcpkg install cgal:x64-windows freeglut:x64-windows zlib:x64-windows tbb:x64-windows
    cd ..
)

REM 4. 设置环境变量
echo 设置环境变量...
set CGAL_DIR=%~dp0vcpkg\installed\x64-windows
set TBB_ROOT=%~dp0vcpkg\installed\x64-windows
set EIGEN3_INCLUDE_DIR=%~dp0vcpkg\installed\x64-windows\include\eigen3

REM 5. 如果不存在则安装 Poetry
echo 检查 Poetry...
poetry --version >nul 2>&1
if errorlevel 1 (
    echo 安装 Poetry...
    pip install poetry
)

REM 6. 安装 SimNIBS 依赖项
echo 安装 Python 依赖项...
poetry install

REM 7. 构建 C++ 扩展
echo 构建 C++ 扩展...
poetry run python setup.py build_ext --inplace

REM 8. 安装特殊的 wheel 文件
echo 安装特殊依赖项...
poetry run pip install https://github.com/simnibs/petsc4py/releases/download/v3.21.5/petsc4py-3.21.5-cp311-cp311-win_amd64.whl

echo ========================================
echo 安装完成！
echo 要使用 SimNIBS：
echo   1. 激活 Poetry 环境：poetry shell
echo   2. 运行任何命令：poetry run simnibs --help
echo ========================================
```

### 2. Linux/macOS 安装包装脚本 (`install_simnibs_poetry.sh`)

```bash
#!/bin/bash

# SimNIBS Poetry 安装包装脚本 for Linux/macOS

echo "========================================"
echo "SimNIBS Poetry 安装脚本"
echo "========================================"

# 检查先决条件
echo "检查先决条件..."

# 1. 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: 未找到 Python3。请安装 Python 3.11+"
    exit 1
fi

# 2. 安装系统依赖项
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "为 Linux 安装系统依赖项..."
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y libcgal-dev libboost-all-dev freeglut3-dev zlib1g-dev libtbb-dev
    # CentOS/RHEL/Fedora
    elif command -v yum &> /dev/null; then
        sudo yum install -y CGAL-devel boost-devel freeglut-devel zlib-devel tbb-devel
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "为 macOS 安装系统依赖项..."
    if command -v brew &> /dev/null; then
        brew install cgal boost freeglut zlib tbb
    else
        echo "ERROR: 未找到 Homebrew。请先安装 Homebrew。"
        exit 1
    fi
fi

# 3. 设置环境变量
echo "设置环境变量..."
export LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
export DYLD_LIBRARY_PATH="/usr/local/lib:$DYLD_LIBRARY_PATH"

# 4. 如果不存在则安装 Poetry
if ! command -v poetry &> /dev/null; then
    echo "安装 Poetry..."
    pip3 install poetry
fi

# 5. 安装 SimNIBS 依赖项
echo "安装 Python 依赖项..."
poetry install

# 6. 构建 C++ 扩展
echo "构建 C++ 扩展..."
poetry run python setup.py build_ext --inplace

# 7. 安装特殊的 wheel 文件（仅限 Linux）
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "安装特殊依赖项..."
    poetry run pip install https://github.com/simnibs/petsc4py/releases/download/v3.21.5/petsc4py-3.21.5-cp311-cp311-manylinux_2_28_x86_64.whl
fi

echo "========================================"
echo "安装完成！"
echo "要使用 SimNIBS："
echo "  1. 激活 Poetry 环境：poetry shell"
echo "  2. 运行任何命令：poetry run simnibs --help"
echo "========================================"
```

### 3. 修改的 setup.py 包装函数

为了更容易集成，您可以创建一个动态修改 `setup.py` 的包装函数：

```python
#!/usr/bin/env python
"""
setup_system.py - 使用系统库构建 SimNIBS 的包装脚本
"""

import os
import sys
import subprocess
import shutil

def setup_with_system_libs():
    """创建使用系统库的修改版 setup.py"""
    
    # 读取原始 setup.py
    with open('setup.py', 'r') as f:
        content = f.read()
    
    # 修改 Conda 依赖检查
    modified_content = content.replace(
        "is_conda = 'CONDA_PREFIX' in os.environ\nif not is_conda:\n    raise Exception(\"Cannot run setup without conda\")",
        "# 修改为系统库安装\n# 已移除 Conda 依赖检查以支持系统库"
    )
    
    # 写入临时设置文件
    temp_file = 'setup_system_temp.py'
    with open(temp_file, 'w') as f:
        f.write(modified_content)
    
    try:
        # 使用修改后的设置进行构建
        print("使用系统库构建...")
        subprocess.run([sys.executable, temp_file, 'build_ext', '--inplace'], check=True)
        print("构建成功！")
        
        # 安装包
        subprocess.run([sys.executable, temp_file, 'develop'], check=True)
        print("安装完成！")
        
    finally:
        # 清理
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == '__main__':
    setup_with_system_libs()
```

### 使用包装脚本

1. **将包装脚本保存在 SimNIBS 项目根目录中**
2. **使其可执行（Linux/macOS）**：`chmod +x install_simnibs_poetry.sh`
3. **运行脚本**：
   ```bash
   # Windows
   install_simnibs_poetry.bat
   
   # Linux/macOS
   ./install_simnibs_poetry.sh
   ```

### 包装方法的优势

1. **自动化**：自动处理所有安装步骤
2. **错误处理**：包括先决条件检查和错误消息
3. **可移植性**：适用于不同平台
4. **可重复性**：确保一致的安装过程
5. **备用选项**：可以包含替代安装方法

### 自定义

您可以根据特定需求自定义包装脚本：
- 添加更详细的日志记录
- 包含用于用户输入的交互式提示
- 添加不同安装配置的选项
- 安装后包含验证测试
- 为失败的安装添加清理功能

## 结论

将 Poetry 与 SimNIBS 结合使用提供了更好的 Python 依赖管理，但需要手动处理系统依赖项。这种方法适用于想要更多控制环境或无法在工作流中使用 Conda 的开发者。

对于大多数用户，基于 Conda 的官方安装（使用 `environment_win.yml`）仍然是推荐的方法，因为它自动处理所有系统依赖项。

## 参考资料

- [SimNIBS 文档](https://simnibs.github.io/simnibs/)
- [Poetry 文档](https://python-poetry.org/docs/)
- [CGAL 安装指南](https://doc.cgal.org/latest/Manual/installation.html)
- [vcpkg 包管理器](https://vcpkg.io/)
