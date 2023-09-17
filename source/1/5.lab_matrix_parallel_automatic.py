#!/usr/bin/env python
# coding: utf-8

# ### Parallel programming approach: Automatic parallelization
# 
# _Hint: Copy useful code snippets from the notebook._

# __1. Import required libraries, define required variables and functions__
import numpy as np 
import sys

# Size of the array
shape = (1000,1000)

# __2. Create arrays using Numpy__

x = # ...
y = # ...

# __2. Write the sequential program to find the value of $z$__

z = # ...

print(f"Size of X {sys.getsizeof(x) / 1000000000} GB")
print(f"Size of Y {sys.getsizeof(y) / 1000000000} GB")
print(f"Size of Z {sys.getsizeof(z) / 1000000000} GB")
