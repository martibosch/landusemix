## Package dependencies

1. Install (for your operating system) **Python 2.7**, Spatialite and GDAL

sudo apt-get install python2.7-dev g++ build-essential python-pip python-matplotlib

sudo apt-get install libspatialite-dev libspatialite5 spatialite-bin

svn co http://svn.osgeo.org/gdal/trunk/gdal

cd gdal

./configure --with-spatialite=yes

make

sudo make install

2. Install a virtual environment

pip install virtualenvwrapper

echo export WORKON_HOME=$HOME/.virtualenvs >>~/.bashrc

echo export PROJECT_HOME=$HOME/urbansprawl >>~/.bashrc

echo source /usr/local/bin/virtualenvwrapper.sh >>~/.bashrc

source ~/.bashrc

3. Create the virtual environment

mkvirtualenv --python=`which python2.7` urbansprawl

workon urbansprawl

pip install --upgrade pip

pip install --upgrade setuptools

pip install -r requirements.txt

4. Work on the **urbansprawl** environment `workon urbansprawl` (and use `deactivate` to exit)

5. Enjoy!
