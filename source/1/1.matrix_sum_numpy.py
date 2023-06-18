#!/usr/bin/env python
# coding: utf-8

# __1. Import required libraries, define required variables and functions__
import numpy as np 
import sys

# Size of the array
shape = (10,10)

# __2. Create arrays__
x = np.ones(shape=shape)
y = np.ones(shape=shape)

# __2. Write the sequential program to find the value of $z$__
z = (x**2) + (y**2)

print(f"Size of X {sys.getsizeof(x) / 1000000000} GB")
print(f"Size of Y {sys.getsizeof(y) / 1000000000} GB")
print(f"Size of Z {sys.getsizeof(z) / 1000000000} GB")
print("Result")
print(z)