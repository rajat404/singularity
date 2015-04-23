angular.module('mainController', [])
	
	.controller('postController', ['$scope','$http','postService', '$auth', function($scope, $http,  postService, $auth) {
		$scope.formData = {};
		// $scope.tweetFilter = null;



		$scope.fetchNearDup = function(){
			$scope.tweetData = $scope.finNearDupList;
			$scope.count = $scope.nearCount;
		};

		$scope.fetchExactDup = function(){
			$scope.tweetData = $scope.finExactDupList;
			$scope.count = $scope.exactCount;

		};

		$scope.fetchAllTweets = function(){
			$scope.tweetgroup = $scope.allTweets;
			$scope.count = $scope.tweetCount;

		};

		$scope.authenticate = function(provider){
	      $auth.authenticate(provider);
	    };

	    $scope.signin = function(username){
	    	var username = $scope.username;
	    	postService.get(username).success(function(data) {
				$scope.response = data['data'];
				$scope.exactCount = data['data']['exactCount'];
	            $scope.nearCount = data['data']['nearCount'];
	            $scope.tweetCount = data['data']['tweetCount'];
	            $scope.allTweets = data['data']['allTweets'];
	            $scope.finExactDupList = data['data']['finExactDupList'];
	            $scope.finNearDupList = data['data']['finNearDupList'];		
	            console.log($scope.response);
	            console.log("API called");
			});
	    }

	}]);
