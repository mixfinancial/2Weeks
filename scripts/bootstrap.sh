#!/bin/bash

user1='{"email": "davidlarrimore@gmail.com", "first_name": "David", "last_name": "Larrimore", "password": "null", "username": "davidlarrimore@gmail.com"}'
user2='{"email": "blarrimore5@gmail.com", "first_name": "Barbara", "last_name": "Larrimore", "password": "null", "username": "blarrimore5@gmail.com"}'


#curl http://localhost:5000/api/users -d "data= $user1" -X POST
#curl http://localhost:5000/api/users -d "data= $user2" -X POST



user2='{"email": "blarrimore6@gmail.com", "first_name": "Ronald", "last_name": "Larrimore", "password": "null", "username": "blarrimore5@gmail.com"}'

#curl http://localhost:5000/api/user/1 -d "data= $user2" -X PUT

curl http://localhost:5000/api/user/1 -X DELETE