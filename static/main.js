'use strict';

    var app = angular.module("myApp", []);

    app.controller("UsersCtrl", function($scope, $http) {
      $http.get('/api/users').
        success(function(data, status, headers, config) {
          $scope.users = data.data;
        }).
        error(function(data, status, headers, config) {
          // log error
        });
    });


    app.controller('formCtrl', function($scope) {
        $scope.reset = function() {
            $scope.user = angular.copy($scope.master);
        };
        $scope.reset();
    });