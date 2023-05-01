import sqlite3
from sqlite3 import Error


class database:
    conn = None

    def __init__(self):
        self.create_connection("lanplay.db")
        self.create_table(sql_create_projects_table)

    def create_connection(self, db_file):
        """
        Creates a database connection to a SQLite database
        """
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

    def create_table(self, create_table_sql):
        """
        Creates a table from the create_table_sql statement
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def insert_server(self, server):
        """
        Inserts a new server inside the table
        :param server: the server
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(sql_insert_server, (server,))
            self.conn.commit()
        except Error as e:
            print(e)

    def delete_server(self, server):
        """
        Delete a server
        :param server: the server
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(sql_delete_server, (server,))
            self.conn.commit()
        except Error as e:
            print(e)

    def select_server(self, server):
        cur = self.conn.cursor()
        if server:
            cur.execute(sql_select_server_by_name, (server,))
        else:
            cur.execute(sql_select_server)

        rows = cur.fetchall()
        return rows

    def close_connection(self):
        if self.conn:
            self.conn.close()
            
            
sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS servers (
                                        id integer PRIMARY KEY AUTOINCREMENT ,
                                        url text NOT NULL
                                    ); """
sql_insert_server = """ INSERT INTO servers (url) VALUES (?); """
sql_delete_server = """ DELETE FROM servers WHERE url = (?)"""
sql_select_server = """ SELECT * FROM servers; """
sql_select_server_by_name = """ SELECT * FROM servers WHERE url = (?)"""