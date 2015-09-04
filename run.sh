#!/bin/bash

export APP_SETTINGS='config.DevelopmentConfig'
export DATABASE_URL='mysql://twoweeks:twoweeks@mixfindb.c6uo5ewdeq5k.us-east-1.rds.amazonaws.com:3306/twoweeks'
export NEW_RELIC_CONFIG_FILE='newrelic.ini'

newrelic-admin run-program python twoweeks.py