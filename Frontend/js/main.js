angular.module('app', []).controller('smile', ['$scope', function($scope) {
  $http.get('http://exodia.ngrok.com/getsmile').
  success(function(data, status, headers, config) {
    $scope.room = data;
  }).
  error(function(data, status, headers, config) {
    // called asynchronously if an error occurs
    // or server returns response with an error status.
  });
}]);