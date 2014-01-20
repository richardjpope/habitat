**NOTE: This is a very early stage work in progress. If you install it, you will probably be disapointed.**

Habitat is an external brain. It runs on a raspberry pi. It does things in response to your interactions with your digital-physical environment using behavior-driven development style tests.

##Examples

```
Feature: Near a point in space
    Scenario: Near a point in space 
        When I am within 100 meters of "[0,0]"
        Then ping "http://example.com/tad-ah"
```

##Setting up a fresh Raspberry Pi with Habitat

1.  Setup headless server with Raspbarian + >= 16 GB SD card: http://www.penguintutor.com/linux/raspberrypi-headless

2. ssh into the server

    ```
    ssh pi@192.168.1.XX
    ```

3. Configure the Raspberry Pi by running  ```sudo raspi-config ```. Make the following changes:
    * 'Change user password'
    * 'Expand filesystem'
    * 'Overclock' set to *turbo*
    * 'Advanced' > 'Hostname' set to 'habitat'
    * 'Advanced' >  'Memory split' set to 16
    * If you are not in the UK, set the time zone

    Then reboot when you are asked to, and ssh in again.


4. Setup extra storage

    Insert a 64GB USB stick, and then mount it by running:

    ```
    sudo mkdir /mnt/storage1
    sudo mount -t vfat /dev/sda1 /mnt/storage1
    sudo su -c "echo '/dev/sda1  /mnt/storage1  ext3 rw,defaults 0 0' >> /etc/fstab"
    ```

5. Install mongodb (based on https://github.com/RickP/mongopi). 

    This will take **a very long time to compile**, so it is best to leave this step running over night and use the `screen` command incase your connection to the raspberry pi drops during the process.

    ```
    sudo apt-get install screen
    screen
    cd ~
    sudo apt-get install git-core build-essential scons libpcre++-dev xulrunner-dev libboost-dev libboost-program-options-dev libboost-thread-dev libboost-filesystem-dev
    git clone git://github.com/RickP/mongopi.git
    cd mongopi
    scons
    sudo scons --prefix=/opt/mongo install

    PATH=$PATH:/opt/mongo/bin/
    export PATH

    ```

6. Configure mongodb - create user, set data to be stored on USB stick, auto start.

    ```
    sudo useradd mongodb
    sudo mkdir /mnt/storage1/mongodb
    sudo chown mongodb:mongodb /mnt/storage1/mongodb
   
    sudo mkdir /etc/mongodb/
    sudo sh -c 'echo "dbpath=/mnt/storage1/mongodb" > /etc/mongodb/mongodb.conf'

    cd /etc/init.d
    sudo wget -O mongodb https://gist.github.com/memespring/b19734772f9f19fa2622/raw/12348660841dd2b33388d7b08c8328fa48b25e6e/mongodb.sh
    sudo chmod +x mongodb
    sudo update-rc.d mongodb defaults
    sudo service mongodb start

    ```

7. Install PIP package manager for python

    ```
    cd ~
    wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
    sudo python ez_setup.py
    rm ez_setup.py
    wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    sudo python get-pip.py
    rm get-pip.py
    ```

8. Install a few other things
    **TODO: setup STARTTLS for sendmail? **

    ```
    sudo apt-get install sendmail
    ```

9. Get the code

    **TODO: this should eventually pull from a specific release zip file ratehr than git, but this is easier for dev**

    ```
    cd ~
    git clone https://github.com/memespring/habitat.git
    ```

10. Install requirements

    ```
    cd ~/habitat
    sudo pip install -r requirements.txt
    ```

11. Create local config

    ```
    cd ~/habitat
    cp local_config.py.git local_config.py
    nano local_config.py
    ```

    And add a randoms tring of numbers and letters to the SECRET_KEY setting, and your email address to EMAIL_TO

12. Start running
    ```
    celery -A habitat.celery worker -B -l info
    python runserver.py
    ```

    Then visit http://habitat:5000

    **TODO: Eventually there needs to be something that starts these on reboot, but for dev it is easier to start manually**


##Seting up a development copy of habitat (i.e. if you want to contribute)

You will need to have the following already setup on your laptop:

- Python
- Pip
- virtualenv
- MongoDB
- git
- sendmail

###Setup

1. Make a directory and create a virtual environment

    ``` 
    mkdir habitat
    cd habitat
    virtualenv .
    ```

2. Grab the code

    ```
    git clone https://github.com/memespring/habitat.git
    ```

3. Enter virtual environment and install requirements

    ```
    source bin/activate
    pip install -r requirements.txt
    ```

### Running

1. Start Mongo DB (if it isnt already running):

    ```
    mongod
    ```

2. Enter virtual environment:

    ```
    source bin/activate
    ```

3. Start celery worker 

    ```
    celery -A habitat.celery worker -B -l info
    ```

4. Start app

    ```
    python runserver.py
    ```



----------------------

Ubuntu dev setup

sudo apt-get install python-setuptools
sudo apt-get install sendmail
sudo apt-get install spatialite-bin
sudo apt-get install python-pip
sudo pip install virtualenv
sudo apt-get install git
sudo apt-get install sqlite3
sudo apt-get install libpq-dev python-dev
sudo apt-get install libsqlite3-dev

Install GEOS, PROJ.4 and libspatialite as per geodjango instructions

[setup shared directory]
[setup a virtualenv in home directory]


pip install -r requirements.txt


Do the thing with sqlite3: https://docs.djangoproject.com/en/1.6/ref/contrib/gis/install/spatialite/