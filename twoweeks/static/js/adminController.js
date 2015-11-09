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



/*******************
* LOGIN CONTROLLER *
*******************/
loginAppControllers.controller("loginAppLoginController",['$scope', '$location', 'Login', 'ngToast', 'LoginCheck', '$routeParams', function($scope, $location, Login, ngToast, LoginCheck, $routeParams) {
    $scope.sectionFlag = 'login';

    $scope.switchSection = function(){
        if($scope.sectionFlag == 'register'){
            $scope.sectionFlag = 'login';
        }else{
            $scope.sectionFlag = 'register';
        }
    }

    LoginCheck.get(function(data) {
        console.log(data);
        if(data.error == null && data.data != null){
            window.location.href = '/admin/home/';
        }
     });

    $scope.model = {};

    $scope.submit = function() {
        console.log("Performing " + $scope.sectionFlag);
        if($scope.sectionFlag == 'login'){
        //LOGGING USER IN
            if($scope.model.username == null || $scope.model.password == null){
                ngToast.warning("Please Enter username and password")
            }else{
                Login.save(JSON.stringify({username: $scope.model.username, password: $scope.model.password}), function(data){
                    console.log(data)
                    if(data.error == null){
                        window.location.href = '/admin/home/';
                    }else{
                        ngToast.danger(data.error);
                        console.log(data.error);
                    }
                });
            }
        }else if($scope.sectionFlag == 'register'){


        }else{
            ngToast.warning("There was an issue, refreshing...");
            window.location.href = '/';
        }
    }
}]);

