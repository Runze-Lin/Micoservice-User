from fastapi import FastAPI, Request, HTTPException, Response, APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse
import httpx
import json
import os

from ..users import UsersService

from .google_module import GoogleSSO

app = FastAPI()
router = APIRouter() # use router to store login-related api endpoints for app.py to call
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # to allow HTTP temporarily, might remove later

# hard coded for now, will move to .env later
CLIENT_ID = "1064225628661-3s8lonjjjb2risas266sfs5udkntp7qg.apps.googleusercontent.com"
CLIENT_SECRET = "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"
OAUTH_URL = "https://ec2-3-144-182-9.us-east-2.compute.amazonaws.com"

sso = GoogleSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=OAUTH_URL + "/auth/callback",
    allow_insecure_http=True,
)

@router.get("/", response_class=HTMLResponse)
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
        <form action="{OAUTH_URL}/auth/login" method="get">
                <input type="hidden" name="role" value="host">
                <button type="submit" class="button">Login as Host</button>
            </form>
            <form action="{OAUTH_URL}/auth/login" method="get">
                <input type="hidden" name="role" value="guest">
                <button type="submit" class="button">Login as Guest</button>
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

            role = request.query_params.get("role", "guest")

            user_info = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "display_name": user.display_name,
                "role": role
            }

            users_svc = UsersService()
            users_svc.create_user(user_info)


            html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>User Info</title>
                </head>
                <body>
                    <h1>User Information</h1>
                    <img src="{user.picture}" alt="User Picture" width="96" height="96"><br>
                    <p><b>ID:</b> {user.id}</p>
                    <p>Email: {user.email}</p>
                    <p>First Name: {user.first_name}</p>
                    <p>Last Name: {user.last_name}</p>
                    <p>Display Name: {user.display_name}</p>
                    <p>Role: {user.role}</p>
                </body>
                </html>
                """
            return HTMLResponse(content=html_content)
    except Exception as e:
        print(e)
        return RedirectResponse("/static/error.html")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
