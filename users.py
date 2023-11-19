import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional

# database services
class UsersService:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_users(self, filters: Dict[str, Optional[str]], limit: int, offset: int) -> List[Dict]:
        cursor = self.db.cursor(dictionary=True)
        query = "SELECT * FROM users"
        params = []

        # applying filters
        if filters:
            filterlist= []
            for k, v in filters.items():
                if v:
                    if k == "credit_gt":
                        filterlist.append("credit > %s")
                    elif k == "credit_lt":
                        filterlist.append("credit < %s")
                    else:
                        filterlist.append(f"{k} = %s")
                    params.append(v)

            if filterlist:
                query += " WHERE " + " AND ".join(filterlist)
            
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
        cursor = self.db.cursor()

        # get curr max id
        cursor.execute("SELECT MAX(CAST(id AS UNSIGNED)) FROM users")
        max_id = cursor.fetchone()[0]
        if max_id is None:
            next_id_int = 1
        else:
            next_id_int = int(max_id) + 1

        # padding into 8 digits
        next_id = f"{next_id_int:08d}"

        columns = ['username', 'first_name', 'last_name', 'email', 'credit', 'openid', 'role']
        values = [next_id] + [user_data.get(col) for col in columns]

        cursor.execute("INSERT INTO users (id, username, first_name, last_name, email, credit, openid, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", values)
        self.db.commit()
        cursor.close()
        return "User created successfully"


    def update_user(self, user_id: int, user_data: Dict[str, str]) -> str:
        cursor = self.db.cursor()
        update_statements = []
        values = []

        for column, value in user_data.items():
            if value is not None:
                update_statements.append(f"{column}=%s")
                values.append(value)

        update_query = "UPDATE users SET " + ", ".join(update_statements) + " WHERE id=%s"
        values.append(user_id)

        try:
            cursor.execute(update_query, values)
            self.db.commit()
            return "User updated successfully" if cursor.rowcount else "User not found"
        except Error as e:
            print(f"Error: {e}")
            return "Failed to update user"
        finally:
            cursor.close()

    def delete_user(self, user_id: int) -> str:
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        self.db.commit()
        cursor.close()
        return "User deleted successfully" if cursor.rowcount > 0 else "User not found"

