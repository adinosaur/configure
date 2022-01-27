# -*- coding=utf-8 -*-

from __main__ import ExeTarget
import glob
import os

class UnityDemo(ExeTarget):
    def __init__(self):
        super(UnityDemo, self).__init__()
        
        if os.name == 'posix':
            self.name = '{BUILD_DIR1}/example/unity-demo/unity-demo'
            self.cxxflags = self.cxxflags + ['-g']          # 编译参数
            self.incs = []                                  # 头文件搜索路径
            self.srcs = glob.glob('example/unity-demo/*.cpp') # 源文件列表

        elif os.name == 'nt':
            self.name = '{BUILD_DIR}\\example\\unity-demo\\unity-demo.exe'
            self.cxxflags = ['/Od']                         # 编译参数
            self.incs = []                                  # 头文件搜索路径
            self.srcs = glob.glob('example\\unity-demo\\*.cpp') # 源文件列表
        
        self.enable_unity = True

UnityDemo()