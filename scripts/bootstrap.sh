#!/bin/bash

#user1='{"email": "davidlarrimore@gmail.com", "first_name": "David", "last_name": "Larrimore", "password": "null", "username": "davidlarrimore@gmail.com"}'
#user2='{"email": "blarrimore5@gmail.com", "first_name": "Barbara", "last_name": "Larrimore", "password": "null", "username": "blarrimore5@gmail.com"}'


#curl http://localhost:5000/api/users -d "data= $user1" -X POST
#curl http://localhost:5000/api/users -d "data= $user2" -X POST



#user2='{"username": "davidlarrimore@gmail.com", "password": "may1098"}'

#curl http://localhost:5000/api/user/ -d "data=$user2" -X POST

#curl http://localhost:5000/api/user/1 -X DELETE
auth='{"username":"xxxx", "password":"xxxx"}'
curl http://localhost:5000/auth -d '{"username": "davidlarrimore@gmail.com", "password": "may1098"}' -X POST -H "Content-Type: application/json"


bill1='{"user_id": "4", "name": "Test"}'
curl http://localhost:5000/api/bill -d "$bill1" -X POST -H "Content-Type: application/json"