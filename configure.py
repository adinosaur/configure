#!/usr/bin/python
# -*- coding=utf-8 -*-

import os
import re
import sys
import subprocess
import textwrap

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


Targets = []

# ======================================
# Config
# ======================================
BuildOutput = 'build'
CC = 'gcc'
CXX = 'g++'
AR = 'ar'

# ======================================
# NinjaWriter
# ======================================

"""Python module for generating .ninja files.
Note that this is emphatically not a required piece of Ninja; it's
just a helpful utility for build-file-generation systems that already
use Python.
"""

def escape_path(word):
    return word.replace('$ ', '$$ ').replace(' ', '$ ').replace(':', '$:')

class NinjaWriter(object):
    def __init__(self, output, width=144):
        self.output = output
        self.width = width

    def newline(self):
        self.output.write('\n')

    def comment(self, text):
        for line in textwrap.wrap(text, self.width - 2, break_long_words=False,
                                  break_on_hyphens=False):
            self.output.write('# ' + line + '\n')

    def variable(self, key, value, indent=0):
        if value is None:
            return
        if isinstance(value, list):
            value = ' '.join(filter(None, value))  # Filter out empty strings.
        self._line('%s = %s' % (key, value), indent)

    def pool(self, name, depth):
        self._line('pool %s' % name)
        self.variable('depth', depth, indent=1)

    def rule(self, name, command, description=None, depfile=None,
             generator=False, pool=None, restat=False, rspfile=None,
             rspfile_content=None, deps=None):
        self._line('rule %s' % name)
        self.variable('command', command, indent=1)
        if description:
            self.variable('description', description, indent=1)
        if depfile:
            self.variable('depfile', depfile, indent=1)
        if generator:
            self.variable('generator', '1', indent=1)
        if pool:
            self.variable('pool', pool, indent=1)
        if restat:
            self.variable('restat', '1', indent=1)
        if rspfile:
            self.variable('rspfile', rspfile, indent=1)
        if rspfile_content:
            self.variable('rspfile_content', rspfile_content, indent=1)
        if deps:
            self.variable('deps', deps, indent=1)

    def build(self, outputs, rule, inputs=None, implicit=None, order_only=None,
              variables=None, implicit_outputs=None, pool=None, dyndep=None):
        outputs = as_list(outputs)
        out_outputs = [escape_path(x) for x in outputs]
        all_inputs = [escape_path(x) for x in as_list(inputs)]

        if implicit:
            implicit = [escape_path(x) for x in as_list(implicit)]
            all_inputs.append('|')
            all_inputs.extend(implicit)
        if order_only:
            order_only = [escape_path(x) for x in as_list(order_only)]
            all_inputs.append('||')
            all_inputs.extend(order_only)
        if implicit_outputs:
            implicit_outputs = [escape_path(x)
                                for x in as_list(implicit_outputs)]
            out_outputs.append('|')
            out_outputs.extend(implicit_outputs)

        self._line('build %s: %s' % (' '.join(out_outputs),
                                     ' '.join([rule] + all_inputs)))
        if pool is not None:
            self._line('  pool = %s' % pool)
        if dyndep is not None:
            self._line('  dyndep = %s' % dyndep)

        if variables:
            if isinstance(variables, dict):
                iterator = iter(variables.items())
            else:
                iterator = iter(variables)

            for key, val in iterator:
                self.variable(key, val, indent=1)

        return outputs

    def include(self, path):
        self._line('include %s' % path)

    def subninja(self, path):
        self._line('subninja %s' % path)

    def default(self, paths):
        self._line('default %s' % ' '.join(as_list(paths)))

    def _count_dollars_before_index(self, s, i):
        """Returns the number of '$' characters right in front of s[i]."""
        dollar_count = 0
        dollar_index = i - 1
        while dollar_index > 0 and s[dollar_index] == '$':
            dollar_count += 1
            dollar_index -= 1
        return dollar_count

    def _line(self, text, indent=0):
        """Write 'text' word-wrapped at self.width characters."""
        leading_space = '  ' * indent
        while len(leading_space) + len(text) > self.width:
            # The text is too wide; wrap if possible.

            # Find the rightmost space that would obey our width constraint and
            # that's not an escaped space.
            available_space = self.width - len(leading_space) - len(' $')
            space = available_space
            while True:
                space = text.rfind(' ', 0, space)
                if (space < 0 or
                    self._count_dollars_before_index(text, space) % 2 == 0):
                    break

            if space < 0:
                # No such space; just use the first unescaped space we can find.
                space = available_space - 1
                while True:
                    space = text.find(' ', space + 1)
                    if (space < 0 or
                        self._count_dollars_before_index(text, space) % 2 == 0):
                        break
            if space < 0:
                # Give up on breaking.
                break

            self.output.write(leading_space + text[0:space] + ' $\n')
            text = text[space+1:]

            # Subsequent lines are continuations, so indent them.
            leading_space = '  ' * (indent+2)

        self.output.write(leading_space + text + '\n')

    def close(self):
        self.output.close()


