from fastapi import FastAPI, Request, HTTPException, Response, APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
import httpx
import json
import os

from google_module import GoogleSSO
from users import UsersService
from jwt_encoder import generate_jwt_token


app = FastAPI()
router = APIRouter() # use router to store login-related api endpoints for app.py to call
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # to allow HTTP temporarily, might remove later

# hard coded for now, will move to .env later
CLIENT_ID = "1064225628661-3s8lonjjjb2risas266sfs5udkntp7qg.apps.googleusercontent.com"
CLIENT_SECRET = "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"
OAUTH_URL = "https://ec2-3-144-182-9.us-east-2.compute.amazonaws.com"
SECRET_KEY = "Doritos"

sso = GoogleSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=OAUTH_URL + "/auth/callback",
    allow_insecure_http=True,
)

async def check_and_create_host(user):
    users_service = UsersService()

    # check if the user already exists as a host
    filters = {'email': user['email'], 'role': 'host'}
    existing_users = users_service.get_users(filters=filters, limit=1, offset=0)

    if existing_users:
        return "User already exists as a host."

    # create the user if they do not exist in db yet
    user_data = {
        'username': user['display_name'].replace(" ", ""),
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'email': user['email'],
        'credit': 100,  # default
        'openid': user['id'],
        'role': 'host'  # login as host
    }
    creation_result = users_service.create_user(user_data)
    return creation_result

async def check_and_create_guest(user):
    users_service = UsersService()

    # check if the user already exists as a guest
    filters = {'email': user['email'], 'role': 'guest'}
    existing_users = users_service.get_users(filters=filters, limit=1, offset=0)

    if existing_users:
        return "User already exists as a guest."

    # create the user if they do not exist in db yet
    user_data = {
        'username': user['display_name'].replace(" ", ""),
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'email': user['email'],
        'credit': 100,  # default credit for guests
        'openid': user['id'],
        'role': 'guest'  # login as guest
    }

    creation_result = users_service.create_user(user_data)
    return creation_result


