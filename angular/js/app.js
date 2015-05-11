angular.module('singularApp',['ngRoute', 'mainController', 'mainService'])
.config(['$routeProvider', '$locationProvider', function($routeProvider) {
  $routeProvider.
        when("/", {templateUrl: "views/signin.html", controller: "signinController"}).
        when("/:username/feed", {templateUrl: "views/feed.html", controller: "postController"}).
        when("/signup", {templateUrl: "views/signup.html", controller: "signupController"}).
        when("/signin", {templateUrl: "views/signin.html", controller: "signinController"}).
        otherwise({redirectTo: '/'});
}]);

