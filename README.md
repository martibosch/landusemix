## Package dependencies

1. Install (for your operating system) the **Python 2.7** version:

1.1 Python
sudo apt-get install python2.7-dev g++ build-essential python-pip python-matplotlib
1.2 Spatialite
sudo apt-get install libspatialite-dev libspatialite5 spatialite-bin
1.3 GDAL with Spatialite support
svn co http://svn.osgeo.org/gdal/trunk/gdal
cd gdal
./configure --with-spatialite=yes
make
sudo make install

2. Install a virtual environment:

#Recommended to use a virtual environment with python2.7
2.1 Install **virtualenvwrapper**
pip install virtualenvwrapper

2.2 Add the following to your bash profile (.bashrc, .profile...) and reload startup file i.e. 
echo export WORKON_HOME=$HOME/.virtualenvs >>~/.bashrc
echo export PROJECT_HOME=$HOME/urbansprawl >>~/.bashrc
echo source /usr/local/bin/virtualenvwrapper.sh >>~/.bashrc
source ~/.bashrc

2.3 Create virutal environment named urbansprawl with python3
mkvirtualenv --python=`which python2.7` urbansprawl

2.4 Work on the virtual environment and install the python dependencies (Upgrade pip and setuptools to avoid latter errors)
workon urbansprawl
pip install --upgrade pip
pip install --upgrade setuptools
# Install requirements
pip install -r requirements.txt

3. Work on the **urbansprawl** environment `workon urbansprawl` (and use `deactivate` to exit)

4. Enjoy!
