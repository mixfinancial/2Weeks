#!/bin/bash

user1='{"email_address": "davidlarrimore@gmail.com", "first_name": "David", "last_name": "Larrimore", "password": "null", "username": "davidlarrimore@gmail.com"}'
user2='{"email_address": "blarrimore5@gmail.com", "first_name": "Barbara", "last_name": "Larrimore", "password": "null", "username": "blarrimore5@gmail.com"}'


curl http://localhost:5000/api/users/ -d "data= $user1" -X POST
curl http://localhost:5000/api/users/ -d "data= $user2" -X POST
#curl http://localhost:5000/api/users