#!/bin/bash

export APP_SETTINGS="config.DevelopmentConfig"
export DATABASE_URL='mysql://twoweeks:twoweeks@mixfindb.c6uo5ewdeq5k.us-east-1.rds.amazonaws.com:3306/twoweeks'


python twoweeks.py