# Planbox

[![Build Status](https://travis-ci.org/openplans/planbox.png?branch=staging)](https://travis-ci.org/openplans/planbox)
[![Requirements Status](https://requires.io/github/openplans/planbox/requirements.png?branch=staging)](https://requires.io/github/openplans/planbox/requirements/?branch=staging)

Planbox is a platform for getting the word out about your planning projects.
Its beautiful and easy to use interface will help you get your project online
in no time.

## Features

* Create project
* Quickly and easily edit details
* Timeline of progress


## Requirements

Describe the technology stack and any dependencies.

## Local Setup

### Clone this repo

    git clone git@github.com:openplans/planbox.git

### Install dependencies

     cd planbox
     virtualenv env
     source env/bin/activate
     pip install -r requirements.txt
     bower install
     cp src/planbox/local_settings.py.template src/planbox/local_settings.py

### Start your local server

     src/manage.py runserver


## Deploy to Heroku

### Create the app

1. Create a Heroku app for your Hatch git repo `heroku apps:create my-app-name`
2. Make sure you add the following Heroku Add-ons
  * Postgresql
  * Rediscloud (or your favorite Redis add-on)
  * Heroku Scheduler

### Next thing

TBD


## Supported Browsers

### Desktop
* Chrome (latest)
* Firefox (latest)
* Safari (latest)
* Internet Explorer (8-10)

### Mobile
* IOS Safari 6+
* Android Browser 4+
* Chrome


## Google Analytics configuration

Planbox stores the request domain information using two additional variables
(dimensions):

* Dimension 1 : Domain
* Dimension 2 : Root Path

Refer to the Google Analytics documentation on [setting up custom dimensions](https://developers.google.com/analytics/devguides/platform/customdimsmets)
to configure your account appropriately.


## Copyright

Copyright (c) 2014 OpenPlans
