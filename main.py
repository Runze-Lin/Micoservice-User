from fastapi import FastAPI, Response
import uvicorn
from resources.students import StudentsResource
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
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

# Replace with your RDS credentials
connection = create_server_connection("user-db.c6mxanhdzdn0.us-east-2.rds.amazonaws.com", "admin", "12345678", "users", 3306)

students_resource = StudentsResource()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Awesome cloud developer 'Rebirth: I am Bezos' says hello {name}"}

@app.get("/hello_text/{name}")
async def say_hello_text(name: str):
    the_message = f"Awesome cloud developer 'Rebirth: I am Bezos' says Hello {name}"
    rsp = Response(content=the_message, media_type="text/plain")
    return rsp

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
