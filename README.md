# 2Weeks
Application to assist with bi-weekly budget planning and execution


### Installation
All required Python libraries can be installed by leveraging the included requirements.txt file.

    sudo pip install -r requirements.txt
    
    For Windows: http://stackoverflow.com/questions/30408340/python-django-installing-mysql-easy-install-and-pip-errors
   
   
Run newrelic-admin run-program python runserver.py

  
    
    
 ## Testing
 
 funtional_test.py
 Selenium -requires 
    https://code.google.com/p/selenium/wiki/ChromeDriver
    Using ChromeDriver
    -Robert
    python functional_test.py




## Notes for Robert since he can't remember
Ref. 1: https://www.digitalocean.com/community/tutorials/docker-explained-how-to-containerize-python-web-applications
Ref. 2: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-14-04
Ref. 3: https://medium.com/@rodkey/deploying-a-flask-application-on-aws-a72daba6bb80

1.    

2.  Setup the application to use uWSGI and talk with Nginx


Rebuild the Docker image process

1.  log in to docker base
2. 


Docker Cleaners 
Containers
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
Images
docker rmi $(docker images -q)




Deploying.  
1.  SSH into Dockerbase
2.  Build a new Docker container
3.  sudo docker build --rm -t 2weeks --no-cache .
4.  Run the container
5.  sudo docker run --name 2weeks_cnt -p 80:80 -i -t 2weeks:latest

5a. Check container
    sudo docker run -t -i 2weeks:latest /bin/bash


Setup of Webservice
Use Docker offical Nginx Docker Image
1.  docker run --name mynginx1 -P -d nginx

Nginx 

### PNOTIFY Info



1. [pNotify](http://sciactive.github.io/pnotify/)
2. [Angular JS Wrapper](https://github.com/jacqueslareau/angular-pnotify)







## API REFERENCE

The 2Weeks API was built based upon the [jsonapi.org](http://jsonapi.org/) specification.

All routes start with /api/


#### API Routes

Each Database object supports the following methods



#### GET (All)

**Method**: GET

**Route**: /api/object

**Optional URL Parameters**: Provide optional Key/Value pairs for search strings




#### GET (ONE)

**Method**: GET

**Route**: /api/object/:ObjectId

**Optional URL Parameters**: objectId




#### CREATE (ONE)

**Method**: POST

**Route**: /api/object

**Accept either** application/x-www-form-urlencoded or application/json



#### UPDATE (ONE)

**Method**: PUT

**Route**: /api/object/:ObjectId

**Optional URL Parameters**: objectId

**Accept either** application/x-www-form-urlencoded or application/json



#### DELETE (ONE)


**Method**: DELETE

**Route**: /api/object/:ObjectId

**Base URL Parameters**: objectId

**Optional URL Parameters**: objectId



### API Response Info


#### Successful Response with data example

    {
        "data": [
            {
                "amount": "100.0", 
                "average_amount": "None", 
                "date_created": null, 
                "description": "Wachovia", 
                "id": 1, 
                "last_updated": null, 
                "name": "Wachovia", 
                "next_due_date": null, 
                "payment_method": null, 
                "payment_type_ind": null, 
                "recurrance": null, 
                "recurring_flag": null, 
                "type": "bills", 
                "user_id": 4
            }
        ], 
        "meta": [
            {
                "authors": [
                    "David Larrimore", 
                    "Robert Donovan"
                ], 
                "copyright": "Copyright 2015 MixFin LLC.", 
                "version": "0.1"
            }
        ]
    }
    
    
#### Successful Resonpse with no results example
    
    {
      "data": null,
      "error": "Username or password incorrect",
      "meta": [
        {
          "authors": [
            "David Larrimore",
            "Robert Donovan"
          ],
          "copyright": "Copyright 2015 MixFin LLC.",
          "version": "0.1"
        }
      ]
    }
    
    
#### Error Resonpse
   
    {
        "data": [], 
        "meta": [
            {
                "authors": [
                    "David Larrimore", 
                    "Robert Donovan"
                ], 
                "copyright": "Copyright 2015 MixFin LLC.", 
                "version": "0.1"
            }
        ]
    }    