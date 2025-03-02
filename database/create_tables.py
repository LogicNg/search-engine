# CREATE TABLE page_relationships (
#     parent_page_id INT NOT NULL,
#     child_page_id INT NOT NULL,
#     PRIMARY KEY (parent_page_id, child_page_id)
# );

# CREATE TABLE url_mapping (
#     page_id INT PRIMARY KEY,
#     url TEXT UNIQUE NOT NULL
# );

# CREATE TABLE forward_index (
#     page_id INT PRIMARY KEY,
#     title TEXT NOT NULL,
#     last_modified_date TIMESTAMP NOT NULL,
#     size INT NOT NULL,
#     FOREIGN KEY (page_id) REFERENCES url_mapping (page_id)
# );

from db import cursor, connection

sql_statements = [
    """
        CREATE TABLE IF NOT EXISTS page_relationships (
            parent_page_id INT NOT NULL,
            child_page_id INT NOT NULL,
            PRIMARY KEY (parent_page_id, child_page_id)
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS url_mapping (
            page_id INT PRIMARY KEY,
            url TEXT UNIQUE NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS forward_index (
            page_id INT PRIMARY KEY,
            title TEXT NOT NULL,
            last_modified_date TIMESTAMP NOT NULL,
            size INT NOT NULL,
            FOREIGN KEY (page_id) REFERENCES url_mapping (page_id)
        );
    """
]

def create_tables():
    """
    Create tables in the database.

    This function is intended to initialize the database schema by creating
    the necessary tables. It should be implemented to define the structure
    of the database, including any relationships between tables.
    """
    try:
        for sql in sql_statements:
            cursor.execute(sql)
        
        connection.commit() 

    except Exception as e:
        print("Failed to create tables:", e)

    #raise NotImplementedError("This function is not implemented yet.")


if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")