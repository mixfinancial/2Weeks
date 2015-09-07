'use strict';


var loginApp = angular.module('billsApp', [
    'ngRoute',
    'billsAppControllers'
]);


var loginApp = angular.module('loginApp', [
    'ngRoute',
    'loginAppControllers'
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