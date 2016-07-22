# Package dependencies

- Install (for your operating system) **Python 2.7**, Spatialite and GDAL
```sh
sudo apt-get install python2.7-dev g++ build-essential python-pip python-matplotlib libspatialite-dev spatialite-bin gdal-bin
```

- Check that GDAL insallation supports SQLite, using the following command:
```sh
ogr2ogr --formats | grep SQLite
```
Otherwise, manually install GDAL with spatialite support:
```sh
svn co http://svn.osgeo.org/gdal/trunk/gdal 
cd gdal
./configure --with-spatialite=yes
make
sudo make install
```

- Install a virtual environment
```sh
pip install virtualenvwrapper
echo export WORKON_HOME=$HOME/.virtualenvs >>~/.bashrc
echo export PROJECT_HOME=$HOME/urbansprawl >>~/.bashrc
echo source /usr/local/bin/virtualenvwrapper.sh >>~/.bashrc
source ~/.bashrc
```

- Create the virtual environment
```sh
mkvirtualenv --python=`which python2.7` urbansprawl
workon urbansprawl
pip install --upgrade pip
pip install --upgrade setuptools
pip install -r requirements.txt
```

- Work on the **urbansprawl** environment `workon urbansprawl` (and use `deactivate` to exit)

- Enjoy!
