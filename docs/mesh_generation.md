# SimNIBS 网格生成流程

## 概述

SimNIBS（Simulation of Non-Invasive Brain Stimulation）中的网格生成是将医学影像（MRI）数据转换为可用于有限元方法（FEM）计算的四面体网格的关键步骤。该流程实现了从分割后的标记图像到高质量、个体化头部模型的自动化转换，为后续的电场计算提供几何基础。

## 完整工作流程

### 1. 输入数据准备
- **输入**: 分割后的标记图像（NIfTI格式），每个体素包含组织类型标签（如：1=白质，2=灰质，3=脑脊液等）
- **预处理**: 图像重采样到各向同性分辨率，确保网格生成质量
- **仿射变换**: 定义从体素空间到世界坐标空间的变换矩阵

### 2. 组织厚度计算
- 使用距离变换算法计算每个组织区域的本征厚度
- 厚度信息用于确定局部网格尺寸（薄区域使用更小的网格单元）
- 厚度计算考虑了组织边界和区域连通性

### 3. 尺寸场生成
- **元素尺寸控制**: 根据组织厚度动态调整网格单元大小
  ```python
  # 尺寸场计算规则
  size = slope × thickness
  size = clamp(size, min_size, max_size)
  ```
- **表面尺寸控制**: 为不同组织表面设置特定的三角形尺寸
- **距离场控制**: 控制网格表面与原始图像边界的逼近精度

### 4. CGAL 3D网格生成
- 使用CGAL（Computational Geometry Algorithms Library）的3D网格生成模块
- 基于Delaunay细化算法生成四面体网格
- 关键参数控制：
  - `facet_angle`: 表面三角形的最小角度（确保三角形质量）
  - `facet_size`: 表面三角形的最大尺寸
  - `facet_distance`: 表面与原始边界的最大距离
  - `cell_radius_edge_ratio`: 四面体的半径边比（控制单元形状质量）
  - `cell_size`: 四面体的最大尺寸

### 5. 网格后处理与优化
1. **尖刺去除**: 检测并移除网格表面的异常尖刺结构
2. **连通分量分析**: 保留最大的连通分量，移除孤立的小组件
3. **表面重建**: 从四面体网格中提取组织界面表面
4. **表面平滑**: 应用拉普拉斯平滑算法改善表面质量
5. **MMG优化**: 使用MMG（Mesh Metric Gradient）库进行网格质量改进
   - 顶点重定位
   - 边翻转
   - 单元分割与合并

### 6. 奶油层处理（可选）
- 在头部外部添加一层虚拟组织用于改善外部表面质量
- 网格生成后移除奶油层，保留光滑的外部表面

## 关键库与算法

### 1. CGAL（计算几何算法库）
- **功能**: 3D网格生成和几何处理的核心库
- **算法**: Delaunay细化、表面网格生成、多边形网格处理
- **SimNIBS集成**: 通过Cython扩展实现Python绑定

### 2. Gmsh
- **功能**: 3D有限元网格生成器
- **用途**: 网格可视化、格式转换、基础网格操作
- **文件格式**: SimNIBS使用Gmsh的.msh格式作为标准网格格式

### 3. Marching Cubes算法
- **位置**: `segmentation/marching_cube.py`
- **功能**: 从体数据中提取等值面
- **应用**: 脑表面提取、初始表面生成
- **优化**: 使用Lewiner改进版本，支持步长控制和连通分量提取

### 4. MMG（Mesh Metric Gradient）
- **功能**: 各向异性网格优化和自适应细化
- **算法**: 基于度量的顶点重定位和边操作
- **SimNIBS应用**: 提高网格单元质量，优化表面三角形

### 5. 距离变换算法
- **功能**: 计算体素到组织边界的距离
- **应用**: 组织厚度估计，用于尺寸场生成
- **实现**: 基于scipy.ndimage的高效实现

## 代码结构与关键函数

### 主要模块结构
```
simnibs/mesh_tools/
├── meshing.py              # 主网格生成函数
├── mesh_io.py              # 网格文件读写（Gmsh格式）
├── surface.py              # 表面网格操作
├── cgal/                   # CGAL Python绑定
│   ├── create_mesh_vol.pyx # 体网格生成
│   ├── create_mesh_surf.pyx # 表面网格生成
│   └── polygon_mesh_processing.pyx # 多边形处理
└── cython_msh.pyx          # Cython网格操作
```

### 核心函数

#### 1. `create_mesh()` - 主网格生成函数
**位置**: `mesh_tools/meshing.py`
**功能**: 从标记图像创建四面体网格的完整流程
**主要参数**:
- `label_img`: 3D标记图像（uint8/uint16）
- `affine`: 4×4仿射变换矩阵
- `elem_sizes`: 元素尺寸控制参数
- `facet_distances`: 表面逼近精度参数
- `optimize`: 是否进行CGAL优化
- `remove_spikes`: 是否移除尖刺

