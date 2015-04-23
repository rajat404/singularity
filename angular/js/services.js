angular.module('mainService', [])

	.factory('postService', ['$http',function($http) {
		return {
			get : function(username) {
				payload = '/api/getdata?authuser='+username;
				window.console.log("payload", payload);
				return $http.get(payload);
			}
		}
	}]);