@router.get("/login", response_class=HTMLResponse)
async def home_page():
    print("Current directory = " + os.getcwd())
    print("Files = " + str(os.listdir("./")))

    result = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Google Login</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 100px;
            }
            .container {
                width: 300px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            .logo {
                margin-bottom: 20px;
            }
            .button {
                display: inline-block;
                padding: 10px 20px;
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="container">
        <p>
        This is Login page for <a href="https://donald-f-ferguson.github.io/E6156-Cloud-Computing-F23/">
        Nestly.</a> 
        <form action="{OAUTH_URL}/auth/login">
            <div class="logo">
                <img src="static/rent.jpeg" 
                    height="100px" alt="Google Logo">
            </div>
            <h2>Sign in with your Google Account</h2>
            <button type="submit" class="button">Login with Google</button>
            </form>
        </div>
    </body>
    </html>
    """

    result = result.replace("{OAUTH_URL}", OAUTH_URL)
    return result

@router.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    with sso:
        return await sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})

@router.get("/auth/callback", response_class=HTMLResponse)
async def auth_callback(request: Request):
    """Verify login"""
    print("Request = ", request)
    print("URL = ", request.url)

    try:
        with sso:
            user = await sso.verify_and_process(request)
            user_json = json.dumps({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'display_name': user.display_name,
                'picture': user.picture  # Include any other fields you need
            })
            html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>User Info</title>
                </head>
                <body>
                    <h1>User Information</h1>
                    <img src="{user.picture}" alt="User Picture" width="96" height="96"><br>
                    <p><b>OpenID:</b> {user.id}</p>
                    <p>Email: {user.email}</p>
                    <p>First Name: {user.first_name}</p>
                    <p>Last Name: {user.last_name}</p>
                    <p>Display Name: {user.display_name}</p>
                    <button id="login-host">Login as Host</button>
                    <button id="login-guest">Login as Guest</button>
                    <button id="login-admin">Login as Admin</button>
                    <script>
                        const userData = {user_json};

                        function redirectTo(url) {{
                            window.location.href = url;
                        }}

                        function handleLogin(endpoint) {{
                            fetch(endpoint, {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/json'
                                }},
                                body: JSON.stringify({{ 'user': userData }})
                            }})
                            .then(response => response.json())
                            .then(data => {{
                                if (data.redirect) {{
                                    redirectTo(data.redirect);
                                }} else {{
                                    alert(data.message);
                                }}
                            }})
                            .catch(error => {{
                                console.error('Error during fetch:', error);
                                alert('Login failed. Please try again.');
                            }});
                        }}

                        document.getElementById('login-host').addEventListener('click', () => handleLogin('/login/host'));
                        document.getElementById('login-guest').addEventListener('click', () => handleLogin('/login/guest'));
                        document.getElementById('login-admin').addEventListener('click', () => handleLogin('/login/admin'));
                    </script>
                </body>
                </html>

                """
            return HTMLResponse(content=html_content)

    except Exception as e:
        print(e)
        return RedirectResponse("/static/error.html")

@router.post("/login/host")
async def login_host(user_data: dict):
    # check if the user (by email) already exist as a host; if not, add into users db
    user_info = user_data['user']
    try:
        result = await check_and_create_host(user_info)
        # get user id to use as sub for jwt token creation 
        users_service = UsersService()
        filters = {'email': user_info['email'], 'role': 'host'}
        users = users_service.get_users(filters=filters, limit=1, offset=0)
        user_id = users[0]['id']

        # generate jwt token
        token = generate_jwt_token(
            user_id=user_id,
            role="host",
            secret_key=SECRET_KEY
        )

        redirect_url = f"https://nestly6156.s3.us-east-2.amazonaws.com/users_static/process_jwt.html?token={token}"
        #redirect_url = f"http://localhost:8012/static/process_jwt.html?token={token}"
        return {"message": result, "redirect": redirect_url}
        # you may add redirect to personal homepage, etc. here
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login/guest")
async def login_guest(user_data: dict):
    user_info = user_data['user']
    
    # check if the user (by email) already exist as a guest, if not, add into users db
    try:
        result = await check_and_create_guest(user_info)
        # get user id to use as sub for jwt token creation 
        users_service = UsersService()
        filters = {'email': user_info['email'], 'role': 'guest'}
        users = users_service.get_users(filters=filters, limit=1, offset=0)
        user_id = users[0]['id']

        # generate jwt token
        token = generate_jwt_token(
            user_id=user_id,
            role="guest",
            secret_key=SECRET_KEY
        )

        redirect_url = f"https://nestly6156.s3.us-east-2.amazonaws.com/users_static/process_jwt.html?token={token}"
        #redirect_url = f"http://localhost:8012/static/process_jwt.html?token={token}"
        return {"message": result, "redirect": redirect_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/admin")
async def login_admin(user_data: dict):
    user_info = user_data['user']

    # instead of check and create if not existed yet,
        # check and directly reject if not existed as admin, since admin were supposed to be "manually" added by other admin    
    users_service = UsersService()
    filters = {'email': user_info['email'], 'role': 'admin'}
    users = users_service.get_users(filters=filters, limit=1, offset=0)
    if users == []:
        content = {"message": "This account is not registered as an Admin, please log in as host/guest."}
        return JSONResponse(content=content, status_code=404)
    user_id = users[0]['id'] 

    # (if not rejected)
    # generate jwt token
    token = generate_jwt_token(
        user_id=user_id,
        role="admin",
        secret_key=SECRET_KEY
    )
    redirect_url = f"https://nestly6156.s3.us-east-2.amazonaws.com/users_static/process_jwt.html?token={token}"
    #redirect_url = f"http://localhost:8012/static/process_jwt.html?token={token}"
    return {"message": "Welcome!", "redirect": redirect_url}


app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
