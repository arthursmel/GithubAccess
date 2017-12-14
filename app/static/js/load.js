$(document).ready(function() {

	$("#repoName").change(function() {

		// Setting up loading html
		$("#dashboard").html("Loading...");
		$("#progress").css("visibility", "visible");

		$.getJSON({
			url: "/getStats",
			data: { 
				repoName: $("#repoName").val(),
			},
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

	});

});