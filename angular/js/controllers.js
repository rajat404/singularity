angular.module('mainController', [])
    
    .controller('postController', ['$scope','$http', '$routeParams', 'postService', function($scope, $http, $routeParams, postService) {
        // $scope.formData = {};
        $scope.username = $routeParams.username;

        $scope.$on('$viewContentLoaded', function(){
            $scope.signin();
        });

        $scope.fetchNearDup = function(){
            $scope.tweetData = $scope.finNearDupList;
            $scope.count = $scope.nearCount;
            if ($scope.count == 0){
                alert("Congratulations!\nNo duplicate tweets in your feed.");
            }
        };

        $scope.fetchExactDup = function(){
            $scope.tweetData = $scope.finExactDupList;
            $scope.count = $scope.exactCount;
            if ($scope.count == 0){
                alert("Congratulations!\nNo duplicate tweets in your feed.");
            }
        };

        $scope.fetchAllTweets = function(){
            $scope.tweetgroup = $scope.allTweets;
            $scope.count = $scope.tweetCount;
            if ($scope.count == 0){
                alert("Insufficient Tweets.\nPlease try later.");
            }
        };

        // $scope.searchFilter = function (tweet) {
  //           var keyword = new RegExp($scope.nameFilter, 'i');
  //           return !$scope.nameFilter || keyword.test(tweet.text);
  //       };

        $scope.signin = function(){
            // var username = $scope.username;
            postService.get($scope.username).success(function(data) {
                $scope.response = data['data'];
                if ($scope.response != null){
                    $scope.exactCount = data['data']['exactCount'];
                    $scope.nearCount = data['data']['nearCount'];
                    $scope.tweetCount = data['data']['tweetCount'];
                    $scope.allTweets = data['data']['allTweets'];
                    $scope.finExactDupList = data['data']['finExactDupList'];
                    $scope.finNearDupList = data['data']['finNearDupList'];        
                    console.log("Singularity --by Rajat Goyal");
                    console.log($scope.response);
                    alert("Successfully logged in.\nUse the blue buttons to get your tweets.");
                }
                else{
                    alert("Username not recognized.\nPlease signup first.");
                }
            });
            // window.location.href = "#/feed";
        }
        
    }])

    .controller('signupController', ['$scope','$http', 'signupService', function($scope, $http, signupService) {

        $scope.signup = function(){
            // var username = $scope.username;
            signupService.get().success(function(data) {
                $scope.url = data['data'];
                // console.log($scope.url);
                // console.log("API called");
            });
            // window.location.href = "#/feed";
        }

    }]);
