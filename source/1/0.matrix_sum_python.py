#!/usr/bin/env python
# coding: utf-8

# __1. Import required libraries, define required variables and functions__
import numpy as np 
import sys

# Size of the array
shape = (10000,10000)

# __2. Create arrays, list of lists__
x = [ [1 for x in range(0,shape[0])] for y in range(0,shape[1]) ]
y = [ [1 for x in range(0,shape[0])] for y in range(0,shape[1]) ]
z = [ [0 for x in range(0,shape[0])] for y in range(0,shape[1]) ]

# __2. Write the sequential program to find the value of $z$__
for i in range(0,shape[0]):
    for j in range(0,shape[1]):
        z[i][j] = x[i][j]**2 + y[i][j]**2

print(f"Size of X {sys.getsizeof(x) / 1000000000} GB")
print(f"Size of Y {sys.getsizeof(y) / 1000000000} GB")
print(f"Size of Z {sys.getsizeof(z) / 1000000000} GB")
