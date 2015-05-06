angular.module('singularApp',['ngRoute', 'mainController', 'mainService'])
.config(['$routeProvider', '$locationProvider', function($routeProvider) {
  $routeProvider.
        when("/", {templateUrl: "views/feed.html", controller: "postController"}).
        when("/feed", {templateUrl: "views/feed.html", controller: "postController"}).
        when("/all", {templateUrl: "views/all.html", controller: "postController"}).
        otherwise({redirectTo: '/'});
}]);

