<a href="https://www.dask.org/">
<img src="http://dask.readthedocs.io/en/latest/_images/dask_horizontal.svg"
     align="right"
     width="30%"
     alt="Dask logo\">
</a>

# Dask Fundamentals Tutorial for High Performance Computing 

Dask is an open-source Python library for parallel/distributed computing. 

* This tutorial explains two fundamental problem paralleization concepts: **domain decomposition** and **functional decomposition**. 
* It exemplifies how these two concepts can be achieved using Dask. 
* It exemplifies how Dask enable parallel computing/distributed, out-of-core computations and scalability (from a local machine to cloud computing systems)

__This tutorial start at__ [0.Introduction](0.Introduction.ipynb).

__Run this tutorial using your own machine__

* Create a virtual enviroment using `conda` or `pip`.
* Install the `requirements.txt`
* Run the jupyterlab enviroment.

__Run this tutorial using Vagrant__

[Vagrant](https://developer.hashicorp.com/vagrant/tutorials/getting-started) automates the deployment of virtual machines. The `Vagrantfile` defines a ready to use jupyterlab virtual machine for this tutorial. Use the following commands to deploy the machine.

Install vagrant

```sh
sudo apt update
sudo apt install virtualbox
sudo apt install vagrant
``` 

Provision the virtual machine

```sh
vagrant up
```

Get into the virtual machine

```sh
vagrant ssh
```

Stop the virtual machine

```sh
vagrant ssh
```

Destroy the virtual machine

```sh
vagrant ssh
```

Use the following url to access the jupyterlab enviroment.

http://192.168.33.10:8000

__This tutorial was presented in__

1. [HPCSS2023: Colombian HPC Summer School 2023, June 20 - 22, 2023](https://cybercolombia.org/summer_school_6/).
2. [CARLA2023: Latin American High Performance Computing Conference, September 18 - 22](https://www.carla2023.org/en/schedule/tutorial/232)

## Acknowledgements

* This project is partially supported by CyberColombia
* We thank [Chameleon Cloud](https://www.chameleoncloud.org/) for its support in compute time.
* We thank [Coiled](https://www.coiled.io/) for their technical support and compute time provided on their ready-to-use Dask Cloud Computing Platform.
* We thank [Naty Clementi](https://github.com/ncclementi) from Coiled for her support and suggestions to improve this tutorial.
* We thank [Alfonso Ladino](https://github.com/aladinor) for extending this tutorial to include an example of processing Zaar analysis-ready radar data by streaming it from the cloud and processing it on an HPC system.
