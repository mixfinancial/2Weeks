'use strict';


var billsApp = angular.module('billsApp', [
    'ngRoute',
    'billsAppControllers',
    'ui.bootstrap'
]);


var loginApp = angular.module('loginApp', [
    'ngRoute',
    'loginAppControllers',
    'ui.bootstrap'
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
