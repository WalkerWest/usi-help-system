var helpApp = angular.module('helpApp',[]);
helpApp.controller('HelpController',function HelpController($scope) {

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
        $.ajax({
            url: "/_getTrees",
            type: "GET",
            success: function(data) {
                console.log("Got data!");
                $scope.trees.length=0;
                data.forEach(function(tree) {
                    console.log(tree.name)
                    $scope.trees.push(tree);
                })
                $scope.$apply();
            },
            error: function(err) {
                console.log("error:",err);
            }
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

        $.ajax({
            url: "/_getChildren",
            type: "GET",
            data: {id:$scope.category},
            success: function(data) {
                console.log("Got category children!");
                var probStart=false;
                data.forEach(function(subcat) {
                    if(subcat.type!="category") {
                        probStart=true;
                    }
                })
                if(probStart) {
                    $scope.showCatDrop=false;
                    appendCat();
                    $scope.showSubcats = true;
                    $scope.children.length=0;
                    data.forEach(function(subcat) {
                        console.log(subcat.name)
                        $scope.children.push(subcat);
                    })
                } else {
                    $scope.showSubcats = false;
                    console.log("Ready to loop!; showCatDrop is "+$scope.showCatDrop);
                    for (var i in $scope.trees) {
                        if($scope.trees[i].id==$scope.category) {
                            $scope.chosenCats.push({id:$scope.category,name:$scope.trees[i].name});
                        }
                    }
                    if (data.length>0) {
                        $scope.trees.length=0;
                        data.forEach(function(tree) {
                            console.log(tree.name)
                            $scope.trees.push(tree);
                        })
                    } else $scope.showCatDrop=false;
                }
                $scope.$apply();
            },
            error: function(err) {
                console.log("error:",err);
            }
        });
    }

    this.showSubcats = false;

    this.getUser = function() {
        console.log($scope.category);
        $.ajax({
            url: "/_getUser",
            type: "GET",
            success: function(data) {
                console.log("Got username!");
                $scope.username = data.user;
                $scope.$apply();
            },
            error: function(err) {
                console.log("error:",err);
            }
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
        $scope.trees.lenth=0;
        getTrees();
    }

});