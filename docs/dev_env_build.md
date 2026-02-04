# 需要的底层库
1. cgal == 5.5.1 https://github.com/CGAL/cgal/releases?page=2
2. boost == 1.78.0 https://www.boost.org/releases/1.78.0/
3. mpfr == 4.2.1 (使用vcpkg安装,安装版本为 4.2.2)
4. gmp == 6.3.0 (使用vcpkg安装, 安装版本为 6.3.0)
5. zlib == 1.3.1 (使用vcpkg安装, 安装版本为 1.3.1)
6. eigen3 == 3.4.0 https://gitlab.com/libeigen/eigen/-/releases
7. mumps == 5.7.3 
    * https://github.com/scivision/mumps/blob/main/Readme_options.md
    * https://blog.actpi.com/articles/2023/compile_mumps.html
    * https://github.com/PyMumps/pymumps 创建wheel时用Intel One Api编译器,需要修改setup.py
    * 即使这样编译成功后,运行时也需要Intel One Api的dll,所以最好得把所有dll都找齐,一起带进wheel
8. tbb == 2022.3.0 (使用vcpkg安装, 安装版本为 2022.3.0)