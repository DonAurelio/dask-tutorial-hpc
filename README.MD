<a href="https://www.dask.org/">
<img src="http://dask.readthedocs.io/en/latest/_images/dask_horizontal.svg"
     align="right"
     width="30%"
     alt="Dask logo\">
</a>

# Dask Fundamentals Tutorial for High Performance Computing 

Dask is an open-source Python library for parallel/distributed computing. 

* This tutorial explains fundamental problem paralleization concepts such as domain decomposition and functional decomposition. 
* It exemplifies how these two concepts can be achieved using Dask. 
* It exemplifies how Dask enable parallel computing/distributed, out-of-core computations and scalability (from a local machine to cloud computing systems)

# Run this tutorial using Vagrant

```sh
sudo apt update
sudo apt install virtualbox
sudo apt install vagrant
vagrant --version
``` 

# Run this tutorial using your own machine

* Create a virtual enviroment using `conda` or `pip`.
* Install the `requirements.txt`
* Run the jupyterlab enviroment.

# This tutorial was presented in

1. [HPCSS2023: Colombian HPC Summer School 2023, June 20 - 22, 2023](https://cybercolombia.org/summer_school_6/).

# Acknowledgements

* This project is partially supported by CyberColombia
* We thank [Chameleon Cloud](https://www.chameleoncloud.org/) for its support in compute time.
* We thank [Coiled](https://www.coiled.io/) for its support in compute time on in their ready-to-use Dask Cloud Computing Platform.
* We thank [Naty Clementi](https://github.com/ncclementi) from Coiled for her support and suggestions to improve this tutorial.
