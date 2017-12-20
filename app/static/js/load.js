$(document).ready(function() {

	// Setup before functions
	var typingTimer;                //timer identifier
	var doneTypingInterval = 1000;  //time in ms 

	// Used to time how long since a user has
	// typed in a input text box
	function createSubmitTimer(elementName) {
		$(elementName).keyup(function(){
			clearTimeout(typingTimer);
			if ($(elementName).val()) {
				// onUserFinishedTyping called after doneTypingInterval time in ms
				typingTimer = setTimeout(onUserFinishedTyping, doneTypingInterval);
			}
		});
	}

	// Create timer for both username + repo name input boxes
	createSubmitTimer("#publicUsername"); 
	createSubmitTimer("#publicRepoName");

	// When the user has finished typing in either
	// the username or the repo text boxes
	function onUserFinishedTyping () {
		// Request data for reponame + username
		var data =	{ 
			repoName: $("#publicRepoName").val(),
			username: $("#publicUsername").val()
		};
		requestData(data);
	}

	$("#repoName").change(function() {
		var data =	{ 
			repoName: $("#repoName").val(),
			username: null // null defaults to the current logged in user
		};
		requestData(data);
	});

	function requestData(userData) {

		// Setting up loading html
		$("#dashboard").html("Loading...");
		$("#progress").css("visibility", "visible");

		$.getJSON({
			url: "/getStats",
			data: userData,
			success: function(data){
				
				if (data.stats === null) { 
					// If there was no stats for the repo...
					$("#dashboard").html(data.message);
					$("#progress").css("visibility", "hidden");
					return; // finish
				}

				// Hide progress bar and update graph
				$("#progress").css("visibility", "hidden");
				$("#dashboard").html(" <area> ");
				dashboard('#dashboard', data.stats);
			}
		});
	}

});