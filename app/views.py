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

			# save uname pword in session
			session["password"] = password
			session["username"] = username

			return render_template("githubAccess.html", 
									username = username,
									repos = repos)			

		except:
			# delete wrong uname and pword from session + give error message
			session.pop("username", None)
			session.pop("password", None)
			flash("Invalid Login")
			return redirect(url_for("index"))

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
	temp_commit_count = COMMIT_COUNT

	# if theres no saved pword and uname
	if ("password" not in session) or ("username" not in session):
		flash("Error: You're not logged in.")
		return redirect(url_for("index"))

	# Log into github using saved pword and uname
	password = session["password"]
	username = session["username"] 
	github = Github(username, password)	
	user = github.get_user()

	try:
		# if repo exists... get repo object
		repo_name = request.args.get("repoName")
		repo = user.get_repo(repo_name)

	except:
		# return error message to ajax request
		return jsonify({ "message" : "Error: Don't have permission.", "stats": None})

	commits = repo.get_commits().get_page(0) # get all commits in the repo
	commit_stats = [] # the reponse of additions / deletions for each commit in the repo

	for commit in commits[:COMMIT_COUNT]:
		# for each commit in the repo
		commit_stats.append(
			# add additions / deletions for each commit to response
			{"commit": temp_commit_count, "freq": {"additions": commit.stats.additions, "deletions": commit.stats.deletions}}
		)
		temp_commit_count -= 1

	# return the reponse to the ajax request
	return jsonify({ "message" : repo_name, "stats": commit_stats })
