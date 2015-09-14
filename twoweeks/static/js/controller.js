'use strict';

    var billsControllers = angular.module("billsControllers", []);
    var loginAppControllers = angular.module("loginAppControllers", []);
    var menuBarAppControllers = angular.module("menuBarAppController", []);


    loginAppControllers.controller("loginAppLoginController",['$scope', '$routeParams', '$location', 'Login', 'notificationService', function($scope, transformRequestAsFormPost, $location, Login, notificationService) {
         $scope.submit = function() {
            if($scope.username == null || $scope.password == null){
                 notificationService.error("Please Enter username and password")
            }else{
                Login.save($.param({username: $scope.username, password: $scope.password}), function(data){
                    console.log(data)
                    if(data.error == null){
                        window.location.href = '/home/';
                    }else{
                        notificationService.error(data.error)
                        console.log(data.error);
                    }
                });
            }
        }
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








    menuBarAppControllers.controller('menuBarAppController',['$scope', '$http', '$location', function($scope, $http, $location ) {
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

