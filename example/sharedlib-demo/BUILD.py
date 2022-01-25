# -*- coding=utf-8 -*-

from __main__ import SharedLibraryTarget
import os

class SharedLibraryDemo(SharedLibraryTarget):
    def __init__(self):
        super(SharedLibraryDemo, self).__init__()
        
        if os.name == 'posix':
            self.name = '{build_dir}/example/sharedlib-demo/libx.so'
            self.cxxflags = ['-g']                          # 编译参数
            self.incs = []                                  # 头文件搜索路径
            self.srcs = ['example/sharedlib-demo/x.cpp']    # 源文件列表
            self.deps = []                                  # 链接的依赖文件
            self.ldflags = ['-rdynamic']                    # 链接的参数
            self.libs = []                                  # 链接的库文件

        elif os.name == 'nt':
            self.name = '{build_dir}\\example\\sharedlib-demo\\libx.dll'
            self.cxxflags = []                              # 编译参数
            self.incs = []                                  # 头文件搜索路径
            self.srcs = ['example\\sharedlib-demo\\x.cpp']  # 源文件列表
            self.deps = []                                  # 链接的依赖文件
            self.ldflags = []                               # 链接的参数
            self.libs = []                                  # 链接的库文件

SharedLibraryDemo()