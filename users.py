# References: 
# https://examples.javacodegeeks.com/crud-operations-in-python-on-mysql/
# https://sesamedisk.com/how-to-write-mysql-crud-queries-in-python/

import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional
from db_service import Database

# database services
class UsersService:
    def __init__(self):
        self.db = Database()
        self.db.connect()

    def get_users(self, filters, limit, offset):
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
        return self.db.execute_query(query, tuple(params))

    def create_user(self, user_data):
        # get current max id
        max_id_result = self.db.execute_query("SELECT MAX(CAST(id AS UNSIGNED)) FROM users")
        max_id = max_id_result[0]['MAX(CAST(id AS UNSIGNED))'] if max_id_result else 0
        next_id_int = 1 if max_id is None else int(max_id) + 1

        # padding into 8 digits
        next_id = str(next_id_int).zfill(8)

        columns = ['username', 'first_name', 'last_name', 'email', 'credit', 'openid', 'role']
        values = [next_id] + [user_data.get(col) for col in columns]

        # execute insert query
        query = "INSERT INTO users (id, username, first_name, last_name, email, credit, openid, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        insert_count = self.db.execute_query(query, values)
        return "User created successfully" if insert_count > 0 else "Failed to create user"

    def update_user(self, user_id, user_data):
        statements = []
        vals = []

        # get all update fields
        for col in user_data:
            v = user_data[col]
            if v:
                statements.append(col + "=%s")
                vals.append(v)

        query = "UPDATE users SET " + ", ".join(statements) + " WHERE id=%s"
        vals.append(user_id)

        # execute update query
        update_count = self.db.execute_query(query, vals)
        return "User updated successfully" if update_count > 0 else "User not found"

    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE id = %s"
        delete_count = self.db.execute_query(query, (user_id,))
        return "User deleted successfully" if delete_count > 0 else "User not found"
