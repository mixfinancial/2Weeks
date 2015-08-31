'use strict';

    angular.module('mainApp',['ngResource']); //mainApp is our main module

    angular.module('myApp.services').factory('Entry', function($resource) {
      return $resource('/api/users/:id', { id: '@_id' }, {
        update: {
          method: 'PUT' // this method issues a PUT request
        }
      });
    });

    angular.module('myApp.controllers',[]);

    angular.module('myApp.controllers').controller('ResourceController',function($scope, Entry) {
      var entry = Entry.get({ id: $scope.id }, function() {
        console.log(entry);
      }); // get() returns a single entry

      var entries = Entry.query(function() {
        console.log(entries);
      }); //query() returns all the entries

      $scope.entry = new Entry(); //You can instantiate resource class

      $scope.entry.data = 'some data';

      Entry.save($scope.entry, function() {
        //data saved. do something here.
      }); //saves an entry. Assuming $scope.entry is the Entry object
    });