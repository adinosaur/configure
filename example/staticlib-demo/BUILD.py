from __main__ import StaticLibraryTarget

class StaticLibraryDemo(StaticLibraryTarget):
    def __init__(self):
        super(StaticLibraryDemo, self).__init__()
        
        self.name = 'example/staticlib-demo/liby.a'
        
        self.cxxflags = ['-g']                          # 编译参数
        self.incs = []                                  # 头文件搜索路径
        self.srcs = ['example/staticlib-demo/y.cpp']    # 源文件列表

StaticLibraryDemo()