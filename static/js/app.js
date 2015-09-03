'use strict';

var myApp = angular.module('myApp', [
    'ngRoute',
    'userControllers'
]);

myApp.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
    when('/usersTable', {
        templateUrl: '../static/partials/usersTable.html',
        controller: 'UserListController'
    }).
    when('/usersView/:userId', {
        templateUrl: '../static/partials/usersView.html',
        controller: 'UserViewController'
    }).
    when('/usersForm', {
        templateUrl: '../static/partials/usersForm.html',
        controller: 'UserFormController'
    }).
    when('/usersEditForm/:userId', {
        templateUrl: '../static/partials/usersEditForm.html',
        controller: 'UserEditFormController'
    }).
    when('/userDelete/:userId', {
        templateUrl: '../static/partials/usersTable.html',
        controller: 'UserDeleteController'
    }).
    otherwise({
        redirectTo: '/usersTable'
    });
}]);


