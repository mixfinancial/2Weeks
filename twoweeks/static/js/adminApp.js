'use strict';

var myApp = angular.module('myApp', [
    'ngRoute',
    'userControllers',
    'dbServices',
    'ui.bootstrap',
    'formly',
    'formlyBootstrap',
    'ngAnimate',
    'ngToast',
    'ngCookies'
]);


myApp.run(function() {
    FastClick.attach(document.body);
});


myApp.directive('ngReallyClick', [function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            element.bind('click', function() {
                var message = attrs.ngReallyMessage;
                if (message && confirm(message)) {
                    scope.$apply(attrs.ngReallyClick);
                }
            });
        }
    }
}]);


myApp.config(['$routeProvider', 'ngToastProvider', function($routeProvider, ngToastProvider) {
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


    ngToastProvider.configure({
        animation: 'fade',
        dismissButton: 'true',
        verticalPosition: 'bottom'
    });
}]);






var loginApp = angular.module('loginApp', [
    'ngRoute',
    'loginAppControllers',
    'loginServices',
    'formly',
    'formlyBootstrap',
    'ngToast'
]);


loginApp.config(['$routeProvider', 'ngToastProvider', function($routeProvider, ngToastProvider) {
    $routeProvider.
    when('/login', {
        templateUrl: '/static/partials/loginAppLoginView.html',
        controller: 'loginAppLoginController'
    }).
    otherwise({
        templateUrl: '/static/partials/loginAppLoginView.html',
        controller: 'loginAppLoginController'
    });


    ngToastProvider.configure({
        animation: 'fade',
        dismissButton: 'true',
        verticalPosition: 'bottom'
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
      'create': {method:'POST', isArray:false},
      'delete': {method:'DELETE', params:{userId:'users'}, isArray:false},
      'update': {method:'PUT', isArray:false}
    });
  }]);


dbServices.factory('Bill', ['$resource',
  function($resource){
    return $resource('/api/bill/:billId', {}, {
      'query': {method:'GET', isArray:false},
      'get': {method:'GET', params:{billId:'bills'}, isArray:false},
      'create': {method:'POST', isArray:false},
      'delete': {method:'DELETE', params:{billId:'bills'}, isArray:false},
      'update': {method:'PUT', isArray:false}
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
