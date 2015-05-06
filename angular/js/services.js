angular.module('mainService', [])

	.factory('postService', ['$http',function($http) {
		return {
			get : function(username) {
				payload = '/api/getdata?authuser='+username;
				window.console.log("payload", payload);
				return $http.get(payload);
			}
		}
	}])

	.factory('signupService', ['$http',function($http) {
		return {
			get : function(username) {
				payload = '/api/createauthurl';
				window.console.log("payload", payload);
				return $http.get(payload);
			}
		}
	}]);
