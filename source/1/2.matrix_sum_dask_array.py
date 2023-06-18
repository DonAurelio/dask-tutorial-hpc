#!/usr/bin/env python
# coding: utf-8

# __1. Import required libraries, define required variables and functions__
import dask.array as da
import sys

shape = (10000,10000)
chunks = (100,100)

# __2. Create the arrays using `Dask Array` and perform domain decomposition. The `chucks` param tell Dask the size of the chuck that will be considered for the decomposition__ 

x = da.ones(shape=shape, chunks=chunks)
y = da.ones(shape=shape, chunks=chunks)

# __3. Write the parallel version of the program__

z = (x**2) + (y**2)

# __4. Compute the result of the equation using `compute` on $z$__

z.compute()

print(f"Size of X {sys.getsizeof(x) / 1000000000} GB")
print(f"Size of Y {sys.getsizeof(y) / 1000000000} GB")
