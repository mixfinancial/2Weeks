'use strict';

    var userControllers = angular.module("userControllers", []);

    userControllers.controller('adminNavBarController',['$scope', '$http', '$location', function($scope, $http, $location ) {
      $scope.logout = function($window, $location) {
        console.log('logging out');
            $http.get('/api/logout/').
                success(function(data, status, headers, config) {
                    window.location.href = '/admin/';
                }).
                error(function(data, status, headers, config) {
                    console.log('could not logout');
            });
        };
    }]);

    userControllers.controller("UserListController", ['$scope', '$http', 'User', function($scope, $http, User) {
        User.query(function(data) {
            console.log(data);
            $scope.users = data.data;
         });

        $scope.delete = function($window, $location) {
            User.delete({userId: $routeParams.userId});
        }
    }]);

    userControllers.controller("UserViewController", ['$scope', '$http', '$routeParams', 'User', function($scope, $http, $routeParams, User) {
        $scope.users = User.get({userId: $routeParams.userId}, function(user) {
            console.log(user.data[0])
            $scope.user = user.data[0];
        });

        $scope.delete = function($window, $location) {
            User.delete({userId: $routeParams.userId});
            window.location.href = '/UserListController';
        }
    }]);

    userControllers.controller("UserFormController",['$scope', '$http', '$routeParams', '$location', 'User', function($scope, $http, transformRequestAsFormPost, $location, User) {
        $scope.submit = function() {
            var data = $scope.user;
            User.save(JSON.stringify(data));
            $location.path( "/usersTable");
        };
    }]);

    userControllers.controller("UserEditFormController",['$scope', '$http', '$routeParams', '$location', 'User', function($scope, $http, $routeParams, $location, User) {
        $scope.users = User.get({userId: $routeParams.userId}, function(user) {
            console.log(user.data[0])
            $scope.user = user.data[0];
        });

        $scope.submit = function() {
            var data = $scope.user;
            User.save(JSON.stringify(data));
            $location.path( "/usersTable");
        };
    }]);

    userControllers.controller("UserLoginController",['$scope', '$routeParams', '$location', 'Login', 'notificationService', function($scope, transformRequestAsFormPost, $location, Login, notificationService) {
         $scope.submit = function() {
            Login.save($.param({username: $scope.username, password: $scope.password}), function(data){
                console.log(data)
                if(data.error == null){
                    window.location.href = '/admin/home/';
                }else{
                    notificationService.error(data.error)
                    console.log(data.error);
                }
            });
        };
    }]);
