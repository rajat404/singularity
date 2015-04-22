angular.module('singularApp',['ngRoute', 'satellizer', 'mainController', 'mainService'])
.config(['$routeProvider', '$locationProvider', function($routeProvider) {
  $routeProvider.
        when("/", {templateUrl: "views/feed.html", controller: "postController"}).
        when("/feed", {templateUrl: "views/feed.html", controller: "postController"}).
        when("/all", {templateUrl: "views/all.html", controller: "postController"}).
        otherwise({redirectTo: '/'});
}])
.config(function($authProvider) {
	$authProvider.twitter({
      url: '/api/twitterauth'
    });
});
