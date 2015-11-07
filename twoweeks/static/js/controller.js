'use strict';

var billsAppControllers = angular.module("billsAppControllers", []);
var loginAppControllers = angular.module("loginAppControllers", []);
var menuBarAppControllers = angular.module("menuBarAppControllers", []);



/***********************
* BILL PREP CONTROLLER *
************************/
billsAppControllers.controller("billFormController",['$scope', '$http', '$routeParams', '$location', 'Bill', '$modal', 'Me', 'PaymentPlan', 'PaymentPlanItem', 'ngToast', function($scope, $http, transformRequestAsFormPost, $location, Bill, $modal, Me, PaymentPlan, PaymentPlanItem, ngToast) {
    $scope.date = new Date();
    $scope.animationsEnabled = true
    $scope.paymentPlanBills = [];
    $scope.fundedBillsTotal = 0;

    $scope.disableSave = true;
    $scope.disableReset = true;
    $scope.disableExecute = true;


    $scope.editBill = function (index) {
        //console.log(index);
        //console.log($scope.bills.indexOf(index));
        var modalInstance = $modal.open({
          animation: $scope.animationsEnabled,
          templateUrl: '/static/partials/Prepare-EditBillModalForm.html',
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

    $scope.editPaymentPlanItem = function (item) {
        //console.log(index);
        //console.log($scope.bills.indexOf(index));
        var modalInstance = $modal.open({
          animation: $scope.animationsEnabled,
          templateUrl: '/static/partials/Prepare-EditPaymentPlanItemModalForm.html',
          controller: 'EditPaymentPlanItemModalController',
          resolve: {
            data: function () {
              return angular.copy($scope.paymentPlanBills[$scope.paymentPlanBills.indexOf(item)]);
            }
          }
        });

        modalInstance.result.then(function (newPaymentPlanItem) {
          angular.forEach($scope.paymentPlanBills,function(value,index){
            if($scope.paymentPlanBills[index].id == newPaymentPlanItem.id){
                $scope.paymentPlanBills.splice(index, 1);
            }
          });
          $scope.paymentPlanBills.push(newPaymentPlanItem);
          $scope.disableSave = false;
        }, function () {
          console.log('Modal dismissed at: ' + new Date());
        });
      };


    $scope.newBill = function () {
        //console.log(index);
        //console.log($scope.bills.indexOf(index));
        var modalInstance = $modal.open({
          animation: $scope.animationsEnabled,
          templateUrl: '/static/partials/Prepare-EditBillModalForm.html',
          controller: 'BillFormModalController',
          resolve: {
            data: function () {
              null;
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

        $scope.fld_account_balance_amount = $scope.me.account_balance_amount;
        $scope.account_balance_amount = $scope.me.account_balance_amount;

        $scope.setAccountBalance = function(){
            Me.update({userId: $scope.me.id}, JSON.stringify({"id":$scope.me.id, "account_balance_amount":$scope.fld_account_balance_amount}), function(data) {
                if(data.error == null){
                    ngToast.success("Account Balance Set");
                    $scope.account_balance_amount = data.data[0].account_balance_amount;
                    $scope.me.account_balance_amount = data.data[0].account_balance_amount;
                }else{
                    $scope.fld_account_balance_amount = $scope.me.account_balance_amount;
                    ngToast.danger("Error: " + data.error);
                }
            }, function(error){
                console.log(error);
                $scope.fld_account_balance_amount = $scope.me.account_balance_amount;
                ngToast.danger("Error Setting Account Balance '" + error.status + "': " + error.statusText);
            });
        }

        Bill.query({'paid_flag': false, 'funded_flag': false}, function(data) {
            $scope.bills = convertBillsToJSObjects(data.data);

            console.log('~~~Bills~~~');
            console.log($scope.bills);

            //GET HOW MANY AND MUCH BILLS THAT ARE FUNDED
            Bill.query({'paid_flag': false, 'funded_flag': true}, function(data) {
                var prepFundedBillsTotal = 0;
                console.log('~~~Checking for funded bills~~~')
                if(data.error == null){
                    console.log(data.data);

                    if (data.data.length > 0){
                        angular.forEach(data.data,function(value,index){
                            console.log("Adding $" + data.data[index].total_due + " to total");
                            prepFundedBillsTotal += data.data[index].total_due;
                        });
                    }
                }else{
                    ngToast.danger("Error: " + error.error);
                }
                $scope.fundedBillsTotal = prepFundedBillsTotal;
            },
            function (error){
                console.log(error);
                ngToast.danger('Error ' + error.status + ': ' + error.statusText);
            });


            PaymentPlan.query({accepted_flag:false, base_flag:false}, function(data){
                if(data.error == null){
                    $scope.paymentPlan = data.data;
                    console.log('~~~Payment Plans~~~');
                    console.log($scope.paymentPlan);
                    $scope.paymentPlan.transfer_date = new Date($scope.paymentPlan.transfer_date);
                    if ($scope.paymentPlan.accepted_flag == false && $scope.paymentPlan.base_flag == false){
                        $scope.ActivePaymentPlan = $scope.paymentPlan;
                        console.log('~~~Active Payment Plan~~~');
                        console.log($scope.paymentPlan);

                        if ($scope.ActivePaymentPlan.payment_plan_items.length >= 1){
                            $scope.disableExecute = false;
                        }

                        //Pushing any bills to ActivePaymentPlan object that are in users active payment plan
                        for(var i = $scope.ActivePaymentPlan.payment_plan_items.length; i--;){
                            for(var j = $scope.bills.length; j--;){
                                if($scope.bills[j].id == $scope.ActivePaymentPlan.payment_plan_items[i].bill_id){
                                    $scope.bills[j].amount = parseFloat($scope.ActivePaymentPlan.payment_plan_items[i].amount);
                                    $scope.paymentPlanBills.push($scope.bills[j]);
                                    $scope.bills.splice(j, 1);
                                }
                            }
                        }

                        if($scope.paymentPlanBills.length > 0){
                            $scope.disableExecute = false;
                        }

                        $scope.differenceBetweenBillAndPlan = function(paymentPlanBill){
                            return (paymentPlanBill.amount/getBillRemainingDue(paymentPlanBill))*100;
                        }

                    }
                }else{
                    ngToast.danger("Error: "+data.error);
                }
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

            $scope.addToPaymentPlan = function(bill){
                if(bill.amount == null){
                    bill.amount = parseFloat(getBillRemainingDue(bill));
                }
                $scope.paymentPlanBills.push(bill);
                $scope.bills.splice($scope.bills.indexOf(bill), 1);
                ngToast.create(bill.name+" added to Plan");

                $scope.disableSave = false;
                $scope.disableExecute = true;
                $scope.disableReset = false;
            }


            $scope.removeFromPaymentPlan = function(paymentPlanBill){
                $scope.bills.push(paymentPlanBill);
                $scope.paymentPlanBills.splice($scope.paymentPlanBills.indexOf(paymentPlanBill), 1);
                ngToast.create(paymentPlanBill.name+" removed from Plan");

                $scope.disableSave = false;
                $scope.disableExecute = true;
                $scope.disableReset = false;
            }


            $scope.resetBillPrep = function(){
                console.log("resetting");
                var deleteList = [];

                //Moving Payment Plan To Bills
                for(var i = $scope.paymentPlanBills.length; i--;){
                    var found = false;
                    for(var j = 0; j < $scope.ActivePaymentPlan.payment_plan_items.length; j++){
                        if($scope.paymentPlanBills[i].id == $scope.ActivePaymentPlan.payment_plan_items[j].bill_id){
                            found = true;
                        }
                    }
                    if (!found){
                        $scope.bills.push($scope.paymentPlanBills[i]);
                        $scope.paymentPlanBills.splice(i, 1);
                    }
                }

                //Moving Bills to Payment Plan
                for(var i = $scope.bills.length; i--;){
                    var found = false;
                    for(var j = 0; j < $scope.ActivePaymentPlan.payment_plan_items.length; j++){
                        if($scope.bills[i].id == $scope.ActivePaymentPlan.payment_plan_items[j].bill_id){
                            found = true;
                        }
                    }
                    if (found){
                        $scope.paymentPlanBills.push($scope.bills[i]);
                        $scope.bills.splice(i, 1);
                    }
                }
                $scope.amount = paymentPlanTotal();

                ngToast.info("Plan Reset");

                $scope.disableSave = true;

                if($scope.paymentPlanBills.length > 0){
                    $scope.disableExecute = false;
                }else{
                    $scope.disableExecute = true;
                }

                $scope.disableReset = true;
            }


         });
     });

    $scope.savePaymentPlan = function(){
        savePaymentPlan();
    }


    function savePaymentPlan(){
        console.log('Saving Payment Plan');
        var paymentPlanItems = [];
        //ngToast.info('Saving payment plan')

        angular.forEach($scope.paymentPlanBills,function(value,index){
            var paymentPlanItem = {bill_id: $scope.paymentPlanBills[index].id, user_id:$scope.me.id, amount:$scope.paymentPlanBills[index].amount};
            console.log(paymentPlanItem);
            paymentPlanItems.push(paymentPlanItem);
        });
        console.log(paymentPlanItems);

        PaymentPlan.update({'payment_plan_id': $scope.ActivePaymentPlan.id}, JSON.stringify({'payment_plan_items':paymentPlanItems, 'amount':paymentPlanTotal()}), function(data){
            if(data.error == null){
                 if(data.data == null){
                    ngToast.danger('No Data');
                    //TODO: UPDATE buttons (Execute/Save/Reset);
                 }else{
                    console.log(data.data);
                    ngToast.success("Plan Saved");
                    $scope.ActivePaymentPlan = data.data;
                    $scope.disableSave = true;

                    if ($scope.paymentPlanBills.length >= 1){
                        $scope.disableExecute = false;
                    }else{
                        $scope.disableExecute = true;
                    }

                    $scope.disableReset = true;
                 }
            }else{
                ngToast.danger('Error: ' + data.error);
            }
        });
    }

    $scope.getBillRemainingDue = function(bill){
       return getBillRemainingDue(bill);
    }

    function paymentPlanTotal(){
        var total = 0;
        if($scope.paymentPlanBills.length > 0){
            for(var i = 0; i < $scope.paymentPlanBills.length; i++){
                if($scope.paymentPlanBills[i].amount){
                    total += parseFloat($scope.paymentPlanBills[i].amount);
                }
            }
        }
        return total;
    }

    $scope.paymentPlanTotal = function(){
        return  paymentPlanTotal();
    };

    $scope.paymentPlanBalance = function(){
        var total = 0;
        if($scope.paymentPlanBills.length > 0){
            for(var i = 0; i < $scope.paymentPlanBills.length; i++){
                if($scope.paymentPlanBills[i].amount){
                    total += parseFloat($scope.paymentPlanBills[i].amount);
                }
            }
        }
        return $scope.account_balance_amount - (total + $scope.fundedBillsTotal);
    };

    $scope.executePaymentPlan = function() {
        if ($scope.paymentPlanBills.length > 0){
            console.log('Saving Payment Plan');
            var paymentPlanItems = [];
            //ngToast.info('Saving payment plan')

            angular.forEach($scope.paymentPlanBills,function(value,index){
                var paymentPlanItem = {bill_id: $scope.paymentPlanBills[index].id, user_id:$scope.me.id, amount:$scope.paymentPlanBills[index].amount};
                console.log(paymentPlanItem);
                paymentPlanItems.push(paymentPlanItem);
            });
            console.log(paymentPlanItems);
            PaymentPlan.update({'payment_plan_id': $scope.ActivePaymentPlan.id}, JSON.stringify({'payment_plan_items':paymentPlanItems}), function(data){
                if(data.error == null){
                     if(data.data == null){
                        ngToast.danger('No Data');
                     }else{
                        console.log(data.data);
                        $scope.ActivePaymentPlan = data.data;


                        $scope.ActivePaymentPlan.accepted_flag = true;
                        PaymentPlan.update({'payment_plan_id': $scope.ActivePaymentPlan.id}, JSON.stringify($scope.ActivePaymentPlan), function(data){
                            if(data.error == null){
                                 if(data.data == null){
                                    ngToast.danger('No Data');
                                 }else{
                                    console.log(data.data);
                                    ngToast.success("Plan Saved");
                                    window.location.href = '/home/';
                                 }
                            }else{
                                ngToast.danger('Error: ' + data.error);
                            }
                        }, function(error){
                            console.log(error);
                            ngToast.danger('Error ' + error.status + ': ' + error.statusText);
                        });
                     }
                }else{
                    ngToast.danger('Error: ' + data.error);
                }
            }, function(data){
                ngToast.danger('Error ' + error.status + ': ' + error.statusText);
            });
        }else{
            ngToast.warning('You must select a bill to pay to execute a funding plan')
        }
    }

    $scope.submit = function() {
       var data = $scope.bill;
       console.log(data);
       Bill.save(JSON.stringify(data), function(data) {
            console.log(data);
            $scope.bills.push(data.data);
            ngToast.create("Bill Created");
       });
    };

    $scope.deleteBill = function(index, $window, $location) {
       //TODO: Add logic to check for already approved bill payment items
       //TODO: Add logic to delete bill pay items
       console.log('attempting to delete bill index #'+index);
       var data = $scope.bills[$scope.bills.indexOf(index)];
       Bill.delete({billId: data.id}, function(data) {
        $scope.bills.splice($scope.bills.indexOf(index), 1);
        ngToast.create("Bill Deleted");
       });
    };

    $scope.differenceInDays = function(first_date) {
        return differenceInDays(first_date);
    };
}]);



/**************************
* BILL EXECUTE CONTROLLER *
***************************/
billsAppControllers.controller("billExecuteController",['$scope', '$http', '$routeParams', '$location', 'Bill', '$modal', 'Me', 'PaymentPlan', 'PaymentPlanItem', 'ngToast', function($scope, $http, transformRequestAsFormPost, $location, Bill, $modal, Me, PaymentPlan, PaymentPlanItem, ngToast) {

    $scope.date = new Date();
    $scope.animationsEnabled = true
    $scope.paymentPlanBills = [];

    $scope.editBill = function (index) {
        //console.log(index);
        //console.log($scope.bills.indexOf(index));
        var modalInstance = $modal.open({
          animation: $scope.animationsEnabled,
          templateUrl: '/static/partials/Prepare-EditBillModalForm.html',
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

    $scope.editPaymentPlanItem = function (item) {
        //console.log(index);
        //console.log($scope.bills.indexOf(index));
        var modalInstance = $modal.open({
          animation: $scope.animationsEnabled,
          templateUrl: '/static/partials/Prepare-EditPaymentPlanItemModalForm.html',
          controller: 'EditPaymentPlanItemModalController',
          resolve: {
            data: function () {
              return angular.copy($scope.paymentPlanBills[$scope.paymentPlanBills.indexOf(item)]);
            }
          }
        });

        modalInstance.result.then(function (newPaymentPlanItem) {
          angular.forEach($scope.paymentPlanBills,function(value,index){
            if($scope.paymentPlanBills[index].id == newPaymentPlanItem.id){
                $scope.paymentPlanBills.splice(index, 1);
            }
          });
          $scope.paymentPlanBills.push(newPaymentPlanItem);
          $scope.disableSave = false;
        }, function () {
          console.log('Modal dismissed at: ' + new Date());
        });
      };


    Me.query(function(data) {
        $scope.me = angular.copy(data.data[0]);
        $scope.me.next_pay_date = new Date($scope.me.next_pay_date);



        PaymentPlan.query({accepted_flag:false, base_flag:false}, function(data){
            if(data.error == null){
                $scope.paymentPlan = data.data;
                console.log('~~~Payment Plans~~~');
                console.log($scope.paymentPlan);
                $scope.paymentPlan.transfer_date = new Date($scope.paymentPlan.transfer_date);
            }else{
                ngToast.danger("Error: "+data.error);
            }
        });

        Bill.query({'paid_flag': false, 'funded_flag': true}, function(data) {
            $scope.bills = convertBillsToJSObjects(data.data);

            console.log('~~~Bills~~~');
            console.log($scope.bills);


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

            $scope.addToProcessed = function(bill){
                Bill.update({billId: bill.id}, {id:bill.id, payment_processing_flag:true}, function(data) {
                    if(data.error == null){
                        bill.payment_processing_flag = true
                        ngToast.success("Bill '"+bill.name+"' set as processing");
                    }else{
                        ngToast.danger("Error: "+data.error);
                    }
                }, function(error){
                    console.log(error);
                    ngToast.danger("Received error status '"+error.status+"': "+error.statusText);
                   });
            }


            $scope.removeFromProcessed = function(bill){
                Bill.update({billId: bill.id}, {id:bill.id, payment_processing_flag:false}, function(data) {
                    if(data.error == null){
                        bill.payment_processing_flag = false
                        ngToast.success("Bill '"+bill.name+"' removed from processed");
                    }else{
                        ngToast.danger("Error: "+data.error);
                    }
                }, function(error){
                    console.log(error);
                    ngToast.danger("Received error status '"+error.status+"': "+error.statusText);
                });
            }

            $scope.fundedBillsTotal = function(){
                var tmpAmount = 0;

                angular.forEach($scope.bills,function(value,index){
                    if ($scope.bills[index].payment_processing_flag == false){
                        tmpAmount += $scope.bills[index].total_due;
                    }
                });
                return tmpAmount;
            }

            $scope.processedBillsTotal = function(){
                var tmpAmount = 0;
                angular.forEach($scope.bills,function(value,index){
                    if ($scope.bills[index].payment_processing_flag == true){
                        tmpAmount += $scope.bills[index].total_due;
                    }
                });
                return tmpAmount;
            }

            $scope.payBill = function(bill){
                Bill.update({billId: bill.id}, {id:bill.id, paid_flag:true}, function(data) {
                    if(data.error == null){
                        $scope.bills.splice($scope.bills.indexOf(bill), 1);
                        ngToast.success("Bill '"+bill.name+"' marked as paid!");
                    }else{
                        ngToast.danger("Error: "+data.error);
                    }
                }, function(error){
                    console.log(error);
                    ngToast.danger("Received error status '"+error.status+"': "+error.statusText);
                });

            }

         });
     });


    $scope.deletePaymentPlanItem = function(index, $window, $location) {
       //TODO: Add logic to check for already approved bill payment items
       //TODO: Add logic to delete bill pay items
       console.log('Attempting to unfund Bill '+index.name);
       var data = $scope.bills[$scope.bills.indexOf(index)];
       PaymentPlanItem.delete({payment_plan_id: null, bill_id:data.id}, function(data) {
           if(data.error == null){
                $scope.bills.splice($scope.bills.indexOf(index), 1);
                ngToast.create("Bill has been unfunded");
           }else{
                ngToast.danger("Error: "+ data.error);
           }
       },
       function (error){
        console.log(error);
        ngToast.danger('Error ' + error.status + ': ' + error.statusText);
       });
    };

    $scope.differenceInDays = function(first_date) {
        return differenceInDays(first_date);
    };
}]);



/*****************************
* BILL FORM MODAL CONTROLLER *
******************************/
billsAppControllers.controller('BillFormModalController', ['$scope', '$modalInstance', 'Bill', 'data', 'ngToast', 'PaymentPlan', function ($scope, $modalInstance, Bill, data, ngToast, PaymentPlan) {
    var action = 'new';

    $scope.showPaymentPlans = false;
    $scope.showRemainingDue = false;
    console.log(data.funded_flag);

    if(data != null){
        var action = 'edit';
        $scope.title = "Edit Bill"
        $scope.model = data;
        $scope.model.due_date = new Date(data.due_date);
        $scope.model.remaining_due = getBillRemainingDue(data);

        PaymentPlan.query({accepted_flag:true, base_flag:false, bill_id:data.id}, function(data){
            if(data.error == null){

                $scope.paymentPlans = data.data;
                if($scope.paymentPlans.length > 0){
                    angular.forEach($scope.paymentPlans,function(value,index){
                        $scope.paymentPlans[index].transfer_date = new Date($scope.paymentPlans[index].transfer_date);
                    });

                    $scope.showPaymentPlans = true;

                    if(data.funded_flag == "false"){
                        $scope.showRemainingDue = true;
                    }
                }

                $scope.getPaymentPlanItemAmount = function(paymentPlan, bill_id){
                    var amount = 0;
                    angular.forEach(paymentPlan.payment_plan_items,function(value,index){
                        if(paymentPlan.payment_plan_items[index].bill_id == bill_id){
                            amount = paymentPlan.payment_plan_items[index].amount;
                        }
                    });
                    return amount;
                }


            }else{
               ngToast.danger("Error: "+data.error);
            }
        }, function(error){
            console.log(error);
            ngToast.danger("Received error status '"+error.status+"': "+error.statusText);
        });


    }else{
        $scope.title = "Create New Bill"
        $scope.model = {};
        $scope.model.payment_type_ind = "M";
    }


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
                    ngToast.success("Bill Updated");
                }else{
                    ngToast.danger("Error: "+data.error);
                }
           }, function(error){
                console.log(error);
                ngToast.danger("Received error status '"+error.status+"': "+error.statusText);
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
                    ngToast.create("Bill Added");
                }else{
                    ngToast.danger("Error: "+data.error);
                }
           }, function(error){
                console.log(error);
                ngToast.danger("Received error status '"+error.status+"': "+error.statusText);
                $scope.bill = backup;
               });
        }

    };



    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };


}]);



/*************************************
* EDIT PAYMENT PLAN MODAL CONTROLLER *
*************************************/
billsAppControllers.controller('EditPaymentPlanItemModalController', ['$scope', '$modalInstance', 'PaymentPlanItem', 'data', 'ngToast', function ($scope, $modalInstance, PaymentPlanItem, data, ngToast) {
    var action = 'new';

    $scope.title = "Edit Payment Plan Item"

    $scope.model = data;
    $scope.model.total_due = parseFloat($scope.model.total_due);
    $scope.model.amount = parseFloat($scope.model.amount);


    $scope.addTenPercent = function(){
        var tenPercent = Math.round(($scope.model.remaining_due/10)*100)/100;
        if((tenPercent + $scope.model.amount) >= $scope.model.remaining_due){
            $scope.model.amount = $scope.model.remaining_due;
        }else{
            $scope.model.amount = Math.round(($scope.model.amount + tenPercent)*100)/100;
        }
    }

    $scope.makeAmountTotal = function(){
        $scope.model.amount = $scope.model.remaining_due;
    }

    $scope.model.remaining_due = getBillRemainingDue(data);


    $scope.subtractTenPercent = function(){
        var tenPercent = Math.round(($scope.model.remaining_due/10)*100)/100;
        if(($scope.model.amount - tenPercent) <= 0){
            $scope.model.amount = 0
        }else{
            $scope.model.amount = Math.round(($scope.model.amount - tenPercent)*100)/100;
        }
    }

    $scope.differencePercent = function() {
       return Math.floor(($scope.model.amount/$scope.model.remaining_due)*100);

    }

     $scope.differenceInAmount = function() {
       return $scope.model.remaining_due - $scope.model.amount;
    };

    $scope.submitModalForm = function(data) {
       //console.log($scope.model);
       $scope.model.amount = parseFloat($scope.model.amount);
       $scope.model.amount = Math.floor($scope.model.amount*100)/100;
       $modalInstance.close($scope.model);
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };


}]);



/*******************
* LOGIN CONTROLLER *
*******************/
loginAppControllers.controller("loginAppLoginController",['$scope', '$routeParams', '$location', 'Login', 'ngToast', 'LoginCheck', function($scope, transformRequestAsFormPost, $location, Login, ngToast, LoginCheck) {

    LoginCheck.get(function(data) {
        console.log(data);
        if(data.error == null && data.data != null){
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
             ngToast.create("Please Enter username and password")
        }else{
            Login.save(JSON.stringify({username: $scope.model.username, password: $scope.model.password}), function(data){
                console.log(data)
                if(data.error == null){
                    window.location.href = '/home/';
                }else{
                    ngToast.danger(data.error);
                    console.log(data.error);
                }
            });
        }
    }
}]);



/**********************
* REGISTER CONTROLLER *
**********************/
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



/**************************
* MENU BAR APP CONTROLLER *
**************************/
menuBarAppControllers.controller('menuBarAppController',['$scope', '$http', '$location', '$modal', 'Me', 'Feedback', 'ngToast', '$cookies', function($scope, $http, $location, $modal, Me, Feedback, ngToast, $cookies) {

    $scope.isActive = function (viewLocation) {
        return viewLocation === $location.path();
    };
    console.log('~~~Cookie~~~');
    console.log($cookies.getAll());
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
                    ngToast.danger('Could not logout')
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



/**************************
* USER ACCOUNT CONTROLLER *
**************************/
menuBarAppControllers.controller('userAccountController',['$scope', '$http', '$location', '$modal', 'Me', 'ngToast', function($scope, $http, $location, $modal, Me, ngToast) {
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
            ngToast.create('uUserNameCollapse');
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
                    ngToast.success("User Updated Successfully");
                    $scope.toggleCollapse(null);
                }else{
                    ngToast.danger("Error: " + data.error);
                    $scope.model.first_name = $scope.me.first_name;
                    $scope.model.last_name = $scope.me.last_name;
                }
            }, function(error){
                console.log(error);
                ngToast.danger("Error Saving User Updates '" + error.status + "': " + error.statusText);
                $scope.model.first_name = $scope.me.first_name;
                $scope.model.last_name = $scope.me.last_name;
            });
         }else if(toggleName == 'uPasswordCollapse'){

            if($scope.model.current_password && $scope.model.new_password && $scope.model.confirm_new_password){

                if($scope.model.new_password != $scope.model.confirm_new_password){
                    ngToast.warning("New password and confirmation do not match");
                }else if($scope.model.new_password == $scope.model.current_password){
                    ngToast.warning("New password must not be the same as the old password");
                }else{

                    data.current_password = $scope.model.current_password;
                    data.new_password = $scope.model.new_password;
                    data.confirm_new_password = $scope.model.confirm_new_password;
                    console.log(data);
                    Me.update({userId: $scope.me.id}, JSON.stringify(data), function(data) {
                        if(data.error == null){
                            ngToast.success("User Updated Successfully");
                            $scope.toggleCollapse(null);
                        }else{
                            ngToast.danger("Error: " + data.error);
                            $scope.model.first_name = $scope.me.first_name;
                            $scope.model.last_name = $scope.me.last_name;
                        }
                    }, function(error){
                        console.log(error);
                        ngToast.danger("Error Saving User Updates '" + error.status + "': " + error.statusText);
                        $scope.model.first_name = $scope.me.first_name;
                        $scope.model.last_name = $scope.me.last_name;
                    });
                }

            }else{
                ngToast.create("Please make sure all required fields are provided");
            }

         }else if(toggleName == 'uEmailCollapse'){
            ngToast.success('uEmailCollapse');
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

                    ngToast.create("User Updated Successfully");
                    $scope.toggleCollapse(null);
                }else{
                    ngToast.create("Error: " + data.error);
                    //TODO: Add logic to revert option to current
                    $scope.model.pay_recurrance_flag = $scope.me.pay_recurrance_flag;
                }
            }, function(error){
                console.log(error);
                ngToast.danger("Error Saving User Updates '" + error.status + "': " + error.statusText);
                $scope.model.pay_recurrance_flag = $scope.me.pay_recurrance_flag;
            });
         }else if(toggleName == 'uNextPayDate'){
            if($scope.model.next_pay_date != $scope.me.next_pay_date){
                data.next_pay_date = $scope.model.next_pay_date;
            }
            Me.update({userId: $scope.me.id}, JSON.stringify(data), function(data) {
                if(data.error == null){
                    $scope.me.next_pay_date = $scope.model.next_pay_date
                    ngToast.success("User Updated Successfully");
                    $scope.toggleCollapse(null);
                }else{
                    ngToast.create("Error: " + data.error);
                    //TODO: Add logic to revert option to current
                    $scope.model.next_pay_date = $scope.me.next_pay_date;
                }
            }, function(error){
                console.log(error);
                ngToast.danger("Error Saving User Updates '" + error.status + "': " + error.statusText);
                $scope.model.next_pay_date = $scope.me.next_pay_date;
            });
         }else if(toggleName == 'uAveragePaycheckAmount'){
            if($scope.model.average_paycheck_amount != $scope.me.average_paycheck_amount){
                data.average_paycheck_amount = $scope.model.average_paycheck_amount;
            }
            Me.update({userId: $scope.me.id}, JSON.stringify(data), function(data) {
                if(data.error == null){
                    $scope.me.average_paycheck_amount = $scope.model.average_paycheck_amount
                    ngToast.success("User Updated Successfully");
                    $scope.toggleCollapse(null);
                }else{
                    ngToast.create("Error: " + data.error);
                    //TODO: Add logic to revert option to current
                    $scope.model.average_paycheck_amount = $scope.me.average_paycheck_amount;
                }
            }, function(error){
                console.log(error);
                ngToast.danger("Error Saving User Updates '" + error.status + "': " + error.statusText);
                $scope.model.average_paycheck_amount = $scope.me.average_paycheck_amount;
            });
         }
    }
}]);




