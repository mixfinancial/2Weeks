'use strict';

var myApp = angular.module('myApp', [
    'ngRoute',
    'userControllers',
    'userServices'
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
      query: {method:'GET', params:{userId:'users'}, isArray:false}
    });
  }]);