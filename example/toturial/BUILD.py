# -*- coding=utf-8 -*-

from __main__ import ExeTarget
import glob
import os

class Toturial(ExeTarget):
    def __init__(self):
        super(Toturial, self).__init__()
        
        if os.name == 'posix':
            self.name = 'example/toturial/toturial'
            self.cxxflags = ['-g']                          # 编译参数
            self.incs = []                                  # 头文件搜索路径
            self.srcs = glob.glob('example/toturial/*.cpp') # 源文件列表
            self.deps = [
                'build/example/staticlib-demo/liby.a',
                'build/example/sharedlib-demo/libx.so',
            ]
            self.ldflags = []                               # 链接的参数
            self.libs = [
                'build/example/staticlib-demo/liby.a',
                'build/example/sharedlib-demo/libx.so',
                '-ldl',
            ]

        elif os.name == 'nt':
            self.name = 'example\\toturial\\toturial.exe'
            self.cxxflags = ['/Od']                         # 编译参数
            self.incs = []                                  # 头文件搜索路径
            self.srcs = glob.glob('example\\toturial\\*.cpp') # 源文件列表
            self.deps = [
                'build\\example\\staticlib-demo\\liby.lib',
            ]
            self.ldflags = []                               # 链接的参数
            self.libs = [
                'build\\example\\staticlib-demo\\liby.lib',
            ]

Toturial()