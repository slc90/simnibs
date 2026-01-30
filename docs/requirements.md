# 任务
  * [x] 使用官方的exe安装，然后使用自带的解释器Simnibs_python执行脚本 (只适合修改参数,不适合自定义开发)
  * [x] ~~按照官方github上的方式，使用conda来安装~~ (conda安装包时要注意协议)
  * [ ] ~~按照项目开发方式安装~~ (Simnibs是GPL3.0协议,不能用这种方法)
    * [ ] ~~单独编译底层库，提供dll或者exe~~
    * [ ] ~~poetry安装python库~~
    * [ ] ~~保留simnibs中有用的源码部分~~
  * [ ] 把相关的python源码和C++源码一起做成exe并开源
    * [x] github fork Simnibs的仓库
    * [ ] 去掉无用内容
    * [x] 去掉conda相关
    * [ ] 打包成exe
  * [x] 列举simnibs中可使用的参数
    * [x] 正向计算
    * [x] leadfield
    * [x] 逆向优化 (参数调整后运行一次太慢了,有些参数相互影响,乱设置会导致报错)
  * [ ] 头模生成
    * [ ] 重建
    * [ ] 分割
    * [ ] 有限元网格生成
  * [ ] FEM计算
  * [ ] 优化算法
    * [ ] DIviding RECTangles (DIRECT)
    * [ ] Differential Evolution
  * [x] 如何自定义优化算法
    * 从文档来看不能
    * 仿照自带的direct和differential_evolution,增加自己的函数,返回OptimizeResult类
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
  * [ ] gmsh可视化
  * [x] TI-toolbox
    * 核心功能就是SimNIBS
    * 增加了一个使用leadfield暴力搜索的TI逆向优化方法
    * 增加额外的功能:文件管理、文件格式转换到别的3D可视化软件、假设检验，以及一些不太重要的功能
    * 软件的架构复杂,部署困难
    * SimNIBS中很多参数并没有在GUI上可以设置,应该还是以简单能用为主
  * [ ] 比较穹顶和SimNIBS的差异