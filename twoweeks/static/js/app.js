'use strict';


var billsApp = angular.module('billsApp', [
    'ngRoute',
    'billsAppControllers',
    'menuBarAppControllers',
    'dbServices',
    'feedbackServices',
    'ui.bootstrap',
    'formly',
    'formlyBootstrap',
    'ngAnimate',
    'ngToast',
    'ngCookies'
]);


billsApp.run(function() {
    FastClick.attach(document.body);
});


billsApp.config(['$routeProvider', 'ngToastProvider', function($routeProvider, ngToastProvider) {
    $routeProvider.
    when('/', {
        templateUrl: '/static/partials/billPrep.html',
        controller: ''
    }).
    when('/billPrep', {
        templateUrl: '/static/partials/billPrep.html',
        controller: ''
    }).
    when('/confirm_email/:confirmation_code', {
        templateUrl: '/static/partials/confirm_email.html',
        controller: ''
    }).
    when('/confirm_email', {
        templateUrl: '/static/partials/confirm_email.html',
        controller: ''
    }).
    when('/recover_password', {
        templateUrl: '/static/partials/recover_password.html',
        controller: ''
    }).
    when('/billExecute', {
        templateUrl: '/static/partials/billExecute.html',
        controller: ''
    }).
    when('/billTrack', {
        templateUrl: '/static/partials/billTrack.html',
        controller: ''
    }).
    when('/userAccount', {
        templateUrl: '/static/partials/userAccount.html',
        controller: ''
    }).
    otherwise({
        redirectTo: '/billPrep'
    });

    ngToastProvider.configure({
        animation: 'fade',
        dismissButton: 'true',
        verticalPosition: 'bottom',
        horizontalPosition: 'left'
    });
}]);


billsApp.directive('ngReallyClick', [function() {
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



/*********************
*  Database Services *
**********************/

var dbServices = angular.module('dbServices', ['ngResource']);

dbServices.factory('Bill', ['$resource',
  function($resource){
    return $resource('/api/bill/:billId', {}, {
      'query': {method:'GET', isArray:false},
      'get': {method:'GET', params:{billId:'billId'}, isArray:false},
      'create': {method:'POST', params:{billId:'billId'}, isArray:false},
      'update': {method:'PUT', isArray:false},
      'delete': {method:'DELETE', isArray:false}
    });
  }]);

dbServices.factory('PaymentPlan', ['$resource',
  function($resource){
    return $resource('/api/payment_plan/:payment_plan_id', {}, {
      'query': {method:'GET', isArray:false},
      'get': {method:'GET', params:{payment_plan_id:'payment_plan_id'}, isArray:false},
      'create': {method:'POST', params:{payment_plan_id:'payment_plan_id'}, isArray:false},
      'update': {method:'PUT', isArray:false},
      'delete': {method:'DELETE', isArray:false}
    });
  }]);


dbServices.factory('PaymentPlanItem', ['$resource',
  function($resource){
    return $resource('/api/payment_plan_item/:payment_plan_item_id', {}, {
      'query': {method:'GET', isArray:false},
      'get': {method:'GET', params:{payment_plan_item_id:'payment_plan_item_id'}, isArray:false},
      'create': {method:'POST', params:{payment_plan_item_id:'payment_plan_item_id'}, isArray:false},
      'update': {method:'PUT', isArray:false},
      'delete': {method:'DELETE', isArray:false}
    });
  }]);


dbServices.factory('Me', ['$resource',
  function($resource){
    return $resource('/api/me/:userId', {}, {
      'query': {method:'GET', isArray:false},
      'get': {method:'GET', params:{userId:'users'}, isArray:false},
      'update': {method:'PUT', isArray:false},
      'register': {method:'POST', isArray:false}
    });
  }]);


dbServices.factory('ConfirmEmail', ['$resource',
  function($resource){
    return $resource('/api/confirm_email/:token', {}, {
      'create': {method:'POST', isArray:false},
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


/*********************
*  Feedback Services *
*********************/

var feedbackServices = angular.module('feedbackServices', ['ngResource']);

feedbackServices.factory('Feedback', ['$resource',
  function($resource){
    return $resource('/api/feedback/', {}, {
      'query': {method:'GET', isArray:false},
      'get': {method:'GET', params:{userId:'users'}, isArray:false},
      'create': {method:'POST', isArray:false}
    });
  }]);