def as_list(input):
    if input is None:
        return []
    if isinstance(input, list):
        return input
    return [input]


def escape(string):
    """Escape a string such that it can be embedded into a Ninja file without
    further interpretation."""
    assert '\n' not in string, 'Ninja syntax does not allow newlines'
    # We only have one special metacharacter: '$'.
    return string.replace('$', '$$')


def expand(string, vars, local_vars={}):
    """Expand a string containing $vars as Ninja would.
    Note: doesn't handle the full Ninja variable syntax, but it's enough
    to make configure.py's use of it work.
    """
    def exp(m):
        var = m.group(1)
        if var == '$':
            return '$'
        return local_vars.get(var, vars.get(var, ''))
    return re.sub(r'\$(\$|\w*)', exp, string)

# ======================================
# CxxTarget
# ======================================
class CxxTarget(object):
    def __init__(self):
        super(CxxTarget, self).__init__()

        self.name = None
        self.cxxflags = []  # 编译参数
        self.incs = []      # 头文件搜索路径
        self.src = None     # 源文件
    
    @classmethod
    def generate_ninja_rule(cls, writer):
        writer.rule('cxx', '{cxx} -o $out -c $in -MMD -MF $in.d $cxxflags $incs'.format(cxx=CXX), description='CXX $in', depfile='$in.d', deps='gcc')
        writer.newline()

    def generate_ninja_build(self, writer):
        target = self.name
        cxxflags = ' '.join(self.cxxflags)
        incs = ' '.join(['-I' + inc for inc in self.incs])
        writer.comment('=== build cxx target: {target} ==='.format(target=target))
        writer.build(target, 'cxx', inputs=self.src, variables={'cxxflags':cxxflags, 'incs':incs})
        writer.newline()

# ======================================
# LinkTarget
# ======================================
class LinkTarget(object):
    def __init__(self):
        super(LinkTarget, self).__init__()

        self.name = None
        self.deps = []      # 链接的依赖文件
        self.ldflags = []   # 链接的参数
        self.libs = []      # 链接的库文件
        self.objs = []      # 链接的objects
    
    @classmethod
    def generate_ninja_rule(cls, writer):
        writer.rule('link', '{cxx} -o $out $in $libs $ldflags'.format(cxx=CXX), description='LINK $out')
        writer.newline()
    
    def generate_ninja_build(self, writer):
        target = self.name
        ldflags = ' '.join(self.ldflags)
        inputs = self.objs + self.libs
        writer.comment('=== build link target: {target} ==='.format(target=target))
        writer.build(target, 'link', inputs=inputs, variables={'ldflags':ldflags})
        writer.newline()

# ======================================
# ArchivesTarget
# ======================================
class ArchivesTarget(object):
    def __init__(self):
        super(ArchivesTarget, self).__init__()

        self.name = None
        self.objs = []      # 归档的objects
    
    @classmethod
    def generate_ninja_rule(cls, writer):
        writer.rule('ar', '{ar} rcs $out $in'.format(ar=AR), description='AR $out')
        writer.newline()
    
    def generate_ninja_build(self, writer):
        target = self.name
        writer.comment('=== build ar target: {target} ==='.format(target=target))
        writer.build(target, 'ar', inputs=self.objs)
        writer.newline()

