'use strict';

    var userControllers = angular.module("userControllers", []);

    userControllers.controller("UserListController", ['$scope', '$http', function($scope, $http) {
      $http.get('/api/user/').
        success(function(data, status, headers, config) {
          $scope.users = data.data;
        }).
        error(function(data, status, headers, config) {
          // log error
        });
    }]);


    userControllers.controller("UserViewController", ['$scope', '$http', '$routeParams', function($scope, $http, $routeParams) {
      $http.get('/api/user/'+$routeParams.userId).
        success(function(data, status, headers, config) {
          $scope.users = data.data;
        }).
        error(function(data, status, headers, config) {
          // log error
        });
    }]);


    angular.module('myApp').factory('dataFactory', ['$http', function($http) {

        var urlBase = '/api/user';
        var dataFactory = {};

        dataFactory.getUsers = function () {
            return $http.get(urlBase);
        };

        dataFactory.getUser = function (id) {
            return $http.get(urlBase + '/' + id);
        };

        dataFactory.insertUser = function (user) {
            return $http.post(urlBase, user);
        };

        dataFactory.updateUser = function (user) {
            return $http.put(urlBase + '/' + user.ID, cust)
        };

        dataFactory.deleteUser = function (id) {
            return $http.delete(urlBase + '/' + id);
        };

       return dataFactory;
    }]);