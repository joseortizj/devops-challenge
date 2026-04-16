var app = angular.module("catsvsdogs", []);
var socket = io.connect({ transports: ["polling"] });

var bg1 = document.getElementById("background-stats-1");
var bg2 = document.getElementById("background-stats-2");

// Old Configuration
//const VOTE_API_HOST = window.location.hostname;
//const VOTE_API_PORT = "5001"; // Flask app port
//const VOTE_API_URL = `http://${VOTE_API_HOST}:${VOTE_API_PORT}`;

// NEW CONFIGURATION:
const VOTE_API_URL = "/api";

app.controller("statsCtrl", function ($scope, $http) {
  $scope.aPercent = 50;
  $scope.bPercent = 50;
  $scope.error = null;
  $scope.optionA = "Cats";
  $scope.optionB = "Dogs";
  $scope.userVote = null;
  $scope.voterId = null;
  $scope.isVoting = false;
  $scope.votingMessage = "";
  $scope.votingMessageClass = "";
  $scope.votingDisabled = false;

  // Initialize voter ID from localStorage or generate new one
  var initVoterId = function () {
    $scope.voterId = localStorage.getItem("voterId");
    if (!$scope.voterId) {
      $scope.voterId = generateVoterId();
      localStorage.setItem("voterId", $scope.voterId);
    }
    // Try to get user's previous vote
    $scope.userVote = localStorage.getItem("userVote");
  };

  var generateVoterId = function () {
    return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
  };

  // Voting functionality
  $scope.submitVote = function (vote) {
    if ($scope.isVoting) return;

    $scope.isVoting = true;
    $scope.votingMessage = "Submitting vote...";
    $scope.votingMessageClass = "voting-progress";

    var voteData = {
      vote: vote,
      voter_id: $scope.voterId,
    };

    $http
      .post(VOTE_API_URL + "/vote", voteData)
      .then(function (response) {
        $scope.userVote = vote;
        $scope.votingMessage = "Vote recorded successfully!";
        $scope.votingMessageClass = "voting-success";
        localStorage.setItem("userVote", vote);

        // Clear message after 3 seconds
        setTimeout(function () {
          $scope.$apply(function () {
            $scope.votingMessage = "";
          });
        }, 3000);
      })
      .catch(function (error) {
        console.error("Voting error:", error);
        $scope.votingMessage = "Failed to record vote. Please try again.";
        $scope.votingMessageClass = "voting-error";

        // Clear message after 5 seconds
        setTimeout(function () {
          $scope.$apply(function () {
            $scope.votingMessage = "";
          });
        }, 5000);
      })
      .finally(function () {
        $scope.isVoting = false;
      });
  };

  // Get voting options from API
  var getVotingOptions = function () {
    $http
      .get(VOTE_API_URL + "/")
      .then(function (response) {
        if (response.data && response.data.options) {
          $scope.optionA = response.data.options.a || "Cats";
          $scope.optionB = response.data.options.b || "Dogs";
        }
      })
      .catch(function (error) {
        console.warn("Could not fetch voting options:", error);
        // Keep default values
      });
  };

  var updateScores = function () {
    socket.on("scores", function (json) {
      data = JSON.parse(json);
      var a = parseInt(data.a || 0);
      var b = parseInt(data.b || 0);

      var percentages = getPercentages(a, b);

      // Update background stats positioning
      bg1.style.width = percentages.a + "%";
      bg2.style.left = percentages.a + "%";
      bg2.style.width = percentages.b + "%";

      $scope.$apply(function () {
        $scope.aPercent = percentages.a;
        $scope.bPercent = percentages.b;
        $scope.total = a + b;
      });
    });
  };

  var handleErrors = function () {
    socket.on("error", function (errorData) {
      $scope.$apply(function () {
        $scope.error = errorData;
      });
    });
  };

  var init = function () {
    document.body.style.opacity = 1;
    initVoterId();
    getVotingOptions();
    updateScores();
    handleErrors();
  };
  socket.on("message", function (data) {
    init();
  });
});

function getPercentages(a, b) {
  var result = {};

  if (a + b > 0) {
    result.a = Math.round((a / (a + b)) * 100);
    result.b = 100 - result.a;
  } else {
    result.a = result.b = 50;
  }

  return result;
}
