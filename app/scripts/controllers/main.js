'use strict';

angular.module('roadshowdemoApp')
  .controller('MainCtrl', function ($scope, $http) {

    $scope.items = []
    $scope.searchForm = []

    function generateItems() {
      $scope.items = []
      for (var i = 0; i < Math.floor((Math.random() * 100) + 1); i++) {
        $scope.items.push({
          column1: 'column1Value',
          column2: 'column2Value',
          column3: 'column3Value',
          column4: 'column4Value',
          column5: 'column5Value'
        });
      };
      $scope.itemsCount = $scope.items.length;
    }

    generateItems();

    $scope.filterItems = function() {
      var params = {
        column1: $scope.searchForm.column1,
        column2: $scope.searchForm.column2
      };
      // generateItems();
     $http({method: 'GET', url: 'https://roadshow-demo.appspot.com/', params: params}).
      success(function(data, status, headers, config) {
        console.log('success');
        generateItems();
      })
      .error(function(data, status, headers, config) {
          console.log('fail');
      });
    }

  });
