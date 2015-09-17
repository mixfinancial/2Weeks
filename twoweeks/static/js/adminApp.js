'use strict';

var myApp = angular.module('myApp', [
    'ngRoute',
    'userControllers',
    'dbServices',
    'loginServices',
    'jlareau.pnotify'
]);

myApp.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
    when('/usersTable', {
        templateUrl: '/static/partials/adminUsersTable.html',
        controller: 'UserListController'
    }).
    when('/usersView/:userId', {
        templateUrl: '/static/partials/adminUsersView.html',
        controller: 'UserViewController'
    }).
    when('/usersForm', {
        templateUrl: '/static/partials/adminUsersForm.html',
        controller: 'UserFormController'
    }).
    when('/usersEditForm/:userId', {
        templateUrl: '/static/partials/adminUsersEditForm.html',
        controller: 'UserEditFormController'
    }).
    when('/userDelete/:userId', {
        templateUrl: '/static/partials/adminUsersTable.html',
        controller: 'UserDeleteController'
    }).
    otherwise({
        redirectTo: '/usersTable'
    });
}]);






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
      'delete': {method:'DELETE', params:{userId:'users'}, isArray:false},
      'put': {method:'PUT', isArray:false}
    });
  }]);


dbServices.factory('Bill', ['$resource',
  function($resource){
    return $resource('/api/bill/:billId', {}, {
      'query': {method:'GET', isArray:false},
      'get': {method:'GET', params:{billId:'bills'}, isArray:false},
      'save': {method:'POST', isArray:false},
      'delete': {method:'DELETE', params:{billId:'bills'}, isArray:false},
      'put': {method:'PUT', isArray:false}
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


