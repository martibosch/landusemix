# Package dependencies

- Install (for your operating system) **Python 2.7**
```sh
sudo apt-get install g++ build-essential python2.7-dev python-pip python-matplotlib
```

- Create the virtual environment and install required dependencies
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
