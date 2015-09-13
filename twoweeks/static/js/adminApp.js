'use strict';

var myApp = angular.module('myApp', [
    'ngRoute',
    'userControllers',
    'userServices',
    'loginServices',
    'alertServices',
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



//DEPRECATED
var alertServices = angular.module('alertServices', ['ngResource']);

//DEPRECATED
alertServices.factory('alertsManager', function() {
    return {
        alerts : [],
        addAlert: function(message, type) {
            //this.alerts = [];
            this.alerts.push({'type' : type,  'msg' : message});
            console.log(this.alerts);
        },
        closeAlert: function(index) {
            this.alerts.splice(index, 1);
        }
    };
});