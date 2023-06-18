#!/usr/bin/env python
# coding: utf-8

# __1. Import required libraries, define required variables and functions__

import numpy as np
import dask

shape = (10000,10000)

def squared(a):
    return a**2

def add(a,b):
    return a + b

# __2. Create arrays__

x = np.ones(shape=shape)
y = np.ones(shape=shape)

# __3. Write the equation in terms of functions__

a = squared(x)
b = squared(y)
c = add(a,b)

# __4. Parallelize the previous program__ using Dask Delayed.

a = dask.delayed(squared)(x)
b = dask.delayed(squared)(y)
c = dask.delayed(add)(a,b)

# __5. Execute the computation__

c.compute()
