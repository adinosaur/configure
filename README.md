# Configure
`configure.py` 是一个轻量级的C/C++构建系统。它会自动加载目录下的所有`BUILD.py`文件，生成`build.ninja`，最后交由ninja来执行构建。

# Usgae
## 1. 构建可执行程序
```python
# example/exe-demo/BUILD.py

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
```

## 2. 构建动态连接库
```python
# example/sharedlib-demo/BUILD.py

class SharedLibraryDemo(SharedLibraryTarget):
    def __init__(self):
        super(SharedLibraryDemo, self).__init__()
        
        self.name = 'example/sharedlib-demo/libx.so'
        
        self.cxxflags = ['-g']                          # 编译参数
        self.incs = []                                  # 头文件搜索路径
        self.srcs = ['example/sharedlib-demo/x.cpp']    # 源文件列表

        self.deps = []                                  # 链接的依赖文件
        self.ldflags = ['-rdynamic']                    # 链接的参数
        self.libs = []                                  # 链接的库文件
```

## 3. 构建静态连接库
```python
# example/staticlib-demo/BUILD.py

class StaticLibraryDemo(StaticLibraryTarget):
    def __init__(self):
        super(StaticLibraryDemo, self).__init__()
        
        self.name = 'example/staticlib-demo/liby.a'
        
        self.cxxflags = ['-g']                          # 编译参数
        self.incs = []                                  # 头文件搜索路径
        self.srcs = ['example/staticlib-demo/y.cpp']    # 源文件列表
```

enjoy it!