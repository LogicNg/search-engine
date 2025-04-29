from database.db import connection, cursor


def create_tables():
    """
    Create tables in the database by reading SQL statements from creates.sql.

    This function reads the SQL statements from the tables.sql file and
    executes them to create the necessary tables in the database.
    """
    try:
        with open("tables.sql", "r") as file:
            sql_statements = file.read()

        cursor.executescript(sql_statements)
        connection.commit()

    except Exception as e:
        print("Failed to create tables:", e)


if __name__ == "__main__":
    create_tables()
