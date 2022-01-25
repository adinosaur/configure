# -*- coding=utf-8 -*-

from __main__ import ExeTarget
import glob
import os

class CDemo(ExeTarget):
    def __init__(self):
        super(CDemo, self).__init__()
        
        if os.name == 'posix':
            self.name = '{build_dir}/example/c-demo/a.out'
            self.cflags = ['-g']                            # 编译参数
            self.incs = ['example/c-demo/']                 # 头文件搜索路径
            self.srcs = glob.glob('example/c-demo/*.c')     # 源文件列表
            self.deps = []                                  # 链接的依赖文件
            self.ldflags = []                               # 链接的参数
            self.libs = []                                  # 链接的库文件

        elif os.name == 'nt':
            self.name = '{build_dir}\\example\\c-demo\\a.exe'
            self.cflags = ['/Od']                           # 编译参数
            self.incs = ['example\\c-demo\\']               # 头文件搜索路径
            self.srcs = glob.glob('example\\c-demo\\*.c')   # 源文件列表
            self.deps = []                                  # 链接的依赖文件
            self.ldflags = []                               # 链接的参数
            self.libs = []                                  # 链接的库文件

CDemo()