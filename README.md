**NOTE: This is a very early stage work in progress. If you install it, you will probably be disapointed.**

Habitat is an external brain. It does things in response to your interactions with your digital-physical environment using behavior-driven development style tests.

##Examples

```
Feature: Near a point in space
    Scenario: Near a point in space
        When I am within 100 meters of "[0,0]"
        Then ping "http://example.com/tad-ah"
```

##Setup

1. Install mongodb
2. Install pip and virtualenv
2. Install bower
3. Clone this repository:

  ```
  git clone git@github.com:memespring/habitat.git
  ```

4. Setup virtual environment and install dependancies

    ```
    cd habitat
    virtualenv .
    source bin/activate
    pip install -r  requirements.txt
    bower install
    ```

## Running

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
