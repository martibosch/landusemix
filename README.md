# Package dependencies

- Install (for your operating system) **Python 2.7**, **Spatialite** and **GDAL**
```sh
sudo apt-add-repository ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update
sudo apt-get install g++ build-essential python2.7-dev python-pip python-matplotlib libspatialite-dev spatialite-bin gdal-bin python-gdal libgdal-dev libfreetype6-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
```

- Create the virtual environment and install required dependencies (Gdal installed binaries and python version must match)
```sh
pip install virtualenvwrapper
echo export WORKON_HOME=$HOME/.virtualenvs >>~/.bashrc
echo export PROJECT_HOME=$HOME/urbansprawl >>~/.bashrc
echo source `which virtualenvwrapper.sh` >>~/.bashrc
source ~/.bashrc
mkvirtualenv --python=`which python2.7` landusemix
workon landusemix
pip install -r requirements.txt
```

- Work on the **landusemix** environment `workon landusemix` (and use `deactivate` to exit)

- Enjoy!