/*********************************
* FEEDBACK FORM MODAL CONTROLLER *
*********************************/
menuBarAppControllers.controller('FeedbackFormModalController', ['$scope', '$modalInstance', 'ngToast', 'Feedback', function ($scope, $modalInstance, ngToast, Feedback) {

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
                ngToast.create("Thank you for your feedback!");
            }else{
                ngToast.danger("Error: "+data.error);
            }
       }, function(error){
            console.log(error);
            ngToast.create("Received error status '"+error.status+"': "+error.statusText);
           });
    };


  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };


}]);



//Global function to help with getting updated bill amounts
function getBillRemainingDue(bill){
    if(bill != null && bill.payment_plan_items != null && bill.payment_plan_items.length > 0){
        //console.log('getting Remaining due for: ' + bill.name);
        //console.log(bill);
        var adjusted_total_due = 0;
        angular.forEach(bill.payment_plan_items,function(value,index){
            if(bill.payment_plan_items[index].accepted_flag == true){
                adjusted_total_due += bill.payment_plan_items[index].amount;
            }
        });
        return Math.floor((bill.total_due - adjusted_total_due)*100)/100;
    }else{
        return Math.floor(bill.total_due*100)/100;
    }
}


//Global function calculate the differene in days
function differenceInDays(first_date) {
    var today = new Date();
    var millisecondsPerDay = 1000 * 60 * 60 * 24;
    var millisBetween = first_date.getTime() - today.getTime();
    var days = millisBetween / millisecondsPerDay;
    return Math.floor(days);
};


//Global function to process bills and convert object types
function convertBillsToJSObjects(bills){
    var newBillsList = [];
    angular.forEach(bills,function(value,index){
        newBillsList.push(convertBillToJSObjects(bills[index]));
    });

    return newBillsList;
}

//Global function to process bills and convert object types
function convertBillToJSObjects(bill){
    bill.due_date = new Date(bill.due_date);
    bill.total_due = parseFloat(bill.total_due);
    bill.amount = parseFloat(getBillRemainingDue(bill));

    if(bill.payment_processing_flag == "true" || bill.payment_processing_flag == true){
        bill.payment_processing_flag = true;
    }else {
        bill.payment_processing_flag = false;
    }

    if(bill.funded_flag == "true" || bill.funded_flag == true){
        bill.funded_flag = true;
    }else {
        bill.funded_flag = false;
    }
    return bill;
}