**内部调用流程**:
```python
1. thickness = _calc_thickness(label_img)           # 计算组织厚度
2. size_field = _sizing_field_from_thickness(...)   # 生成尺寸场
3. m = image2mesh(...)                              # CGAL网格生成
4. m = _remove_spikes(...)                          # 移除尖刺
5. m.reconstruct_unique_surface(...)                # 表面重建
6. m = _run_mmg(...)                                # MMG优化
```

#### 2. `image2mesh()` - CGAL网格生成接口
**功能**: 调用CGAL库从图像生成四面体网格
**关键步骤**:
1. 验证图像数据类型（uint8/uint16）
2. 分解仿射矩阵，检查剪切分量
3. 设置默认网格参数
4. 调用Cython/C++扩展执行CGAL网格生成
5. 应用仿射变换到节点坐标

#### 3. `marching_cube()` - 表面提取函数
**位置**: `segmentation/marching_cube.py`
**功能**: 从体数据中提取等值面
**特点**:
- 支持步长控制以减少三角形数量
- 可提取最大连通分量
- 支持均匀重网格化优化

### 4. `_run_mmg()` - 网格优化函数
**功能**: 调用MMG库进行网格质量改进
**优化策略**:
1. **第一阶段**: 基本质量改进，保持拓扑
2. **第二阶段**: 激进优化，可能改变拓扑
3. **尺寸场引导**: 可选尺寸场控制优化过程

## 网格生成算法详解

### Delaunay细化算法
CGAL使用的核心算法，确保生成高质量的四面体网格：

1. **初始Delaunay三角剖分**: 在定义域内创建初始点集
2. **表面保护**: 插入保护点确保表面逼近精度
3. **细化标准检查**:
   - 半径边比检查（消除狭长四面体）
   - 尺寸检查（控制四面体大小）
   - 表面距离检查（确保表面逼近）
4. **迭代细化**: 在违反标准的位置插入新点
5. **优化后处理**:
   - 扰动（Perturbation）：消除银状四面体
   - 渗出（Exudation）：进一步改善单元质量
   - 劳埃德优化（Lloyd optimization）：均匀化单元分布

### 尺寸场自适应策略
SimNIBS使用基于组织厚度的自适应尺寸场：

1. **厚度映射**: `thickness = f(label_img)`
2. **尺寸计算**: 
   ```
   对于每个体素v：
     thickness = 局部组织厚度
     base_size = slope × thickness
     final_size = clamp(base_size, min_size, max_size)
   ```
3. **平滑处理**: 应用高斯平滑消除厚度估计异常值
4. **表面特殊处理**: 外层表面（皮肤）使用固定小尺寸确保电极放置精度

### 尖刺检测与移除算法
尖刺是网格表面的异常细长突起，影响仿真精度：

1. **连通性分析**: 构建顶点邻接矩阵
2. **候选检测**: 识别度数为1的顶点链（潜在的尖刺）
3. **几何验证**: 检查角度和长度是否符合尖刺特征
4. **标签传播**: 确定尖刺的正确组织标签
5. **分裂与合并**: 
   - 长尖刺：在适当位置分割
   - 短尖刺：合并到相邻区域

## 输出网格结构与属性

### 网格文件格式
- **主格式**: Gmsh .msh 格式（版本4.1）
- **元素类型**: 四面体（体积）、三角形（表面）
- **组织标签**: 每个元素包含组织类型标签（1-1000为体积，1001+为表面）

### 标准组织标签
| 标签 | 组织类型 | 描述 |
|------|----------|------|
| 1 | 白质（WM） | 脑白质组织 |
| 2 | 灰质（GM） | 脑灰质组织 |
| 3 | 脑脊液（CSF） | 脑室和蛛网膜下腔 |
| 4 | 骨（Bone） | 平均骨组织 |
| 5 | 头皮（Scalp） | 头皮组织 |
| 6 | 眼球（Eye balls） | 眼球组织 |
| 7 | 密质骨（Compact bone） | 致密骨组织 |
| 8 | 松质骨（Spongy bone） | 多孔骨组织 |
| 9 | 血液（Blood） | 血液组织 |
| 10 | 肌肉（Muscle） | 头部肌肉组织 |
| 11 | 软骨（Cartilage） | 耳鼻软骨组织 |
| 12 | 脂肪（Fat） | 脂肪组织 |
| 100 | 电极橡胶（Electrode rubber） | tDCS橡胶电极材料 |
| 500 | 盐水（Saline） | tDCS海绵电极盐水 |
| 999 | 奶油层（Cream） | 临时添加的网格优化层 |

### 表面标签系统
SimNIBS使用统一的标签映射规则来区分体积元素和表面元素：

#### 标签映射规则
1. **体积元素标签**: 1-999
2. **表面元素标签**: 体积标签 + 1000

