# 2Weeks
Application to assist with bi-weekly budget planning and execution


### Installation
All required Python libraries can be installed by leveraging the included requirements.txt file.

    sudo pip install -r requirements.txt
    
    
    
    
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
1.    

2.  Setup the application to use uWSGI and talk with Nginx



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