import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional

# database services
class UsersService:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_users(self, filters, limit, offset):
        cursor = self.db.cursor(dictionary=True)
        query = "SELECT * FROM users"
        params = []

        # applying filters
        if filters is not None:
            filterlist = []
            for k, v in filters.items():
                if v:
                    # credit greater than or less than filters
                    if k == "credit_gt":
                        condition = "credit > %s"
                        filterlist.append(condition)
                    elif k == "credit_lt":
                        condition = "credit < %s"
                        filterlist.append(condition)
                    # all other filters
                    else:
                        condition = k + " = %s"
                        filterlist.append(condition)
                    params.append(v)

            # Join all filters and construct the query
            if filterlist:
                query += " WHERE " + " AND ".join(filterlist)
            
        # pagination
        if limit and offset is not None:
            query += " LIMIT %s OFFSET %s"
            params.append(limit)
            params.append(offset)

        # execute select query
        cursor.execute(query, tuple(params))
        users = cursor.fetchall()
        cursor.close()
        return users


    def create_user(self, user_data):
        cursor = self.db.cursor()

        # get current max id
        cursor.execute("SELECT MAX(CAST(id AS UNSIGNED)) FROM users")
        max_id = cursor.fetchone()[0]
        next_id_int = 1 if max_id is None else int(max_id) + 1

        # padding into 8 digits
        next_id = str(next_id_int).zfill(8)

        columns = ['username', 'first_name', 'last_name', 'email', 'credit', 'openid', 'role']
        values = [next_id] + [user_data.get(col) for col in columns]

        # execute insert query
        query = "INSERT INTO users (id, username, first_name, last_name, email, credit, openid, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, values)
        self.db.commit()
        cnt = cursor.rowcount
        cursor.close()
        return "User created successfully" if cnt > 0 else "Failed to create user"

    def update_user(self, user_id, user_data):
        cursor = self.db.cursor()
        statements = []
        vals = []

        # get all update fields
        for col in user_data:
            v = user_data[col]
            if v:
                statement = col + "=%s"
                statements.append(statement)
                vals.append(v)

        query = "UPDATE users SET " + ", ".join(statements) + " WHERE id=%s"
        vals.append(user_id)

        # execute update query
        cursor.execute(query, vals)
        self.db.commit()
        cnt = cursor.rowcount
        cursor.close()

        return "User updated successfully" if cnt > 0 else "User not found"

    def delete_user(self, user_id):
        cursor = self.db.cursor()
        query = "DELETE FROM users WHERE id = %s"

        # execute delete query
        cursor.execute(query, (user_id,))
        self.db.commit()
        cnt = cursor.rowcount
        cursor.close()
        return "User deleted successfully" if cnt > 0 else "User not found"
