# References: 
    # https://examples.javacodegeeks.com/crud-operations-in-python-on-mysql/    
    # https://sesamedisk.com/how-to-write-mysql-crud-queries-in-python/
from google_sso import router as google_sso_router
from fastapi import FastAPI, Request, HTTPException
import mysql.connector
from typing import Optional
from users import UsersService
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()
app.include_router(google_sso_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

users_svc = UsersService()

# api endpoints
@app.get("/")  ## use this as the static page of this app
async def root():
    return RedirectResponse(url="https://nestly6156.s3.us-east-2.amazonaws.com/users_static/index.html")
    
@app.get("/users", )      ##use this to get the users
async def get_users(request: Request,id: Optional[str] = None, username: Optional[str] = None, first_name: Optional[str] = None,
                    last_name: Optional[str] = None, email: Optional[str] = None,
                    credit: Optional[int] = None, credit_lt: Optional[int] = None,
                    credit_gt: Optional[int] = None, role: Optional[str] = None,
                    limit: Optional[int] = None, offset: Optional[int] = None):
    filters = {
        "id":id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "credit": credit,
        "credit_lt": credit_lt,
        "credit_gt": credit_gt,
        "role": role
    }
    query = {k: v for k, v in filters.items() if v}    ##simple search
    auth_header = request.headers.get('Authorization')
    print("Authorization header (expected to be jwt token):", auth_header)
    return users_svc.get_users(query, limit, offset)

@app.get("/users/{user_id}")  ## get user by user_id
async def get_user(user_id: int):
    user = users_svc.get_users({"id": user_id}, limit=1, offset=None)
    return user[0]

@app.post("/users")         ##create users function
async def create_user(request: Request):
    user_data = await request.json()
    auth_header = request.headers.get('Authorization')
    print("Authorization header (expected to be jwt token):", auth_header)
    return users_svc.create_user(user_data)

@app.put("/users/{user_id}")        ##update users function
async def update_user(user_id: int, request: Request):
    user_data = await request.json()
    auth_header = request.headers.get('Authorization')
    print("Authorization header (expected to be jwt token):", auth_header)
    return users_svc.update_user(user_id, user_data)

@app.delete("/users/{user_id}")  ##delete users function
async def delete_user(user_id: int, request: Request):
    auth_header = request.headers.get('Authorization')
    print("Authorization header (expected to be jwt token):", auth_header)
    return users_svc.delete_user(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
