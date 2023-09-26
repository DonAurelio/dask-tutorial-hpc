#!/usr/bin/env python
# coding: utf-8

# __1. Import required libraries, define required variables and functions__

import numpy as np
import dask

shape = (1000,1000)

def create_array():
    return [ [1 for x in range(0,shape[0])] for y in range(0,shape[1]) ]

def square(a):
    # __1. Square array (element-wise)__
    return [ [ (a[x][y]**2) for x in range(0,shape[0])] for y in range(0,shape[1]) ]

def add(a,b):
    # __1. Addition (element-wise)__
    return [ [ (a[x][y] + b[x][y]) for x in range(0,shape[0])] for y in range(0,shape[1]) ]

# __2. Parallelize the previous program__ using Dask Delayed.

x = dask.delayed(create_array)()
y = dask.delayed(create_array)()
a = dask.delayed(square)(x)
b = dask.delayed(square)(y)
c = dask.delayed(add)(a,b)

# __3. Execute the computation__
# c.compute(scheduler='threads')
# c.compute(scheduler='processes')
c.compute()
