'use strict';

    var app = angular.module("myApp", []);

    app.controller("UsersCtrl", function($scope, $http) {
      $http.get('/users').
        success(function(data, status, headers, config) {
          $scope.users = data;
        }).
        error(function(data, status, headers, config) {
          // log error
        });
    });
