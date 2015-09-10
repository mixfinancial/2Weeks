'use strict';

    var billsControllers = angular.module("billsControllers", []);
    var loginAppControllers = angular.module("loginAppControllers", []);
    var menuBarAppController = angular.module("menuBarAppController", []);


    loginAppControllers.controller("loginAppLoginController",['$scope', '$http', '$routeParams', '$location', function($scope, $http, transformRequestAsFormPost, $location ) {
        $scope.submit = function() {
            $http({
              url: "/api/login/",
              method: "POST",
              headers: {'Content-Type': 'application/x-www-form-urlencoded'},
               data: $.param({username: $scope.username, password: $scope.password})
            }).success(function(data) {
              console.log(data)
              if(data['error'] == 'none'){
                window.location.href = '/home/';
              }else{
                 $scope.errors = data.error;
                 console.log(data.error)
                 //console.log($scope.alerts)
                 console.log($scope.alerts);
                 //$location.path("/login");
              }
            })
        };
    }]);


    loginAppControllers.controller("loginAppRegisterController",['$scope', '$http', '$routeParams', '$location','$window', function($scope, $http, transformRequestAsFormPost, $location ) {
        $scope.submit = function($window, $location) {
            $http({
              url: "/api/login/",
              method: "POST",
              headers: {'Content-Type': 'application/x-www-form-urlencoded'},
               data: $.param({username: $scope.username, password: $scope.password})
            }).success(function(data) {
              console.log(data)
              window.location.href = '/home/';
            });
        };
    }]);


    menuBarAppController.controller('menuBarAppController',['$scope', '$http', '$location', function($scope, $http, $location ) {
     console.log('logging out');
      $scope.logout = function($window, $location) {
        console.log('logging out');
            $http.get('/api/logout/').
                success(function(data, status, headers, config) {
                    window.location.href = '/';
                }).
                error(function(data, status, headers, config) {
                    console.log('could not logout');
            });
        };
    }]);

