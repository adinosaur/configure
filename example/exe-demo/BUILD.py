# -*- coding=utf-8 -*-

from __main__ import ExeTarget
import glob

class ExeDemo(ExeTarget):
    def __init__(self):
        super(ExeDemo, self).__init__()
        
        self.name = 'example/exe-demo/a.out'
        
        self.cxxflags = ['-g']                          # 编译参数
        self.incs = ['example/exe-demo/']               # 头文件搜索路径
        self.srcs = glob.glob('example/exe-demo/*.cpp') # 源文件列表

        self.deps = []                                  # 链接的依赖文件
        self.ldflags = []                               # 链接的参数
        self.libs = []                                  # 链接的库文件

ExeDemo()