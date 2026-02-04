# Task
  * [x] 使用官方的exe安装，然后使用自带的解释器Simnibs_python执行脚本 (只适合修改参数,不适合自定义开发)
  * [x] 按照官方github上的方式，使用conda来安装 (conda安装包时要注意协议)
    * 使用miniforge,使用的源是conda-forge,社区维护的
  * [ ] ~~按照项目开发方式安装~~ (Simnibs是GPL3.0协议,不能用这种方法)
    * ~~单独编译底层库，提供dll或者exe~~
    * ~~poetry安装python库~~
    * ~~保留simnibs中有用的源码部分~~
  * [ ] 把相关的python源码和C++源码一起做成exe并开源
    * github fork Simnibs的仓库
    * 使用poetry
    * 去掉无用内容(可选)
      * matlab相关
      * conda相关
      * pyqt相关
      * matplotlib相关
      * mumps相关(可选).这个求解器是SimNIBS对于mac不能使用其他求解器才加入的,不用这个也可以用别的.去掉的好处是不用编译mumps相关的东西,太复杂,最终打包时也容易出问题
    * 打包成exe
  * [x] 列举simnibs中可使用的参数
    * 正向计算
    * leadfield
    * 逆向优化 (参数调整后运行一次太慢了,有些参数相互影响,乱设置会导致报错)
  * [x] 头模生成
    * atlas配准
    * 分割 https://www.sciencedirect.com/science/article/pii/S1053811920305309
    * 生成表面 .gii
      * 读取freeSurfer的结果
      * 仿照CAT12(matlab库) python手搓
    * 有限元网格生成 .msh cgal得到的结构再转成.msh
  * [ ] FEM计算
  * [x] 优化算法
    * https://docs.scipy.org/doc/scipy/reference/optimize.html#module-scipy.optimize
    * DIviding RECTangles (DIRECT) 确定性结果 慢
    * Differential Evolution 不确定结果,用multi-target多跑几次取最好的结果 
  * [x] 如何自定义优化算法
    * 从文档来看不能,可以尝试使用scipy中其他优化算法
  * [x] 如何自定义目标函数
    * 可以传入自定义函数
    * user provided function taking e-field as an input which is a list of list of np.ndarrays of float [n_channel_stim][n_roi] containing np.array with e-field
    * gpt的示例,能跑,还需明白这个函数具体是怎么起作用的
      ```python
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
      ```
    * 貌似会导致hdf5的无法序列化问题?
  * [x] 可视化
    * 使用自带的gmsh查看msh文件
    * 后端输出为ply文件,把Node、Element、NodeValue、ElementValue都存进去,前端用NodeValue后处理为颜色
    * https://github.com/amandaghassaei/msh-parser 前端直接读取msh,再做后处理,仍需验证
  * [x] TI-toolbo
    * 核心功能就是SimNIBS
    * 增加了一个使用leadfield暴力搜索的TI逆向优化方法
    * 增加额外的功能:文件管理、文件格式转换到别的3D可视化软件、假设检验，以及一些不太重要的功能
    * 软件的架构复杂,部署困难
    * SimNIBS中很多参数并没有在GUI上可以设置,应该还是以简单能用为主
  * [x] 比较穹顶和SimNIBS的差异