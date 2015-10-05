'use strict';

var billsAppControllers = angular.module("billsAppControllers", []);
var loginAppControllers = angular.module("loginAppControllers", []);
var menuBarAppControllers = angular.module("menuBarAppControllers", []);



/***********************
* BILL PREP CONTROLLER *
************************/
billsAppControllers.controller("billFormController",['$scope', '$http', '$routeParams', '$location', 'Bill', 'notificationService', '$modal', 'Me', function($scope, $http, transformRequestAsFormPost, $location, Bill, notificationService, $modal, Me) {
    $scope.date = new Date();
    $scope.animationsEnabled = true


    $scope.editBill = function (index) {
        //console.log(index);
        //console.log($scope.bills.indexOf(index));
        var modalInstance = $modal.open({
          animation: $scope.animationsEnabled,
          templateUrl: '/static/partials/modalForm.html',
          controller: 'BillFormModalController',
          resolve: {
            data: function () {
              return angular.copy($scope.bills[$scope.bills.indexOf(index)]);
            }
          }
        });

        modalInstance.result.then(function (newBill) {
          $scope.bills.splice($scope.bills.indexOf(index), 1);
          $scope.bills.push(newBill);
        }, function () {
          console.log('Modal dismissed at: ' + new Date());
        });
      };


    $scope.newBill = function () {
        var modalInstance = $modal.open({
          animation: $scope.animationsEnabled,
          templateUrl: '/static/partials/modalForm.html',
          controller: 'BillFormModalController',
          resolve: {
            data: function () {
              return null;
            }
          }
        });

        modalInstance.result.then(function (newBill) {
          $scope.bills.push(newBill);
        }, function () {
          console.log('Modal dismissed at: ' + new Date());
        });
      };


    //Convert dates in the bills array
    var log = [];

    Me.query(function(data) {
        $scope.me = angular.copy(data.data[0]);
        $scope.me.next_pay_date = new Date($scope.me.next_pay_date);

         Bill.query(function(data) {
            $scope.bills = data.data;
            angular.forEach($scope.bills,function(value,index){
                $scope.bills[index].due_date = new Date($scope.bills[index].due_date);
                $scope.bills[index].total_due = parseFloat($scope.bills[index].total_due);
            });


            $scope.dueBeforeNextPaycheck = function() {
            var total = 0;
            for(var i = 0; i < $scope.bills.length; i++){
                if ($scope.bills[i].due_date.getTime() < $scope.me.next_pay_date.getTime()){
                    if($scope.bills[i].total_due){
                        total += $scope.bills[i].total_due;
                    }
                }
            }
            return total;
            };


            $scope.dueBeforeNext30 = function() {
            var total = 0;
            for(var i = 0; i < $scope.bills.length; i++){
                if ($scope.differenceInDays($scope.bills[i].due_date) < 30){
                    if($scope.bills[i].total_due){
                        total += $scope.bills[i].total_due;
                    }
                }
            }
            return total;
            };


            $scope.daysBeforeNextPaycheck = function() {
                return $scope.differenceInDays($scope.me.next_pay_date);
            };


         });

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

    $scope.deleteBill = function(index, $window, $location) {
       console.log('attempting to delete bill index #'+index);
       var data = $scope.bills[$scope.bills.indexOf(index)];
       Bill.delete({billId: data.id}, function(data) {
        $scope.bills.splice($scope.bills.indexOf(index), 1);
        notificationService.notice("Bill Deleted")
       });
    };

    $scope.differenceInDays = function(first_date) {
        var today = new Date();
        var millisecondsPerDay = 1000 * 60 * 60 * 24;
        var millisBetween = first_date.getTime() - today.getTime();
        var days = millisBetween / millisecondsPerDay
        return Math.floor(days);
    };
}]);







/*****************************
* BILL FORM MODAL CONTROLLER *
******************************/
billsAppControllers.controller('BillFormModalController', ['$scope', '$modalInstance', 'Bill', 'notificationService', 'data', function ($scope, $modalInstance, Bill, notificationService, data) {
    var action = 'new';


    if(data != null){
        var action = 'edit';
        $scope.title = "Edit Bill"
        $scope.model = data;
        $scope.model.due_date = new Date(data.due_date);
    }else{
        $scope.title = "Create New Bill"
    }

    $scope.formFields = [
                            {
                                key: 'name',
                                type: 'input',
                                templateOptions: {
                                    type: 'text',
                                    label: 'name',
                                    placeholder: 'Name of Bill',
                                    required: true
                                }
                            },
                            {
                                key: 'total_due',
                                type: 'input',
                                templateOptions: {
                                    addonLeft: {
                                        text:'$'
                                    },
                                    type: 'number',
                                    label: 'Total Due',
                                    required: true
                                }
                            },
                            {
                                key: 'due_date',
                                type: 'input',
                                templateOptions: {
                                    type: 'date',
                                    label: 'Due Date',
                                    required: true
                                }
                            }
                        ];


    var backup = data;
    //console.log($scope.model);

    $scope.submitModalForm = function(data) {
        //need to convert strings to date for persistance through application;
        $scope.model.due_date = new Date($scope.model.due_date);
        var data = $scope.model;
        if(action == "edit"){
           //console.log(data);
           Bill.update({billId: data.id}, JSON.stringify(data), function(data) {
                if(data.error == null){
                    data.data.due_date = new Date(data.data.due_date);
                    data.data.total_due = parseFloat(data.data.total_due);
                    $modalInstance.close(data.data);
                    notificationService.success("Bill Updated");
                }else{
                    notificationService.error("Error: "+data.error);
                }
           }, function(error){
                console.log(error);
                notificationService.error("Received error status '"+error.status+"': "+error.statusText);
                $scope.bill = backup;
               });
        }else{
           console.log(data);
           Bill.create(JSON.stringify(data), function(data) {
                if(data.error == null){
                    console.log(data.data);
                    data.data.due_date = new Date(data.data.due_date);
                    data.data.total_due = parseFloat(data.data.total_due);
                    $modalInstance.close(data.data);
                    notificationService.success("Bill Added");
                }else{
                    notificationService.error("Error: "+data.error);
                }
           }, function(error){
                console.log(error);
                notificationService.error("Received error status '"+error.status+"': "+error.statusText);
                $scope.bill = backup;
               });

        }

    };


  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };


}]);






loginAppControllers.controller("loginAppLoginController",['$scope', '$routeParams', '$location', 'Login', 'notificationService', 'LoginCheck', function($scope, transformRequestAsFormPost, $location, Login, notificationService, LoginCheck) {

    LoginCheck.get(function(data) {
        console.log(data);
        if($scope.error == null){
            window.location.href = '/home/';
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
             notificationService.error("Please Enter username and password")
        }else{
            Login.save(JSON.stringify({username: $scope.model.username, password: $scope.model.password}), function(data){
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










menuBarAppControllers.controller('menuBarAppController',['$scope', '$http', '$location', '$modal', 'Me', 'Feedback', function($scope, $http, $location, $modal, Me, Feedback) {

    Me.query(function(data) {
        console.log(data.data[0]);
        $scope.me = data.data[0];
     });

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

    $scope.openFeedbackModal = function () {
        var modalInstance = $modal.open({
          animation: $scope.animationsEnabled,
          templateUrl: '/static/partials/modalForm.html',
          controller: 'FeedbackFormModalController',
          scope: $scope,
          resolve: {
            data: function () {
              return null;
            }
          }
        });

        modalInstance.result.then(function () {
            console.log('Form submitted');
        }, function () {
          console.log('Modal dismissed at: ' + new Date());
        });
      };


}]);




menuBarAppControllers.controller('userAccountController',['$scope', '$http', '$location', '$modal', 'Me', 'notificationService', function($scope, $http, $location, $modal, Me, notificationService) {
    $scope.uNameCollapse = true;
    $scope.uUserNameCollapse = true;
    $scope.uPasswordCollapse = true;
    $scope.uEmailCollapse = true;
    $scope.uNextPayDate = true;
    $scope.uPayRecurrence = true;
    $scope.uAveragePaycheckAmount = true;

    $scope.uPayRecurrenceSelectOptions = [
            {id: '1', value: "W",  name: 'Weekly'},
            {id: '2', value: "B",  name: 'Bi-Weekly'},
            {id: '3', value: "T",  name: 'Twice Monthly'},
            {id: '4', value: "M",  name: 'Monthly'}
        ];


    Me.query(function(data) {
        console.log(data.data[0]);
        $scope.model = angular.copy(data.data[0]);
        $scope.me = angular.copy(data.data[0]);
        $scope.me.next_pay_date = new Date($scope.me.next_pay_date);
        $scope.model.next_pay_date = $scope.me.next_pay_date;

        if ($scope.me.pay_recurrance_flag == "W"){
            $scope.model.selectedOption = {id: '1', value: "W",  name: 'Weekly'};
            $scope.me.selectedOption = {id: '1', value: "W",  name: 'Weekly'};
        }else if ($scope.me.pay_recurrance_flag =="B"){
            $scope.model.selectedOption = {id: '2', value: "B",  name: 'Bi-Weekly'};
            $scope.me.selectedOption = {id: '2', value: "B",  name: 'Bi-Weekly'};
        }else if ($scope.me.pay_recurrance_flag =="T"){
            $scope.model.selectedOption = {id: '3', value: "T",  name: 'Twice Monthly'};
            $scope.me.selectedOption = {id: '3', value: "T",  name: 'Twice Monthly'};
        }else if ($scope.me.pay_recurrance_flag =="M"){
            $scope.model.selectedOption = {id: '4', value: "M",  name: 'Monthly'};
            $scope.me.selectedOption = {id: '4', value: "M",  name: 'Monthly'};
        }
     });

    $scope.selections = [{name:'General', icon:'user'}, {name:'Paycheck', icon:'usd'}];
    $scope.selected = 'General';

    $scope.changeSelection = function (name) {
        console.log(name+" Has been selected");

        //Collapse all General tabs
        $scope.uUserNameCollapse = true;
        $scope.uNameCollapse = true;
        $scope.uPasswordCollapse = true;
        $scope.uEmailCollapse = true;

        //Collapse all Paycheck tabs
        $scope.uNextPayDate = true;
        $scope.uPayRecurrence = true;
        $scope.uAveragePaycheckAmount = true;


        //Collapse all Paycheck tabs
        $scope.selected = name;
    };

    $scope.toggleCollapse = function(toggleName){
        if ($scope.selected == "General"){
            if(toggleName == 'uUserNameCollapse'){
                $scope.uUserNameCollapse = !$scope.uUserNameCollapse;
                $scope.uNameCollapse = true;
                $scope.uPasswordCollapse = true;
                $scope.uEmailCollapse = true;
            }else if(toggleName == 'uNameCollapse'){
                $scope.uUserNameCollapse = true;
                $scope.uNameCollapse = !$scope.uNameCollapse;
                $scope.uPasswordCollapse = true;
                $scope.uEmailCollapse = true;
            }else if(toggleName == 'uPasswordCollapse'){
                $scope.uUserNameCollapse = true;
                $scope.uNameCollapse = true;
                $scope.uPasswordCollapse = !$scope.uPasswordCollapse;
                $scope.uEmailCollapse = true;
            }else if(toggleName == 'uEmailCollapse'){
                $scope.uUserNameCollapse = true;
                $scope.uNameCollapse = true;
                $scope.uPasswordCollapse = true;
                $scope.uEmailCollapse = !$scope.uEmailCollapse;
            }else if(!toggleName){
                $scope.uUserNameCollapse = true;
                $scope.uNameCollapse = true;
                $scope.uPasswordCollapse = true;
                $scope.uEmailCollapse = true;
            }
        }else if ($scope.selected == "Paycheck"){
            if(toggleName == 'uPayRecurrence'){
                $scope.uPayRecurrence = !$scope.uPayRecurrence;
                $scope.uNextPayDate = true;
                $scope.uAveragePaycheckAmount = true;
            }else if(toggleName == 'uNextPayDate'){
                $scope.uPayRecurrence = true;
                $scope.uNextPayDate = !$scope.uNextPayDate;
                $scope.uAveragePaycheckAmount = true
            }else if(toggleName == 'uAveragePaycheckAmount'){
                $scope.uPayRecurrence = true;
                $scope.uNextPayDate = true
                $scope.uAveragePaycheckAmount = !$scope.uAveragePaycheckAmount;
            }else if(!toggleName){
                $scope.uPayRecurrence = true;
                $scope.uNextPayDate = true;
                $scope.uAveragePaycheckAmount = true;
            }
        }
    }



    $scope.submitForm = function(toggleName){
         var data = {};
         data.id = $scope.me.id;
         if(toggleName == 'uUserNameCollapse'){
            notificationService.info('uUserNameCollapse');
            $scope.toggleCollapse(null);
         }else if(toggleName == 'uNameCollapse'){
            if($scope.model.first_name != $scope.me.first_name){
                data.first_name = $scope.model.first_name;
            }
            if($scope.model.last_name != $scope.me.last_name){
                data.last_name = $scope.model.last_name;
            }
            Me.update({userId: $scope.me.id}, JSON.stringify(data), function(data) {
                if(data.error == null){
                    $scope.me.first_name = $scope.model.first_name
                    $scope.me.last_name = $scope.model.last_name
                    notificationService.success("User Updated Successfully");
                    $scope.toggleCollapse(null);
                }else{
                    notificationService.error("Error: " + data.error);
                    $scope.model.first_name = $scope.me.first_name;
                    $scope.model.last_name = $scope.me.last_name;
                }
            }, function(error){
                console.log(error);
                notificationService.error("Error Saving User Updates '" + error.status + "': " + error.statusText);
                $scope.model.first_name = $scope.me.first_name;
                $scope.model.last_name = $scope.me.last_name;
            });
         }else if(toggleName == 'uPasswordCollapse'){

            if($scope.model.current_password && $scope.model.new_password && $scope.model.confirm_new_password){

                if($scope.model.new_password != $scope.model.confirm_new_password){
                    notificationService.error("New password and confirmation do not match");
                }else if($scope.model.new_password == $scope.model.current_password){
                    notificationService.error("New password must not be the same as the old password");
                }else{

                    data.current_password = $scope.model.current_password;
                    data.new_password = $scope.model.new_password;
                    data.confirm_new_password = $scope.model.confirm_new_password;
                    console.log(data);
                    Me.update({userId: $scope.me.id}, JSON.stringify(data), function(data) {
                        if(data.error == null){
                            notificationService.success("User Updated Successfully");
                            $scope.toggleCollapse(null);
                        }else{
                            notificationService.error("Error: " + data.error);
                            $scope.model.first_name = $scope.me.first_name;
                            $scope.model.last_name = $scope.me.last_name;
                        }
                    }, function(error){
                        console.log(error);
                        notificationService.error("Error Saving User Updates '" + error.status + "': " + error.statusText);
                        $scope.model.first_name = $scope.me.first_name;
                        $scope.model.last_name = $scope.me.last_name;
                    });
                }

            }else{
                notificationService.error("Please make sure all required fields are provided");
            }

         }else if(toggleName == 'uEmailCollapse'){
            notificationService.info('uEmailCollapse');
            $scope.toggleCollapse(null);
         }else if(toggleName == 'uPayRecurrence'){
            $scope.model.pay_recurrance_flag = $scope.model.selectedOption.value;
            if($scope.model.pay_recurrance_flag != $scope.me.pay_recurrance_flag){
                data.pay_recurrance_flag = $scope.model.pay_recurrance_flag;
            }
            Me.update({userId: $scope.me.id}, JSON.stringify(data), function(data) {
                if(data.error == null){
                    $scope.me.pay_recurrance_flag = $scope.model.pay_recurrance_flag;
                    $scope.me.selectedOption = $scope.model.selectedOption;

                    notificationService.success("User Updated Successfully");
                    $scope.toggleCollapse(null);
                }else{
                    notificationService.error("Error: " + data.error);
                    //TODO: Add logic to revert option to current
                    $scope.model.pay_recurrance_flag = $scope.me.pay_recurrance_flag;
                }
            }, function(error){
                console.log(error);
                notificationService.error("Error Saving User Updates '" + error.status + "': " + error.statusText);
                $scope.model.pay_recurrance_flag = $scope.me.pay_recurrance_flag;
            });
         }else if(toggleName == 'uNextPayDate'){
            if($scope.model.next_pay_date != $scope.me.next_pay_date){
                data.next_pay_date = $scope.model.next_pay_date;
            }
            Me.update({userId: $scope.me.id}, JSON.stringify(data), function(data) {
                if(data.error == null){
                    $scope.me.next_pay_date = $scope.model.next_pay_date
                    notificationService.success("User Updated Successfully");
                    $scope.toggleCollapse(null);
                }else{
                    notificationService.error("Error: " + data.error);
                    //TODO: Add logic to revert option to current
                    $scope.model.next_pay_date = $scope.me.next_pay_date;
                }
            }, function(error){
                console.log(error);
                notificationService.error("Error Saving User Updates '" + error.status + "': " + error.statusText);
                $scope.model.next_pay_date = $scope.me.next_pay_date;
            });
         }else if(toggleName == 'uAveragePaycheckAmount'){
            if($scope.model.average_paycheck_amount != $scope.me.average_paycheck_amount){
                data.average_paycheck_amount = $scope.model.average_paycheck_amount;
            }
            Me.update({userId: $scope.me.id}, JSON.stringify(data), function(data) {
                if(data.error == null){
                    $scope.me.average_paycheck_amount = $scope.model.average_paycheck_amount
                    notificationService.success("User Updated Successfully");
                    $scope.toggleCollapse(null);
                }else{
                    notificationService.error("Error: " + data.error);
                    //TODO: Add logic to revert option to current
                    $scope.model.average_paycheck_amount = $scope.me.average_paycheck_amount;
                }
            }, function(error){
                console.log(error);
                notificationService.error("Error Saving User Updates '" + error.status + "': " + error.statusText);
                $scope.model.average_paycheck_amount = $scope.me.average_paycheck_amount;
            });
         }
    }
}]);







/*********************************
* FEEDBACK FORM MODAL CONTROLLER *
*********************************/
menuBarAppControllers.controller('FeedbackFormModalController', ['$scope', '$modalInstance', 'notificationService', 'Feedback', function ($scope, $modalInstance, notificationService, Feedback) {

    $scope.model = {};
    $scope.title = "Submit Feedback"

    $scope.formFields = [
                            {
                                key: 'rating',
                                type: 'radio',
                                templateOptions: {
                                    label: 'Rating',
                                    "options": [
                                      {
                                        "name": "1 - Sad Panda",
                                        "value": "1"
                                      },
                                      {
                                        "name": "2",
                                        "value": "2"
                                      },
                                      {
                                        "name": "3",
                                        "value": "3"
                                      },
                                      {
                                        "name": "4",
                                        "value": "4"
                                      },
                                      {
                                        "name": "5 - Amazing!",
                                        "value": "5"
                                      }
                                    ]

                                }
                            },
                            {
                                key: 'feedback',
                                type: 'textarea',
                                templateOptions: {
                                    rows: 4,
                                    type: 'text',
                                    label: 'Feedback',
                                    required: true
                                }
                            }
                        ];


    $scope.submitModalForm = function() {
       console.log($scope.model);
       Feedback.create(JSON.stringify($scope.model), function(data) {
            if(data.error == null){
                $modalInstance.close();
                notificationService.success("Thank you for your feedback!");
            }else{
                notificationService.error("Error: "+data.error);
            }
       }, function(error){
            console.log(error);
            notificationService.error("Received error status '"+error.status+"': "+error.statusText);
           });
    };


  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };


}]);


