'use strict';

angular.module('roadshowdemoApp')
  .controller('MainCtrl', function ($scope, $http) {

    $scope.items = []
    $scope.searchForm = []

    $scope.filterItems = function() {
      var params = {
        column1: $scope.searchForm.column1,
        column2: $scope.searchForm.column2
      };
      $http({method: 'GET', url: 'https://04-frontend-dot-roadshow-demo.appspot.com/githubinfo', params: params}).
       success(function(data, status, headers, config) {
         console.log('success');
         console.log(data);
         $scope.loadItems(data.rows);
       })
       .error(function(data, status, headers, config) {
           console.log('fail');
       });
    }

    $scope.loadItems = function (items) {
      $scope.items = []
      for (var i = 0; i < items.length; i++) {
        $scope.items.push({
          language: items[i]['f'][1]['v'],
          count: items[i]['f'][0]['v']
        });
      };
      $scope.itemsCount = items.length;
      $scope.showStatistics();
    }

    $scope.filterItems();

    $scope.showStatistics = function() {
      var piechartValues = [];
      var piechartLabels = [];
      for (var i = 0; i < 10; i++) {
        piechartValues.push(parseInt($scope.items[i]['count']));
        piechartLabels.push('%%.%% - ' + $scope.items[i]['language']);
      }

      console.log('values and labels');
      console.log(piechartValues);
      console.log(piechartLabels);

      var r = Raphael("holder"),
      pie = r.piechart(320, 175, 100, piechartValues, { legend: piechartLabels, legendpos: "west", href: ["http://raphaeljs.com", "http://g.raphaeljs.com"]});

      r.text(320, 50, "Top 10 Languages").attr({ font: "20px sans-serif" });
      pie.hover(function () {
          this.sector.stop();
          this.sector.scale(1.1, 1.1, this.cx, this.cy);

          if (this.label) {
              this.label[0].stop();
              this.label[0].attr({ r: 7.5 });
              this.label[1].attr({ "font-weight": 800 });
          }
      }, function () {
          this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 500, "bounce");

          if (this.label) {
              this.label[0].animate({ r: 5 }, 500, "bounce");
              this.label[1].attr({ "font-weight": 400 });
          }
      });
    }

  });
