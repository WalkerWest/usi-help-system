//var helpApp = angular.module('helpApp',['ngMaterial']);
//angular.module('helpApp',['ngAnimate','ngSanitize','ui.bootstrap','ngMaterial']);
//angular.module('helpApp',['ngAnimate','ngSanitize','ui.bootstrap','ngMaterial']);
angular.module('helpApp',['ngMaterial']);
var helpApp=angular.module('helpApp');
helpApp.controller('HelpController',function HelpController($scope,$mdDialog,$http) {

    /*
    $scope.chosenCats = [
        { id: "i", name: 'Cat I'},
        { id: "ii", name: 'Cat II'}
    ]
    */

    $scope.chosenCats = []

    $scope.trees = [
        { id: '1', name: 'Test #1'},
        { id: '2', name: 'Test #2'},
        { id: '3', name: 'Test #3'}
    ];

    getTrees();

    function getTrees() {
        $http({
            url: "/_getTrees",
            method: "GET"
        }).then(function successCallback(response) {
                console.log("Got data!");
                $scope.trees.length=0;
                $scope.trees.push({ id: '0', name: ''})
                $scope.category=$scope.trees[0].id;
                response.data.forEach(function(tree) {
                    console.log(tree.name)
                    $scope.trees.push(tree);
                })
                //$scope.$apply();

        },function errorCallback(response) {
                console.log("error:",response);
        });
    }

    $scope.children = [
        { id: 'A', name: 'Child A'},
        { id: 'B', name: 'Child B'},
        { id: 'C', name: 'Child C'}
    ];

    $scope.showCatDrop = true;

    function appendCat() {
        for (var i in $scope.trees) {
            if($scope.trees[i].id==$scope.category) {
                $scope.chosenCats.push({id:$scope.category,name:$scope.trees[i].name});
            }
        }
    }

    $scope.category = "";
    this.chooseCat = function() {
        console.log($scope.category);
        if($scope.category!=0) {
            $http({
                url: "/_getChildren",
                method: "GET",
                params: {id:$scope.category}
            }).then(function successCallback(response) {
                console.log("Got category children!");
                var probStart=false;
                response.data.forEach(function(subcat) {
                    if(subcat.type!="category") probStart=true;
                })
                if(probStart) {
                    $scope.showCatDrop=false;
                    appendCat();
                    $scope.showSubcats = true;
                    $scope.children.length=0;
                    response.data.forEach(function(subcat) {
                        console.log(subcat.name)
                        $scope.children.push(subcat);
                    })
                } else {
                    $scope.showSubcats = false;
                    console.log("Ready to loop!; showCatDrop is "+$scope.showCatDrop);
                    for (var i in $scope.trees) {
                        console.log($scope.trees[i].name);
                        if($scope.trees[i].id==$scope.category) {
                            $scope.chosenCats.push({id:$scope.category,name:$scope.trees[i].name});
                        }
                    }
                    console.log(response.data);
                    if (response.data.length>0) {
                        $scope.trees.length=0;
                        $scope.trees.push({ id: '0', name: ''})
                        $scope.category=$scope.trees[0].id;
                        response.data.forEach(function(tree) {
                            console.log(tree.name)
                            $scope.trees.push(tree);
                        })
                    } else $scope.showCatDrop=false;
                }
                // $scope.$apply();
                $scope.$
            },function errorCallback(responose) {
                console.log("error:",response);
            });

        }
    }

    this.showSubcats = false;

    this.getUser = function() {
        console.log($scope.category);
        $http({
            url: "/_getUser",
            method: "GET"
        }).then(function successCallback(response) {
            console.log("Got username!");
            $scope.username = response.data.user;
            //$scope.$apply();
        },function errorCallback(responose) {
            console.log("error:",response);
        });
    }

    $scope.username = this.getUser();

    this.openCreateCat = function() {
        console.log("Opening createCat");
        $dialog.dialog({}).open('');
    }

    this.resetCats = function() {
        console.log("Reset button pushed!");
        $scope.chosenCats.length=0;
        $scope.children.length=0;
        $scope.showCatDrop=true;
        $scope.showSubcats=false;
        $scope.trees.length=0;
        $scope.formCat.$setPristine();
        //$scope.trees.push({id:'? string: ?',name:''});
        //$scope.model='';
        getTrees();
    }

    /***************************************************************************
     * DIALOG STUFF                                                            *
     ***************************************************************************/

    $scope.status = '  ';
    $scope.customFullscreen = false;

    $scope.showAlert = function(ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        // Modal dialogs should fully cover application
        // to prevent interaction outside of dialog
        $mdDialog.show(
          $mdDialog.alert()
            .parent(angular.element(document.querySelector('#popupContainer')))
            .clickOutsideToClose(true)
            .title('This is an alert title')
            .textContent('You can specify some description text in here.')
            .ariaLabel('Alert Dialog Demo')
            .ok('Got it!')
            .targetEvent(ev)
        );
    };

    $scope.showConfirm = function(ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.confirm()
              .title('Would you like to delete your debt?')
              .textContent('All of the banks have agreed to forgive you your debts.')
              .ariaLabel('Lucky day')
              .targetEvent(ev)
              .ok('Please do it!')
              .cancel('Sounds like a scam');

        $mdDialog.show(confirm).then(function() {
          $scope.status = 'You decided to get rid of your debt.';
        }, function() {
          $scope.status = 'You decided to keep your debt.';
        });
    };

    $scope.showPrompt = function(ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.prompt()
          .title('What would you name your dog?')
          .textContent('Bowser is a common name.')
          .placeholder('Dog name')
          .ariaLabel('Dog name')
          .initialValue('Buddy')
          .targetEvent(ev)
          .ok('Okay!')
          .cancel('I\'m a cat person');

        $mdDialog.show(confirm).then(function(result) {
          $scope.status = 'You decided to name your dog ' + result + '.';
        }, function() {
          $scope.status = 'You didn\'t name your dog.';
        });
    };

    $scope.showAdvanced = function(ev) {
        $mdDialog.show({
          controller: DialogController,
          templateUrl: 'dialog1.tmpl.html',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose:true,
          fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
        })
        .then(function(answer) {
          $scope.status = 'You said the information was "' + answer + '".';
        }, function() {
          $scope.status = 'You cancelled the dialog.';
        });
    };

    $scope.showTabDialog = function(ev) {
        $mdDialog.show({
          controller: DialogController,
          templateUrl: 'tabDialog.tmpl.html',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose:true
        })
            .then(function(answer) {
              $scope.status = 'You said the information was "' + answer + '".';
            }, function() {
              $scope.status = 'You cancelled the dialog.';
            });
    };

    $scope.showPrerenderedDialog = function(ev) {
        $mdDialog.show({
          controller: DialogController,
          contentElement: '#myDialog',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose: true
        });
    };

    function DialogController($scope, $mdDialog) {
        $scope.hide = function() {
          $mdDialog.hide();
        };
        $scope.cancel = function() {
          $mdDialog.cancel();
        };
        $scope.answer = function(answer) {
          $mdDialog.hide(answer);
        };
    }

});
