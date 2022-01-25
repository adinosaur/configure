# -*- coding=utf-8 -*-

from __main__ import Args

cflags = ['-g', '-std=c11', '-m64']
cxxflags = ['-g', '-std=c++11', '-m64']

if Args.type == 'release':
    cflags += ['-O2']
    cxxflags += ['-O2']

EXPORT = ['cflag', 'cxxflags']