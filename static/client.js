//var helpApp = angular.module('helpApp',['ngMaterial']);
//angular.module('helpApp',['ngAnimate','ngSanitize','ui.bootstrap','ngMaterial']);
//angular.module('helpApp',['ngAnimate','ngSanitize','ui.bootstrap','ngMaterial']);
angular.module('helpApp',['ngMaterial']);
var helpApp=angular.module('helpApp');

helpApp.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('//').endSymbol('//');
})

helpApp.controller('HelpController',function HelpController($scope,$mdDialog,$http) {

    /*
    $scope.chosenCats = [
        { id: "i", name: 'Cat I'},
        { id: "ii", name: 'Cat II'}
    ]
    */

    $scope.chosenCats = []
    $scope.chosenSubcats = []

    $scope.trees = [
        { id: '1', name: 'Test #1'},
        { id: '2', name: 'Test #2'},
        { id: '3', name: 'Test #3'}
    ];

    getTrees();

    function paintTree(response) {
        console.log("Got data!");
        $scope.trees.length=0;
        $scope.trees.push({ id: '0', name: ''})
        $scope.category=$scope.trees[0].id;
        response.data.forEach(function(tree) {
            console.log(tree.name)
            $scope.trees.push(tree);
        })
        //$scope.$apply();
    }

    function getTrees() {
        $http({
            url: "/_getTrees",
            method: "GET"
        }).then(function successCallback(response) {
            paintTree(response);
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
    $scope.showSubcatDrop = false;

    function appendCat() {
        for (var i in $scope.trees) {
            if($scope.trees[i].id==$scope.category) {
                $scope.chosenCats.push({id:$scope.category,name:$scope.trees[i].name});
            }
        }
    }

    $scope.partStart=false;
    $scope.probStart=false;
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
                response.data.forEach(function(subcat) {
                    if(subcat.type=="problem") $scope.probStart=true;
                    else if (subcat.type=="part") $scope.partStart=true;
                })
                if($scope.probStart || $scope.partStart) {
                    $scope.showCatDrop=false;
                    $scope.showSubcatDrop=true;
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
            },function errorCallback(response) {
                console.log("error:",response);
            });

        }
    }

    this.chooseSubcat = function(myId) {
        if(myId==null) myId=$scope.subcat;
        console.log(myId);
        if(myId!=0) {
            $http({
                url: "/_getChildren",
                method: "GET",
                params: {id:myId}
            }).then(function successCallback(response) {
                console.log("Got subcat children!");
                console.log("The subcat length is "+response.data.length)
                if(response.data.length==0) {
                    console.log("Turning off the subcat drop!");
                    $scope.showSubcatDrop=false;
                    if($scope.probStart)$scope.showSurrender();
                    else {
                        for (var i in $scope.children) {
                            if($scope.children[i].id==myId) {
                                $scope.showPartBox($scope.children[i]);
                            }
                        }
                    }
                    //$scope.$apply();
                }
                for (var i in $scope.children) {
                    if($scope.children[i].id==myId) {
                        $scope.chosenSubcats.push({id:myId,name:$scope.children[i].name});
                    }
                }

                $scope.children.length=0;
                response.data.forEach(function(subcat) {
                    console.log(subcat.name)
                    $scope.children.push(subcat);
                })

            },function errorCallback(response) {
                console.log("error:",response);
            });

        }
    }

    this.showSubcats = false;

    $scope.createRoot = function(myName) {
        if(myName==null)
            console.log("No value passed!");
        else {
            console.log("Preparing to make a root for: "+myName);
            $http({
                url: "/_createRoot",
                method: "GET",
                params: {name:myName}
            }).then(function successCallback(response) {
                paintTree(response);
            },function errorCallback(response) {
                console.log("error:",response);
            });
        }
    }

    $scope.createSubcat = function(myObj) {
        console.log("Preparing to make a subcat for: "+myObj.name);
        $http({
            url: "/_createSubcat",
            method: "GET",
            params: myObj
        }).then(function successCallback(response) {
            //paintTree(response);
            console.log("I'm back!");
            resetCategories();
        },function errorCallback(response) {
            console.log("error:",response);
        });
    }

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

    //$scope.username = this.getUser();

    this.openCreateCat = function() {
        console.log("Opening createCat");
        $dialog.dialog({}).open('');
    }

    this.resetCats = function () {
        resetCategories();
    }

    function resetCategories() {
        console.log("Reset button pushed!");
        $scope.chosenCats.length=0;
        $scope.chosenSubcats.length=0;
        $scope.children.length=0;
        $scope.showCatDrop=true;
        $scope.showSubcats=false;
        $scope.trees.length=0;
        $scope.formCat.$setPristine();
        $scope.partStart=false;
        $scope.probStart=false;
        //$scope.trees.push({id:'? string: ?',name:''});
        //$scope.model='';
        getTrees();
        $scope.children.push({ id: '0', name: ''})
        $scope.subcat=$scope.children[0].id;
    }

    this.findPart = function() {
        console.log("Find Part was clicked!");
        $scope.probStart=false;
        newArr=[]
        for(var i in $scope.children) {
            if($scope.children[i].type!="problem" && $scope.children[i].type!="solution" ) {
                newArr.push($scope.children[i])
            }
        }
        $scope.children=newArr;
    }

    this.solveProblem = function() {
        console.log("Solve Problem was clicked!");
        $scope.partStart=false;
        newArr=[]
        for(var i in $scope.children) {
            if($scope.children[i].type=="problem" || $scope.children[i].type=="solution" ) {
                newArr.push($scope.children[i])
            }
        }
        $scope.children=newArr;
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

    $scope.showSolutionOld = function(ev,myObj) {
        // Appending dialog to document.body to cover sidenav in docs app
        // Modal dialogs should fully cover application
        // to prevent interaction outside of dialog
        console.log("Showing solution!");
        /*
        if(myObj.hasOwnProperty('url') && myObj.url!=null)
            boxStr=myObj.solution+" (for more information, see: <a href='"+myObj.url+"'>Click Here</a>)";
        else boxStr=myObj.solution;
        */
        boxStr=myObj.solution;
        $mdDialog.show(
          $mdDialog.alert()
            .parent(angular.element(document.querySelector('#popupContainer')))
            .clickOutsideToClose(true)
            .title('Solution Found')
            .textContent(boxStr)
            .ariaLabel('Alert Dialog Demo')
            .ok('Got it!')
            .targetEvent(ev)
        );
    };

    $scope.showSolution = function(ev,myObj) {
        $mdDialog.show({
          controller: DialogController,
          templateUrl: '/static/solution.tmpl.html',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose:true,
          fullscreen: $scope.customFullscreen, // Only for -xs, -sm breakpoints.
          locals: {
            solution: myObj.solution,
            url: myObj.url,
            part: null,
            parentId: null,
            allowedTypes: null
          }
        })
        .then(function(answer) {
          $scope.status = 'You said the information was "' + answer + '".';
        }, function() {
          $scope.status = 'You cancelled the dialog.';
        });
    };

    $scope.showSurrender = function(ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        // Modal dialogs should fully cover application
        // to prevent interaction outside of dialog
        $mdDialog.show(
          $mdDialog.alert()
            .parent(angular.element(document.querySelector('#popupContainer')))
            .clickOutsideToClose(true)
            .title('We Surrender!')
            .textContent('You have stumped us.')
            .ariaLabel('Alert Dialog Demo')
            .ok('Got it!')
            .targetEvent(ev)
        );
    };

    $scope.showPartBox = function(/*ev,*/myObj) {
        $mdDialog.show({
          controller: DialogController,
          templateUrl: '/static/part.tmpl.html',
          parent: angular.element(document.body),
          //targetEvent: ev,
          clickOutsideToClose:true,
          fullscreen: $scope.customFullscreen, // Only for -xs, -sm breakpoints.
          locals: {
            solution: null,
            url: null,
            part: myObj,
            parentId: null,
            allowedTypes: null
          }
        })
        .then(function(answer) {
          $scope.status = 'You said the information was "' + answer + '".';
        }, function() {
          $scope.status = 'You cancelled the dialog.';
        });
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

    $scope.showAddRoot = function(ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.prompt()
          .title('New Top-Level Category')
          .textContent('Enter a name for the category.')
          .placeholder('Category name')
          .ariaLabel('Category name')
          .targetEvent(ev)
          .ok('Okay!')
          .cancel('Cancel');

        $mdDialog.show(confirm).then(function(result) {
          // this happens when you click Okay
          $scope.createRoot(result);
          //$scope.status = 'You decided to name your dog ' + result + '.';
        }, function() {
          // this happens when you click Cancel
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
          templateUrl: '/static/dialog.tmpl.html',
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

    $scope.addSolution = function(ev) {
        console.log("Adding an alternative solution ...");
        $http({
            url: "/_getDistantProgeny",
            method: "GET",
            params: {id:$scope.chosenSubcats[0].id}
        }).then(function successCallback(response) {
            console.log("I found the most distant progeny!");
            console.log($scope.chosenSubcats[0].id+" is my GUID");
            console.log(response.data.id          +" is the progeny GUID");
            $scope.showAddSubcat(ev,response.data.id,[{'name':'Solution'}]);
        },function errorCallback(response) {
            console.log("error:",response);
        });
    }

    function showSubcatBox(ev,parentId,allowedTypes) {
        $mdDialog.show({
          locals: {
            allowedTypes: allowedTypes,
            solution: null,
            url: null,
            part: null,
            problem:null,
            parentId: parentId
          },
          controller: DialogController,
          templateUrl: '/static/addSubcat.tmpl.html',
          parent: angular.element(document.body),
          //targetEvent: ev,
          clickOutsideToClose:true,
          fullscreen: $scope.customFullscreen, // Only for -xs, -sm breakpoints.
        })
        .then(function(subcat) {
            if(subcat.hasOwnProperty('type') && (subcat.type=='Subcategory' || subcat.type=='Part') &&
                    subcat.hasOwnProperty('name') && subcat.name.length>0) {
                console.log ('You said the information was "' + subcat.name + '".');
                $scope.createSubcat(subcat);
            } else if(subcat.hasOwnProperty('type') && (subcat.type=='Problem' || subcat.type=='Solution') &&
                        subcat.hasOwnProperty('problem') && subcat.problem.length>0) {
                if ((subcat.type=='Solution' && subcat.hasOwnProperty('solution') && subcat.solution.length>0) ||
                        subcat.type=='Problem') {
                    console.log ('You said the information was "' + subcat.problem + '".');
                    $scope.createSubcat(subcat);
                }
                else console.log('Either the problem or solution was not entered');
            } else console.log('No subcat name was entered!');
        }, function() {
          console.log ('You cancelled the dialog.');
        });
    }

    $scope.showAddSubcat = function(ev,parentId,allowedTypes) {
        allowedTypes = allowedTypes || []
        if (allowedTypes.length==0) {
            $http({
                url: "/_getAllowedChildTypes",
                method: "GET",
                params: {parentId:parentId}
            }).then(function successCallback(response) {
                // Get the allowed types
                console.log("I have my list of allowed types!");
                allowedTypes=response.data;
                for(var i in allowedTypes) {
                    console.log(allowedTypes[i].name);
                }
                // Display the dialog box
                showSubcatBox(ev,parentId,allowedTypes);
            },function errorCallback(response) {
                console.log("error:",response);
            });
        }
        else showSubcatBox(ev,parentId,allowedTypes);

        /*
        $mdDialog.show({
          controller: DialogController,
          templateUrl: '/static/addSubcat.tmpl.html',
          parent: angular.element(document.body),
          //targetEvent: ev,
          clickOutsideToClose:true,
          fullscreen: $scope.customFullscreen, // Only for -xs, -sm breakpoints.
          locals: {
            solution: null,
            url: null,
            part: null,
            parentId: parentId
          }
        })
        .then(function(subcat) {
            if(subcat.hasOwnProperty('type') && (subcat.type=='Subcategory' || subcat.type=='Part') &&
                    subcat.hasOwnProperty('name') && subcat.name.length>0) {
                console.log ('You said the information was "' + subcat.name + '".');
                $scope.createSubcat(subcat);
            } else if(subcat.hasOwnProperty('type') && (subcat.type=='Problem') &&
                    subcat.hasOwnProperty('problem') && subcat.problem.length>0) {
                console.log ('You said the information was "' + subcat.problem + '".');
                $scope.createSubcat(subcat);
            } else {
                console.log('No subcat name was entered!');
            }
        }, function() {
          console.log ('You cancelled the dialog.');
        });
        */
    };

    function DialogController($scope, $mdDialog, solution, url, part, parentId,allowedTypes) {
        $scope.hide = function() {
          $mdDialog.hide();
        };
        $scope.cancel = function() {
          $mdDialog.cancel();
        };
        $scope.answer = function(answer) {
          $mdDialog.hide(answer);
        };
        $scope.solution = solution;
        $scope.url = url;
        $scope.part = part;
        $scope.parentId = parentId;
        $scope.allowedTypes = allowedTypes;
    }

});

helpApp.controller('AddSubcatController',function ($scope,$mdDialog) {
        //allowedTypes = allowedTypes || [];
        console.log('In the dialog controller!');
        console.log($scope);
        $scope.subcat = {
            name: '',
            type: '',
            parentId: $scope.parentId,
            url: '',
            problem: '',
            solution: '',
            allowedTypes: $scope.allowedTypes
        }
        /*
        $scope.catTypes =('Subcategory Part Problem').split(' ').map(function(catType) {
            return {name: catType};
        });
        */
        /*
        $scope.answer = function (answer) {
            console.log(answer);
        };
        */
});
