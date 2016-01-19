'use strict';

var loginApp = angular.module('loginApp', [
    'ngRoute',
    'loginAppControllers',
    'loginServices',
    'dbServices',
    'formly',
    'formlyBootstrap',
    'ngToast'
]);



loginApp.config(['$routeProvider','ngToastProvider', function($routeProvider, ngToastProvider) {
    $routeProvider.
    when('/', {
        templateUrl: '/static/partials/Login-LoginForm.html',
        controller: 'loginAppLoginController'
    }).
    when('/recover_password/', {
        templateUrl: '/static/partials/recover_password.html',
        controller: 'recoverPasswordController'
    }).
    when('/recover_password', {
        templateUrl: '/static/partials/recover_password.html',
        controller: 'recoverPasswordController'
    }).
    otherwise({
        templateUrl: '/static/partials/Login-LoginForm.html',
        controller: 'loginAppLoginController'
    });




    ngToastProvider.configure({
        animation: 'fade',
        dismissButton: 'true',
        verticalPosition: 'bottom',
        horizontalPosition: 'left'
    });
}]);




/*********************
*  Database Services *
**********************/

var dbServices = angular.module('dbServices', ['ngResource']);

dbServices.factory('Me', ['$resource',
  function($resource){
    return $resource('/api/me/:userId', {}, {
      'query': {method:'GET', isArray:false},
      'get': {method:'GET', params:{userId:'users'}, isArray:false},
      'update': {method:'PUT', isArray:false},
      'register': {method:'POST', isArray:false}
    });
  }]);


/******************
*  Login Services *
******************/

var loginServices = angular.module('loginServices', ['ngResource']);

loginServices.factory('Login', ['$resource',
  function($resource){
    return $resource('/api/login/', {}, {
      'save': {method:'POST', isArray:false}
    });
  }]);

loginServices.factory('LoginCheck', ['$resource',
  function($resource){
    return $resource('/api/login_check/', {}, {
      'get': {method:'GET', isArray:false}
    });
  }]);

loginServices.factory('RecoverPassword', ['$resource',
  function($resource){
    return $resource('/api/recover_password/:email_address', {}, {
      'create': {method:'POST', isArray:false},
      'update': {method:'PUT', isArray:false}
    });
  }]);






var loginAppControllers = angular.module("loginAppControllers", []);

