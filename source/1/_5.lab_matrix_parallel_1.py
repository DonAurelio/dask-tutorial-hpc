#!/usr/bin/env python
# coding: utf-8

# ### Parallel programming approach: Domain decomposition (Dask Array)
# 
# _Hint: Copy useful code snippets from the notebook._

# __1. Import required libraries, define required variables and functions__
# 
# _Hint: Import dask.array, define shape and chunks_

# ...

shape = # ...


# __2. Create the first array__ using `Dask Array` and perform domain decomposition. The `chucks` param tell Dask the size of the chuck that will be considered for the decomposition. 

# In[ ]:


x = # ...
x


# __3. Create the second array__ using `Dask Array` and perform domain decomposition. The `chucks` param tell Dask the size of the chuck that will be considered for the decomposition. 

# In[ ]:


y = # ...
y


# __3. Write the parallel version of the program__
# 
# *Hint: you just need to write the equation $z = x^2 + y^2$ in Python langauge*

# In[ ]:


z = # ...
z


# **4. Compute the result** of the equation
# 
# _Hint: Use `compute` on $z$._

# In[ ]:


get_ipython().run_cell_magic('time', '', '\n# ...\n')


# ### Parallel programming approach: Functional decomposition (Dask Delayed)
# 
# *Hint: Remember, you will need to adjust the code to be able to apply functional decomposition. You can copy useful code snippets from the intro notebook.*

# __1. Import required libraries, define required variables and functions__
# 
# _Hint: define the shape to be (1000,1000), define `squared`, `add`, `subtract`, and `mult` functions to replace `**`, `+`, `-` and `*`_

# In[ ]:


import numpy as np
import dask

shape = # ...

# ...

# ...

# ...

# ...


# __2. Create arrays__

# In[ ]:


x = np.ones(shape=shape)
y = np.ones(shape=shape)


# __3. Write the equation in terms of functions__
# 
# _Hint: you just need to write the equation $z = x^2 + y^2$ in Python langauge, but using `squared`, `add`, `substract`, and `mult` functions in place of `**`, `+`, `-` and `*`. It will be easier if you assign the result of a function to a new variable, for example: `a`, `b`, `c`, ..._

# In[ ]:


get_ipython().run_cell_magic('time', '', '\na = # ...\nb = # ... \nc = # ...\nd = # ...\ne = # ...\ne\n')


# __4. Parallelize the previous program__ using Dask Delayed.

# In[ ]:


get_ipython().run_cell_magic('time', '', '\na = # ...\nb = # ... \nc = # ...\nd = # ...\ne = # ...\ne\n')


# __5. Visualize the parallel computation__ to be performed.

# In[ ]:


e.visualize()


# __6. Execute the computation__
# 
# _Questions: wondering why we need to use `compute` in Dask? Ask the speaker._

# In[ ]:


get_ipython().run_cell_magic('time', '', '\ne.compute()\n')

