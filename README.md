- Manages all user-related data and operations such as registration, authentication, and profile management.
- Routes:
	* Frontend: back to @app.get("/")
		- Cloud: http://ec2-3-144-182-9.us-east-2.compute.amazonaws.com:8012/
		- Local: http://localhost:8012/
	* Login: @router.get("/login")
		- Cloud: http://ec2-3-144-182-9.us-east-2.compute.amazonaws.com/login
		- Local: http://localhost:8012/login

- To test the whole login process locally:
	1. Navigate to google_sso.py
	2. Find Line 'OAUTH_URL = "https://ec2-3-144-182-9.us-east-2.compute.amazonaws.com"' (line 18)
	3. change the OAUTH_URL to "http://localhost:8012"
	4. If not exchanged, the login page will be prompted, but the callback will not work when EC2 is not up
	5. Please remember to change it back to OAUTH_URL = "https://ec2-3-144-182-9.us-east-2.compute.amazonaws.com" before pushing to Github

- Note (TODO):
	the Login as host/guest now connects to the db, but does not redirect to the logged in pages. Please feel free to add that part (directly in /login/host and /login/guest so the "Already Exist" users can be redirected too)
