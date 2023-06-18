#!/usr/bin/env python
# coding: utf-8

# ### Parallel programming approach: Domain decomposition (Dask Array)
# 
# *Hint: Copy useful code snippets from the notebook.*

# __1. Import required libraries, define required variables and functions__
# 
# _Hint: Import dask.array, define shape and chunks_

# ...

shape = # ...

# __2. Create the arrays using `Dask Array` and perform domain decomposition__

x = # ...
y = # ...

# __3. Write the equation for find the value of $z = (x^2 + y^2) * (x^2 - y^2)$__

z = # ...

# __4. Compute the result of the equation__
# 
# _Hint: Use `compute` on $z$._

# ...

print(f"Size of X {sys.getsizeof(x) / 1000000000} GB")
print(f"Size of Y {sys.getsizeof(y) / 1000000000} GB")
print(f"Size of Z {sys.getsizeof(z) / 1000000000} GB")
