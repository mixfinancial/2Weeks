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
    when('/:sectionFlag', {
        templateUrl: '/static/partials/Login-LoginForm.html',
        controller: 'loginAppLoginController'
    }).
    when('/', {
        templateUrl: '/static/partials/Login-LoginForm.html',
        controller: 'loginAppLoginController'
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







/**************
* CONTROLLERS *
**************/

var loginAppControllers = angular.module("loginAppControllers", []);



loginAppControllers.controller("loginAppLoginController",['$scope', '$location', 'Login', 'ngToast', 'LoginCheck', '$routeParams', 'Me', function($scope, $location, Login, ngToast, LoginCheck, $routeParams, Me) {

    var location = ""
    $scope.disableRegister = false;
    $scope.sectionFlag = 'login';

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

    if($location.absUrl().indexOf("admin") > -1){
        console.log("Admin Home");
        location = "/admin";
        $scope.disableRegister = true;
    }else{
        console.log("Main Home");

        if (searchObject != null && searchObject.auth_check == true){
            console.log('setting sectionFlag as login');
            $scope.sectionFlag = 'login';
        }else if($routeParams.sectionFlag == null){
            $scope.sectionFlag = 'register';
        }else if($routeParams.sectionFlag == 'register' || $routeParams.sectionFlag == 'login'){
            $scope.sectionFlag = $routeParams.sectionFlag;
        }else{
            $scope.sectionFlag = 'register';
        }
    }


    $scope.uPayRecurrenceSelectOptions = uPayRecurrenceSelectOptions;



    $scope.switchSection = function(){
        if($scope.sectionFlag == 'register'){
            $scope.sectionFlag = 'login';
        }else{
            $scope.sectionFlag = 'register';
        }
    }

    LoginCheck.get(function(data) {
        console.log(data);
        if(data.error == null && data.data != null){
            if(searchObject.action == null){
                window.location.href = location+'/home/';
            }else{
                window.location.href = location + '/home/#/' + searchObject.action + '/?' + jQuery.param(searchObject);
            }
        }
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

        }else{
            ngToast.warning("There was an issue, refreshing...");
            window.location.href = location+'/';
        }
    }
}]);






var uPayRecurrenceSelectOptions = [
        {id: '1', value: "W",  name: 'Weekly'},
        {id: '2', value: "B",  name: 'Bi-Weekly (Every Other Week)'},
        {id: '3', value: "T",  name: 'Twice Monthly (1st and 15th)'},
        {id: '4', value: "M",  name: 'Monthly'}
];