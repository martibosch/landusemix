## Package dependencies
Recommended to use `conda` as Python environment and package manager

1. Install (for your operating system) the **Python 2.7** version of *either*:
    * **Anaconda** (https://www.continuum.io/downloads) if you have 600MB of free disk space and don't mind installing a large distribution of Python Data Analytics packages, *or*
    * **Miniconda** (http://conda.pydata.org/miniconda.html) if you want to install manually the packages
    **Important Notes:**
        * Do NOT install as super user
        * If installing in Linux: select `yes` when asked to prepend the install location to your `PATH` in your bash config (i.e. `~/.bashrc`)
        * To have tab autocompletion in the terminal, do `echo 'eval "$(register-python-argcomplete conda)'" >> ~/.bashrc` (or change `~/.bashrc` for your bash config file)
        
    See http://conda.pydata.org/docs/installation.html for more information about the installation.

2. Use `conda env create -f environment.yml` to replicate the virtual environment **urbansprawl**

3. Work on the **urbansprawl** environment `source activate urbansprawl` (and use `deactivate urbansprawl` to exit)

4. Enjoy!
