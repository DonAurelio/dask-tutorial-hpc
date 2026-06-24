#!/usr/bin/env python
# coding: utf-8

# __1. Import required libraries, define required variables and functions__

import dask

shape = (1000,1000)

def create_array():
    return [[1 for column in range(0, shape[1])] for row in range(0, shape[0])]

def square(a):
    # __1. Square array (element-wise)__
    return [[ (a[row][column]**2) for column in range(0, shape[1])] for row in range(0, shape[0]) ]

def add(a,b):
    # __1. Addition (element-wise)__
    return [[ (a[row][column] + b[row][column]) for column in range(0, shape[1])] for row in range(0, shape[0]) ]

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
