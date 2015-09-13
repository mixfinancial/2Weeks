'use strict';


var billsApp = angular.module('billsApp', [
    'ngRoute',
    'billsAppControllers'
]);


var loginApp = angular.module('loginApp', [
    'ngRoute',
    'loginAppControllers',
    'userServices',
    'loginServices',
    'jlareau.pnotify'
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



var userServices = angular.module('userServices', ['ngResource']);

userServices.factory('User', ['$resource',
  function($resource){
    return $resource('/api/user/:userId', {}, {
      'query': {method:'GET', isArray:false},
      'get': {method:'GET', params:{userId:'users'}, isArray:false},
      'save': {method:'POST', isArray:false},
      'delete': {method:'DELETE', isArray:false},
      'put': {method:'PUT', isArray:false}
    });
  }]);


var loginServices = angular.module('loginServices', ['ngResource']);

loginServices.factory('Login', ['$resource',
  function($resource){
    return $resource('/api/login/', {}, {
      'save': {method:'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, isArray:false}
    });
  }]);


