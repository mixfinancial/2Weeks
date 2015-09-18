'use strict';

var billsAppControllers = angular.module("billsAppControllers", []);
var loginAppControllers = angular.module("loginAppControllers", []);
var menuBarAppControllers = angular.module("menuBarAppControllers", []);



/***********************
* BILL PREP CONTROLLER *
************************/
billsAppControllers.controller("billFormController",['$scope', '$http', '$routeParams', '$location', 'Bill', 'notificationService', '$modal', function($scope, $http, transformRequestAsFormPost, $location, Bill, notificationService, $modal) {

    $scope.animationsEnabled = true

    $scope.openModal = function (index) {
        console.log(index);
        var modalInstance = $modal.open({
          animation: $scope.animationsEnabled,
          templateUrl: '/static/partials/form_bill.html',
          controller: 'BillFormModalController',
          resolve: {
            data: function () {
              return $scope.bills[index];
            }
          }
        });

        modalInstance.result.then(function (selectedItem) {
          $scope.selected = selectedItem;
        }, function () {
          console.log('Modal dismissed at: ' + new Date());
        });
      };


    Bill.query(function(data) {
        console.log(data);
        $scope.bills = data.data;
     });

    $scope.submit = function() {
       var data = $scope.bill;
       console.log(data);
       Bill.save(JSON.stringify(data), function(data) {
            console.log(data);
            $scope.bills.push(data.data);
            notificationService.success("Bill Created")
       });
    };

    $scope.delete = function(index, $window, $location) {
       console.log('attempting to delete bill index #'+index);
       var data = $scope.bills[index];
       Bill.delete({billId: data.id}, function(data) {
        $scope.bills.splice(index);
        notificationService.notice("Bill Deleted")
       });
    };

}]);







/*****************************
* BILL FORM MODAL CONTROLLER *
******************************/
billsAppControllers.controller('BillFormModalController', ['$scope', '$modalInstance', 'Bill', 'notificationService', 'data', function ($scope, $modalInstance, Bill, notificationService, data) {
    $scope.bill = data;
    $scope.bill.newName = data.name;
    $scope.bill.newDueDate = data.dueDate;

    var backup = data;
    console.log($scope.bill);

    $scope.submitEditForm = function(data) {

       var data = $scope.bill;
       data.billId = data.id;
       data.name = $scope.bill.newName;
       data.due_date = $scope.bill.newDueDate;

       console.log(data);
       Bill.put({billId: data.id}, JSON.stringify(data), function(data) {
            if(data.error == null){
                $scope.bill.name = $scope.bill.newName;
                $scope.bill.dueDate = $scope.bill.newdueDate;
                console.log(data);
                $modalInstance.close();
                notificationService.success("Bill Updated");
            }else{
                notificationService.error("Error: "+data.error);
            }
       }, function(error){
            console.log(error);
            notificationService.error("Received error status '"+error.status+"': "+error.statusText);
            $scope.bill = backup;
           });
    };


  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };


  $scope.today = function() {
    $scope.due_date = new Date();
  };
  $scope.today();

  $scope.clear = function () {
    $scope.due_date = null;
  };

  // Disable weekend selection
  $scope.disabled = function(date, mode) {
    return ( mode === 'day' && ( date.getDay() === 0 || date.getDay() === 6 ) );
  };

  $scope.toggleMin = function() {
    $scope.minDate = $scope.minDate ? null : new Date();
  };

  $scope.toggleMin();
  $scope.maxDate = new Date(2020, 5, 22);

  $scope.openDatePicker = function($event) {
    console.log('test');
    $scope.status.opened = true;
  };

  $scope.dateOptions = {
    formatYear: 'yy',
    startingDay: 1
  };

  $scope.format =  'yyyy/MM/dd';

  $scope.status = {
    opened: false
  };

  var tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  var afterTomorrow = new Date();
  afterTomorrow.setDate(tomorrow.getDate() + 2);
  $scope.events =
    [
      {
        date: tomorrow,
        status: 'full'
      },
      {
        date: afterTomorrow,
        status: 'partially'
      }
    ];

  $scope.getDayClass = function(date, mode) {
    if (mode === 'day') {
      var dayToCheck = new Date(date).setHours(0,0,0,0);

      for (var i=0;i<$scope.events.length;i++){
        var currentDay = new Date($scope.events[i].date).setHours(0,0,0,0);

        if (dayToCheck === currentDay) {
          return $scope.events[i].status;
        }
      }
    }

    return '';
  };


}]);






loginAppControllers.controller("loginAppLoginController",['$scope', '$routeParams', '$location', 'Login', 'notificationService', function($scope, transformRequestAsFormPost, $location, Login, notificationService) {
     $scope.submit = function() {
        if($scope.username == null || $scope.password == null){
             notificationService.error("Please Enter username and password")
        }else{
            Login.save(JSON.stringify({username: $scope.username, password: $scope.password}), function(data){
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





loginAppControllers.controller("loginAppRegisterController",['$scope', '$http', '$routeParams', '$location','$window', function($scope, $http, transformRequestAsFormPost, $location) {
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
 //console.log('logging out');
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



