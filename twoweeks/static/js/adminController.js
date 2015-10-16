'use strict';

    var userControllers = angular.module("userControllers", []);
    var loginAppControllers = angular.module("loginAppControllers", []);

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

    userControllers.controller("UserListController", ['$scope', '$http', 'User', '$routeParams', 'ngToast', function($scope, $http, User, $routeParams, ngToast) {
        User.query(function(data) {
            console.log(data);
            $scope.users = data.data;
         });

        $scope.delete = function(text, $window, $location) {
            User.delete({userId: text});
            ngToast.success('User #'+text+' has been successfully deleted')
            //TODO: Check for successful $promise before sending notification
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
            User.create(JSON.stringify(data));
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
            User.create(JSON.stringify(data));
            $location.path( "/usersTable");
        };
    }]);



loginAppControllers.controller("loginAppLoginController",['$scope', '$routeParams', '$location', 'Login', 'ngToast', 'LoginCheck', function($scope, transformRequestAsFormPost, $location, Login, ngToast, LoginCheck) {

    LoginCheck.get(function(data) {
        console.log(data);
        if(data.error == null && data.data != null){
            window.location.href = '/admin/home/';
        }
     });

     $scope.model = {};

     $scope.formFields = [
                            {
                                key: 'username',
                                type: 'input',
                                templateOptions: {
                                    type: 'text',
                                    label: 'username',
                                    placeholder: 'your@email.com',
                                    required: true
                                }
                            },
                            {
                                key: 'password',
                                type: 'input',
                                templateOptions: {
                                    type: 'password',
                                    label: 'password',
                                    required: true
                                }
                            }
                        ];

     $scope.submit = function() {
        if($scope.model.username == null || $scope.model.password == null){
             ngToast.create("Please Enter username and password")
        }else{
            Login.save(JSON.stringify({username: $scope.model.username, password: $scope.model.password}), function(data){
                console.log(data)
                if(data.error == null){
                    window.location.href = '/admin/home/';
                }else{
                    ngToast.danger(data.error)
                    console.log(data.error);
                }
            });
        }
    }
}]);

