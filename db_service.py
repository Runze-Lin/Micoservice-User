import mysql.connector

class Database:
    def __init__(self):
        self.config = {
            'user': 'admin',
            'password': 'dbuserdbuser',
            'host': 'database-1.cjcvwqrysug2.us-east-2.rds.amazonaws.com',
            'database': 'users',
            'port': 3306
        }
        self.conn = None
        self.connect()

    def connect(self):
        if not self.conn:
            try:
                self.conn = mysql.connector.connect(**self.config)
                print("successfully connected to the db")
            except mysql.connector.Error as err:
                print(f"failed to connect to the db due to: {err}")
    '''

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print("disconnected from the db")
    '''

    def execute_query(self, query, params=None):
        if not self.conn:
            print("db is not connected")
            return None
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"): ## SELECTs
                result = cursor.fetchall()
            else: ## other commands
                self.conn.commit()
                result = cursor.rowcount
            return result
        except mysql.connector.Error as err:
            print(f"failed to execute query due to: {err}")
            return None
