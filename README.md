**NOTE: This is at a very early stage work in progress. If you install it, you will probably be disapointed.**

Habitat is an external brain. It runs on a raspberry pi. It does things in response to your interactions with your digital-physical environment using behavior-driven development style tests.

##Examples

	Feature: Near a point in space
	    Scenario: Near a point in space 
	        When I am within 100 meters of "[0,0]"
	        Then ping "http://example.com/tad-ah"

##Setting up a fresh Raspberry Pi with Habitat

* Setup headless server with Raspbarian: http://www.penguintutor.com/linux/raspberrypi-headless

* ssh into the server

	ssh pi@192.168.1.XX
	

* Install and configure mongodb (based on https://github.com/RickP/mongopi). 

This will take **a very long time to compile**, so it is best to leave this step running over night and use the `screen` command incase your connection to the raspberry pi drops during the process.


	screen
	cd ~
	sudo apt-get install git-core build-essential scons libpcre++-dev xulrunner-dev libboost-dev libboost-program-options-dev libboost-thread-dev libboost-filesystem-dev
	git clone git://github.com/RickP/mongopi.git
	cd mongopi
	scons
	sudo scons --prefix=/opt/mongo install

* Install PIP package manager for python

	cd ~
	wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
	sudo python get-pip.py
	rm get-pip.py
	sudo pip install setuptools --no-use-wheel --upgrade

* Get the code

	wget 'https://github.com/memespring/habitat/archive/master.zip'
	unzip master.zip
	mv habitat-master habitat
	rm master.zip

* Install requirements

	cd ~/habitat
	sudo pip install -r habitat/requirements.txt


**TODO: document how to start everything running**


##Seting up a development copy of habitat (i.e. if you want to contribute)

You will need to have the following already setup on your laptop:

- Python
- Pip
- virtualenv
- MongoDB
- git

###Setup

* Make a directory and create a virtual environment
	
	mkdir habitat
	cd habitat
	virtualenv .

* Grab the code

	git clone https://github.com/memespring/habitat.git

* Enter virtual environment and install requirements

	source bin/activate
	pip install -r requirements.txt

### Running

* Start Mongo DB (if it isnt already running):

	mongod

* Enter virtual environment:

	source bin/activate

* Start celery worker 
	celery -A habitat.celery worker -B -l info

* Start app

	python runserver.py