/*******************
* LOGIN CONTROLLER *
*******************/
loginAppControllers.controller("loginAppLoginController",['$scope', '$location', 'Login', 'ngToast', 'LoginCheck', '$routeParams', 'Me', 'RecoverPassword', function($scope, $location, Login, ngToast, LoginCheck, $routeParams, Me, RecoverPassword) {

    var location = '';
    $scope.title = '';
    $scope.disableRegister = false;
    $scope.sectionFlag = 'login';


    /*This section checks for url parameters
    * If URL parameters are found, it sees if the "auth_check" variable is set to true.
    * If "auth_check" is set to true, it forces the login screen to show
    * URL parameters are tacked on to the end of the login redirect
    */
    var searchObject = $location.search();
    if (searchObject != null){
        console.log('~~~URL Parameters~~~');
        console.log(searchObject);
        if (searchObject.auth_check != null && searchObject.auth_check == "true"){
            searchObject.auth_check = true;
            $scope.disableRegister = true;
        }else{
            searchObject.auth_check = false;
        }
    }


    //This logic sets what shows...either login or Register
    //as well as where the user will be logged into (Admin/Main Site)
    if($location.absUrl().indexOf("admin") > -1){
        console.log("Admin Home");
        location = "/admin";
        $scope.disableRegister = true;
        $scope.sectionFlag = 'login';
    }else{
        console.log("Main Home");

        //MAIN LOGIC FOR SWITCHING APP
        if(searchObject.action != null){
            if(searchObject.action == 'login'){
                $scope.title = "Login";
                $scope.sectionFlag = 'login';
            }else if(searchObject.action == 'recover_password_form'){
                $scope.title = "Recover Password";
                $scope.sectionFlag = 'recover_password_form';
            }else if(searchObject.action == 'recover_password'){
                $location.path(searchObject.action);
            }else{
                $scope.title = "Register new account";
                $scope.sectionFlag = 'register';
            }
        }else if(searchObject.auth_check != null && searchObject.auth_check){
            console.log('setting sectionFlag as login');
            $scope.sectionFlag = 'login';
            $scope.title = "Please login first";
        }else{
            $scope.title = "Register new account";
            $scope.sectionFlag = 'register';
        }
    }


    $scope.uPayRecurrenceSelectOptions = uPayRecurrenceSelectOptions;


    //This function switches from register to login and vice versa
    $scope.switchSection = function(){
        if($scope.sectionFlag == 'register'){
            $scope.title = "Login";
            $scope.sectionFlag = 'login';
        }else{
            $scope.title = "Register new account";
            $scope.sectionFlag = 'register';
        }
    }


    //This simple function auto-logs in users
    LoginCheck.get(function(data) {
        console.log(data);
        if(data.error == null && data.data != null){
            if(searchObject.action == null){
                window.location.href = location+'/home/';
            }else{
                window.location.href = location + '/home/#/' + searchObject.action + '/?' + jQuery.param(searchObject);
            }
        }
     }, function(error){
        null;
     });


    $scope.model = {};

    $scope.submit = function() {
        console.log("Performing " + $scope.sectionFlag);
        if($scope.sectionFlag == 'login'){
        //LOGGING USER IN
            if($scope.model.username == null || $scope.model.password == null){
                ngToast.warning("Please Enter username and password")
            }else{
                Login.save(JSON.stringify({username: $scope.model.username, password: $scope.model.password}), function(data){
                    console.log(data)
                    if(data.error == null){
                        if(searchObject.action == null){
                            window.location.href = location+'/home/';
                        }else{
                            window.location.href = location + '/home/#/' + searchObject.action + '/?' + jQuery.param(searchObject);
                        }
                    }else{
                        ngToast.danger(data.error);
                        console.log(data.error);
                    }
                });
            }
        }else if($scope.sectionFlag == 'register'){
        //REGISTERING NEW USER

        //Need to update pay_recurrance_flag...comes in as a json object

        $scope.model.pay_recurrance_flag = $scope.model.pay_recurrance.value

            console.log("REGISTERING NEW USER");
            Me.register(JSON.stringify($scope.model), function(data){
                console.log(data)
                if(data.error == null){
                    window.location.href = location+'/home/';
                }else{
                    ngToast.danger(data.error);
                    console.log(data.error);
                }
            });
        }else if($scope.sectionFlag == 'recover_password_form'){

            RecoverPassword.create({email_address:$scope.model.email},{email_address:$scope.model.email}, function(data) {
            if(data.error == null){
                    ngToast.success("Email sent. Please check your email box");
                    $scope.sectionFlag = 'complete_recover_password';
                }else{
                    ngToast.danger("Error: " + data.error);
                }
            }, function(error){
                console.log(error);
                ngToast.danger("Error Saving User Updates '" + error.status + "': " + error.statusText);
            });
        }else{
            ngToast.warning("There was an issue, refreshing...");
            window.location.href = location+'/';
        }
    }
}]);




/******************************
* RECOVER PASSWORD CONTROLLER *
******************************/
loginAppControllers.controller("recoverPasswordController",['$scope', '$location', 'ngToast', '$routeParams', 'Me', 'RecoverPassword',  function($scope, $location, ngToast, $routeParams, Me, RecoverPassword) {

    $scope.model= [];
    $scope.alreadyConfirmed = false;
    $scope.needToConfirm = true;
    $scope.confirmed = false;

    var searchObject = $location.search();
    if (searchObject != null){
        console.log('~~~URL Parameters~~~');
        console.log(searchObject);
        if (searchObject.token != null){
            $scope.model.password_token = searchObject.token;
            $scope.model.email_address = searchObject.email_address
        }
    }

    $scope.submit  = function(){

        if ($scope.model.new_password == $scope.model.confirm_new_password){
            var JSONdata = {};
            JSONdata.new_password = $scope.model.new_password;
            JSONdata.confirm_new_password = $scope.model.confirm_new_password;
            JSONdata.email_address = $scope.model.email_address;
            JSONdata.password_token = $scope.model.password_token;


            RecoverPassword.update({email_address:$scope.model.email_address}, JSON.stringify(JSONdata), function(data) {
                if(data.error == null){
                        $scope.confirmed = true
                        $scope.needToConfirm = false;
                        ngToast.success("Password has been changed");
                    }else{
                        ngToast.danger("Error: " + data.error);
                    }
            }, function(error){
                console.log(error);
                ngToast.danger("Error Saving User Updates '" + error.status + "': " + error.statusText);
            });


        }else{
            ngToast.danger("Passwords do not match");
        }

    }

}]);


var uPayRecurrenceSelectOptions = [
        {id: '1', value: "W",  name: 'Weekly'},
        {id: '2', value: "B",  name: 'Bi-Weekly (Every Other Week)'},
        {id: '3', value: "T",  name: 'Twice Monthly (1st and 15th)'},
        {id: '4', value: "M",  name: 'Monthly'}
];