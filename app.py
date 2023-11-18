from fastapi import FastAPI, Request, HTTPException
import mysql.connector
from typing import Optional
from users import UsersService

app = FastAPI()

# setting up db connection
def setup_db_connection(host, user, pwd, db, port):
    try:
        conn = mysql.connector.connect(host=host, user=user, passwd=pwd, database=db, port=port)
        print("MySQL Database connected successfully.")
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
        raise HTTPException(status_code=500, detail="Database connection failed")
    return conn

# initialize db connection and UsersService
conn = setup_db_connection("users.c6mxanhdzdn0.us-east-2.rds.amazonaws.com", "admin", "12345678", "users", 3306)
users_svc = UsersService(conn)

# api endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to our User Management API"}
    
@app.get("/users")
async def get_users(username: Optional[str] = None, first_name: Optional[str] = None,
                    last_name: Optional[str] = None, email: Optional[str] = None,
                    credit: Optional[int] = None, credit_lt: Optional[int] = None,
                    credit_gt: Optional[int] = None, role: Optional[str] = None,
                    limit: Optional[int] = None, offset: Optional[int] = None):
    filters = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "credit": credit,
        "credit <": credit_lt,
        "credit >": credit_gt,
        "role": role
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    return users_svc.get_users(filters, limit, offset)

@app.post("/users")
async def create_user(request: Request):
    user_data = await request.json()
    return users_svc.create_user(user_data)

@app.put("/users/{user_id}")
async def update_user(user_id: int, request: Request):
    user_data = await request.json()
    return users_svc.update_user(user_id, user_data)

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    return users_svc.delete_user(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
