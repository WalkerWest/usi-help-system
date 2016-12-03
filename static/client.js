var helpApp = angular.module('helpApp',[]);
helpApp.controller('HelpController',function HelpController($scope) {

    $scope.trees = [
        { id: '1', name: 'Test #1'},
        { id: '2', name: 'Test #2'},
        { id: '3', name: 'Test #3'}
    ];

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

    $scope.children = [
        { id: 'A', name: 'Child A'},
        { id: 'B', name: 'Child B'},
        { id: 'C', name: 'Child C'}
    ];

    $scope.category = "";
    this.chooseCat = function() {
        console.log($scope.category);
        $.ajax({
            url: "/_getChildren",
            type: "GET",
            data: {id:$scope.category},
            success: function(data) {
                console.log("Got category children!");
                $scope.showSubcats = true;
                $scope.children.length=0;
                data.forEach(function(subcat) {
                    console.log(subcat.name)
                    $scope.children.push(subcat);
                })
                $scope.$apply();
            },
            error: function(err) {
                console.log("error:",err);
            }
        });
    }

    this.showSubcats = false;

});
