import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional

class UsersService:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_users(self, filters: Dict[str, Optional[str]], limit: int, offset: int) -> List[Dict]:
        cursor = self.db.cursor(dictionary=True)
        query = "SELECT * FROM users"
        params = []

        # applying filters
        if filters:
            filter_clauses = [f"{k} = %s" for k, v in filters.items() if v is not None]
            query += f" WHERE {' AND '.join(filter_clauses)}"
            params.extend(v for v in filters.values() if v is not None)

        # pagination
        if limit and offset is not None:
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

        try:
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()

    def create_user(self, user_data: Dict[str, str]) -> str:
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT MAX(id) FROM users")
                next_id = (cursor.fetchone()[0] or 0) + 1
                columns = ['username', 'first_name', 'last_name', 'email', 'credit', 'openid', 'role', 'Avatar', 'Self_Intro', 'Birthday']
                values = [next_id] + [user_data.get(col) for col in columns]
                cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
                self.db.commit()
        except Error as e:
            print(f"Error: {e}")
            return f"Failed to create user: {e}"
        return "User created successfully" if cursor.rowcount > 0 else "Failed to create user"

    def update_user(self, id: int, user_data: Dict[str, str]) -> str:
        columns = ['username', 'first_name', 'last_name', 'email', 'credit', 'openid', 'role', 'Avatar', 'Self_Intro', 'Birthday']
        values = [user_data[col] for col in columns] + [id]
        try:
            with self.db.cursor() as cursor:
                update_query = "UPDATE users SET " + ", ".join([f"{col}=%s" for col in columns]) + " WHERE id=%s"
                cursor.execute(update_query, values)
                self.db.commit()
        except Error as e:
            print(f"Error: {e}")
            return f"Failed to update user: {e}"
        return "User updated successfully" if cursor.rowcount > 0 else "User not found"

    def delete_user(self, id: int) -> str:
        try:
            with self.db.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s", (id,))
                self.db.commit()
        except Error as e:
            print(f"Error: {e}")
            return f"Failed to delete user: {e}"
        return "User deleted successfully" if cursor.rowcount > 0 else "User not found"
