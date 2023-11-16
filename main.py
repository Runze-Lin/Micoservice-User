from fastapi import FastAPI, Response, Request
import uvicorn
import mysql.connector
from mysql.connector import Error

app = FastAPI()

# Database connection
def create_server_connection(host_name, user_name, user_password, db_name, port):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
            port=port
        )
        print("MySQL Database connected successfully.")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

connection = create_server_connection("user-db.c6mxanhdzdn0.us-east-2.rds.amazonaws.com", "admin", "12345678", "users", 3306)

# API gateways
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/users")
async def create_user(request: Request):
    data = await request.json()
    cursor = connection.cursor()
    try:
        sql = "INSERT INTO users (username, first_name, last_name, email, credit, openid, role, Avatar, Self_Intro, Birthday) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (data['username'], data['first_name'], data['last_name'], data['email'], data.get('credit', 100), data['openid'], data['role'], data.get('Avatar'), data.get('Self_Intro'), data.get('Birthday'))
        cursor.execute(sql, val)
        connection.commit()
        return {"message": "User created successfully"}
    except Error as err:
        raise HTTPException(status_code=400, detail=f"Error: {err}")
    finally:
        cursor.close()

@app.get("/users/{user_id}")
async def read_user(user_id: int):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Error as err:
        raise HTTPException(status_code=400, detail=f"Error: {err}")
    finally:
        cursor.close()

@app.put("/users/{user_id}")
async def update_user(user_id: int, request: Request):
    data = await request.json()
    cursor = connection.cursor()
    try:
        sql = "UPDATE users SET username=%s, first_name=%s, last_name=%s, email=%s, credit=%s, openid=%s, role=%s, Avatar=%s, Self_Intro=%s, Birthday=%s WHERE id=%s"
        val = (data['username'], data['first_name'], data['last_name'], data['email'], data.get('credit', 100), data['openid'], data['role'], data.get('Avatar'), data.get('Self_Intro'), data.get('Birthday'), user_id)
        cursor.execute(sql, val)
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User updated successfully"}
    except Error as err:
        raise HTTPException(status_code=400, detail=f"Error: {err}")
    finally:
        cursor.close()

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Error as err:
        raise HTTPException(status_code=400, detail=f"Error: {err}")
    finally:
        cursor.close()

@app.get("/users")
async def get_users():
    result = []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users")
        result = cursor.fetchall()
        cursor.close()
    except Error as err:
        print(f"Error: '{err}'")
        result = {"error": str(err)}
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8012)
