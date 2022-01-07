# -*- coding=utf-8 -*-

from __main__ import StaticLibraryTarget
import os

class StaticLibraryDemo(StaticLibraryTarget):
    def __init__(self):
        super(StaticLibraryDemo, self).__init__()
        
        if os.name == 'posix':
            self.name = 'example/staticlib-demo/liby.a'
            self.cxxflags = ['-g']                          # 编译参数
            self.incs = []                                  # 头文件搜索路径
            self.srcs = ['example/staticlib-demo/y.cpp']    # 源文件列表

        elif os.name == 'nt':
            self.name = 'example\\staticlib-demo\\liby.lib'
            self.cxxflags = ['/Od']                         # 编译参数
            self.incs = []                                  # 头文件搜索路径
            self.srcs = ['example\\staticlib-demo\\y.cpp']  # 源文件列表

StaticLibraryDemo()