#### 表面标签示例
| 体积标签 | 表面标签 | 表面类型 |
|----------|----------|----------|
| 1 (WM) | 1001 | 白质表面 |
| 2 (GM) | 1002 | 灰质表面 |
| 3 (CSF) | 1003 | 脑脊液表面 |
| 5 (Scalp) | 1005 | 头皮表面 |
| 100 (Electrode rubber) | 1100 | 电极橡胶表面 |
| 500 (Saline) | 1500 | 盐水表面 |

#### 特殊表面标签范围
- **2000-2499**: 电极插头表面（Electrode plug surfaces）
- **5000-5999**: 左半球表面（Left hemisphere surfaces）
- **6000-6999**: 左半球中央皮层表面（Left hemisphere central cortical surfaces）
- **7000-7999**: 右半球表面（Right hemisphere surfaces）
- **8000-8999**: 右半球中央皮层表面（Right hemisphere central cortical surfaces）

#### 中央皮层分层标签
SimNIBS支持皮质分层分析，使用特定标签表示不同皮层深度：
- **LH_CENTRAL_LAYER_1** (6001): 左半球第1层，深度0.06
- **LH_CENTRAL_LAYER_23** (6101): 左半球第2-3层，深度0.40
- **LH_CENTRAL_LAYER_4** (6102): 左半球第4层，深度0.55
- **LH_CENTRAL_LAYER_5** (6103): 左半球第5层，深度0.65
- **LH_CENTRAL_LAYER_6** (6104): 左半球第6层，深度0.85
- 右半球对应标签为8001-8104

#### 标签使用示例
```python
from simnibs.utils.mesh_element_properties import ElementTags

# 提取灰质体积元素
gm_volume = mesh.crop_mesh([ElementTags.GM])

# 提取灰质表面元素
gm_surface = mesh.crop_mesh([ElementTags.GM_TH_SURFACE])

# 提取左半球灰质表面
lh_gm_surface = mesh.crop_mesh([ElementTags.LH_GM_SURFACE])
```

### 网格质量指标
- **半径边比**: 理想值 < 3.0
- **四面体体积**: 避免过小或负体积单元
- **三角形质量**: 最小角度 > 30度
- **表面法向一致性**: 确保正确方向

## 性能优化策略

### 并行计算
- CGAL网格生成支持多线程（`num_threads`参数）
- 厚度计算使用矢量化操作
- 大型图像支持分块处理

### 内存管理
- 及时释放中间数据（尺寸场、距离场）
- 使用内存映射处理大型图像
- 增量式网格处理减少峰值内存使用

### 算法优化
- 快速距离变换算法
- 增量式连通分量分析
- 局部重网格化代替全局重生成

## 故障排除与调试

### 常见问题
1. **网格生成失败**: 通常由于图像质量问题或仿射矩阵包含剪切分量
2. **表面不封闭**: 检查分割图像是否包含完整的组织边界
3. **尖刺过多**: 调整`remove_spikes`参数或增加平滑步骤
4. **内存不足**: 减少图像尺寸或使用更宽松的网格参数

### 调试工具
- **中间文件保存**: 设置`debug=True`保存各阶段网格
- **质量统计**: 使用`mesh_io`的质量检查函数
- **可视化**: 使用Gmsh或PyVista查看网格

## 应用实例

### CHARM流程集成
```python
# CHARM分割流程中的网格生成
from simnibs.mesh_tools.meshing import create_mesh

# 从分割结果创建网格
mesh = create_mesh(
    label_img=segmentation_labels,
    affine=affine_matrix,
    elem_sizes={"standard": {"range": [1, 5], "slope": 1.0}},
    facet_distances={"standard": {"range": [0.1, 3], "slope": 0.5}},
    optimize=True,
    remove_spikes=True,
    skin_tag=1005
)
```

### 自定义网格生成
```python
# 自定义尺寸场控制
custom_sizing_field = calculate_custom_sizes(label_img)
mesh = create_mesh(
    label_img=label_img,
    affine=affine,
    sizing_field=custom_sizing_field,
    skin_facet_size=1.5,  # 更精细的外部表面
    smooth_steps=10       # 更多平滑步骤
)
```

## 参考文献

1. **CGAL文档**: https://doc.cgal.org/latest/Mesh_3/index.html
2. **Gmsh手册**: https://gmsh.info/doc/texinfo/gmsh.html
3. **Delaunay细化**: Shewchuk, J. R. (1998). Tetrahedral mesh generation by Delaunay refinement.
4. **Marching Cubes**: Lewiner, T., et al. (2003). Efficient implementation of Marching Cubes' cases with topological guarantees.
5. **MMG库**: Dapogny, C., et al. (2014). Three-dimensional adaptive domain remeshing, implicit domain meshing, and applications to free and moving boundary problems.

## 未来发展

1. **深度学习集成**: 使用神经网络预测最优网格参数
2. **各向异性网格**: 支持基于扩散张量的各向异性网格生成
3. **实时网格更新**: 支持术中影像的快速网格更新
4. **云网格生成**: 分布式网格生成服务
5. **自动化质量控制**: 基于机器学习的网格质量评估

---

*文档最后更新: 2024年*
*SimNIBS版本: 4.1*