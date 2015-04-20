angular.module('mainService', [])

	.factory('postService', ['$http',function($http) {
		return {
			get : function() {
				return $http.get('/api/getdata');
			}
		}
	}]);