# ======================================
# Exe Target
# ======================================
class ExeTarget(object):
    def __init__(self):
        super(ExeTarget, self).__init__()
        Targets.append(self)

        self.name = None
        self.cxxflags = []  # 编译参数
        self.incs = []      # 头文件搜索路径
        self.srcs = []      # 源文件列表

        self.deps = []      # 链接的依赖文件
        self.ldflags = []   # 链接的参数
        self.libs = []      # 链接的库文件

    def generate_ninja_build(self, writer):
        objs = []
        for src in self.srcs:
            cxx_target = CxxTarget()
            cxx_target.name = os.path.join(BuildOutput, src) + '.o'
            cxx_target.cxxflags = self.cxxflags
            cxx_target.incs = self.incs
            cxx_target.src = src
            cxx_target.generate_ninja_build(writer)
            objs.append(cxx_target.name)
        
        link_target = LinkTarget()
        link_target.name = os.path.join(BuildOutput, self.name)
        link_target.deps = self.deps
        link_target.ldflags = self.ldflags
        link_target.libs = self.libs
        link_target.objs = objs
        link_target.generate_ninja_build(writer)

# ======================================
# Shared Library Target
# ======================================
class SharedLibraryTarget(object):
    def __init__(self):
        super(SharedLibraryTarget, self).__init__()
        Targets.append(self)

        self.name = None
        self.cxxflags = []  # 编译参数
        self.incs = []      # 头文件搜索路径
        self.srcs = []      # 源文件列表

        self.deps = []      # 链接的依赖文件
        self.ldflags = []   # 链接的参数
        self.libs = []      # 链接的库文件
    
    def generate_ninja_build(self, writer):
        objs = []
        for src in self.srcs:
            cxx_target = CxxTarget()
            cxx_target.name = os.path.join(BuildOutput, src) + '.o'
            cxx_target.cxxflags = self.cxxflags
            cxx_target.incs = self.incs
            cxx_target.src = src
            cxx_target.generate_ninja_build(writer)
            objs.append(cxx_target.name)
        
        link_target = LinkTarget()
        link_target.name = os.path.join(BuildOutput, self.name)
        link_target.deps = self.deps
        link_target.ldflags = ['-shared'] + self.ldflags
        link_target.libs = self.libs
        link_target.objs = objs
        link_target.generate_ninja_build(writer)

# ======================================
# Static Library Target
# ======================================
class StaticLibraryTarget(object):
    def __init__(self):
        super(StaticLibraryTarget, self).__init__()
        Targets.append(self)

        self.name = None
        self.cxxflags = []  # 编译参数
        self.incs = []      # 头文件搜索路径
        self.srcs = []      # 源文件列表
    
    def generate_ninja_build(self, writer):
        objs = []
        for src in self.srcs:
            cxx_target = CxxTarget()
            cxx_target.name = os.path.join(BuildOutput, src) + '.o'
            cxx_target.cxxflags = self.cxxflags
            cxx_target.incs = self.incs
            cxx_target.src = src
            cxx_target.generate_ninja_build(writer)
            objs.append(cxx_target.name)
        
        archives_target = ArchivesTarget()
        archives_target.name = os.path.join(BuildOutput, self.name)
        archives_target.objs = objs
        archives_target.generate_ninja_build(writer)

# ======================================
# Load module
# ======================================
def __load_module(module_name, file_path):
    try:
        import importlib.machinery
        loader = importlib.machinery.SourceFileLoader(module_name, file_path)
        return loader.load_module()

    except ImportError:
        import imp
        return imp.load_source(module_name, file_path)
    
    return None

# ======================================
# Main
# ======================================
def main():

    # load BUILD.py
    targets_cnt = 0
    for path, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file == 'BUILD.py':
                targets_cnt += 1
                module_name = '__build_target%s' % targets_cnt
                file_path = os.path.join(path, file)
                __load_module(module_name, file_path)

    # generate ninja
    out = StringIO()
    writer = NinjaWriter(out)
    writer.comment('build.nija generated by configure.py')
    writer.newline()

    # generate rules
    CxxTarget.generate_ninja_rule(writer)
    LinkTarget.generate_ninja_rule(writer)
    ArchivesTarget.generate_ninja_rule(writer)

    # generate builds
    for target in Targets:
        target.generate_ninja_build(writer)

    # write to build.ninja
    with open('build.ninja', 'w+') as f:
        f.write(out.getvalue())
    
    out.close()

    # run ninja
    p = subprocess.Popen('ninja/ninja-linux/ninja', shell=True)
    p.communicate()
    return p.returncode


if __name__ == '__main__':
    sys.exit(main())