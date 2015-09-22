'use strict';


var billsApp = angular.module('billsApp', [
    'ngRoute',
    'billsAppControllers',
    'menuBarAppControllers',
    'jlareau.pnotify',
    'dbServices',
    'ui.bootstrap',
    'formly',
    'formlyBootstrap'
]);


billsApp.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
    when('/billPrep', {
        templateUrl: '/static/partials/billPrep.html',
        controller: ''
    }).
    otherwise({
        templateUrl: '/static/partials/billPrep.html',
        controller: ''
    });
}]);



var loginApp = angular.module('loginApp', [
    'ngRoute',
    'loginAppControllers',
    'loginServices',
    'jlareau.pnotify',
    'formly',
    'formlyBootstrap'
]);


loginApp.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
    when('/login', {
        templateUrl: '/static/partials/loginAppLoginView.html',
        controller: 'loginAppLoginController'
    }).
    when('/register', {
        templateUrl: '/static/partials/loginAppRegisterView.html',
        controller: 'loginAppRegisterController'
    }).
    otherwise({
        templateUrl: '/static/partials/loginAppLoginView.html',
        controller: 'loginAppLoginController'
    });
}]);




var menuBarApp = angular.module('menuBarApp', [
    'ngRoute',
    'menuBarAppController'
]);






/*********************
*  Database Services *
**********************/

var dbServices = angular.module('dbServices', ['ngResource']);

dbServices.factory('User', ['$resource',
  function($resource){
    return $resource('/api/user/:userId', {}, {
      'query': {method:'GET', isArray:false},
      'get': {method:'GET', params:{userId:'users'}, isArray:false},
      'save': {method:'POST', isArray:false},
      'put': {method:'PUT', isArray:false},
      'delete': {method:'DELETE', isArray:false}
    });
  }]);


dbServices.factory('Bill', ['$resource',
  function($resource){
    return $resource('/api/bill/:billId', {}, {
      'query': {method:'GET', isArray:false},
      'get': {method:'GET', params:{billId:'billId'}, isArray:false},
      'save': {method:'POST', params:{billId:'billId'}, isArray:false},
      'put': {method:'PUT', isArray:false},
      'delete': {method:'DELETE', isArray:false}
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


