from flask import Flask, render_template, request, redirect, url_for, flash, session, json, jsonify
from app import app
from github import Github

@app.route("/")

@app.route("/index", methods = ["POST", "GET"])
def index():

	# If username and password already saved in session
	if ("username" in session) and ("password" in session):
		return redirect(url_for("githubAccess"))

	# Otherwise no signed in, redirect to sign in page
	else:
		return render_template("index.html")


@app.route("/githubAccess", methods=["GET", "POST"])
def githubAccess():

	# If username and password already saved in session
	if ("username" in session) and ("password" in session):
		username = session["username"]
		password = session["password"]

		# log in using saved detuils
		github = Github(username, password)
		user = github.get_user()
		repos = user.get_repos()

		return render_template("githubAccess.html", 
								username = username,
								repos = repos)	

	# Otherwise get details from form
	elif request.method == "POST":

		# Get pword and uname from form
		username = request.form["username"]
		password = request.form["password"]

		try:
			# try use details to log into github
			github = Github(username, password)	
			user = github.get_user()
			repos = user.get_repos()
			users_repos = [] # The repos that the user owns

			for repo in repos:
				if repo.owner.login == username:
					# If user owns the repo, add to array
					users_repos.append(repo)

		except:
			flash("Invalid Login")
			return redirect(url_for("index"))

		# save uname pword in session
		session["password"] = password
		session["username"] = username

		return render_template("githubAccess.html", 
								username = username,
								repos = users_repos)	

	# Error, usually on form resubmission
	else:
		flash("Error with login.")
		return redirect(url_for("index"))


@app.route("/logout", methods=["GET", "POST"])
def logout():
	# delete uname and pword from session 
	session.pop("username", None)
	session.pop("password", None)
	flash("Logged out")
	return redirect(url_for("index"))


@app.route("/getStats", methods=["GET", "POST"])
def getStats():
	COMMIT_COUNT = 20
	temp_commit_count = 0 # Used to index the commits

	# if theres no saved pword and uname
	if ("password" not in session) or ("username" not in session):
		flash("Error: You're not logged in.")
		return redirect(url_for("index"))

	# Log into github using saved pword and uname
	password = session["password"]
	username = session["username"] 

	# Getting args from request
	requested_repo_name = request.args.get("repoName")
	requested_user_name = request.args.get("username")

	# Creating github object
	github = Github(username, password)	

	# If another username was requested
	if requested_user_name:
		# Different user requested
		try:
			user = github.get_user(requested_user_name)
		except:
			# return error message to ajax request
			return jsonify({ "message" : "Error: Not a valid user.", "stats": None})

	else:
		# Current user requested
		user = github.get_user()

	try:
		# if repo exists... get repo object
		repo = user.get_repo(requested_repo_name)

	except:
		# return error message to ajax request
		return jsonify({ "message" : "Error: Don't have permission.", "stats": None})

	commits = repo.get_commits().get_page(0) # get all commits in the repo
	commit_stats = [] # the reponse of additions / deletions for each commit in the repo

	for commit in commits[:COMMIT_COUNT]:
		# for each commit in the repo
		temp_commit_count += 1
		commit_stats.append(
			# add additions / deletions for each commit to response
			{"commit": temp_commit_count, "freq": {"additions": commit.stats.additions, "deletions": commit.stats.deletions}}
		)
		

	# return the reponse to the ajax request
	return jsonify({ "message" : requested_repo_name, "stats": commit_stats })
