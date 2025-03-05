from db import cursor, connection

'''
Table in total:
1. page_relationships
2. url_mapping
3. word_mapping
4. forward_index
5. inverted_index
6. keyword_statistics
7. page_rank
'''

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
        CREATE TABLE IF NOT EXISTS word_mapping (
            word_id INT PRIMARY KEY,
            word TEXT UNIQUE NOT NULL
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS forward_index (
            page_id INT PRIMARY KEY,
            title TEXT NOT NULL,
            last_modified_date TIMESTAMP NOT NULL,
            size INT NOT NULL,
            child_links JSON NOT NULL,
            FOREIGN KEY (page_id) REFERENCES url_mapping (page_id)
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS inverted_index (
            word_id INT NOT NULL,
            page_id INT NOT NULL,
            term_frequency INT NOT NULL,
            PRIMARY KEY (word_id, page_id)
            FOREIGN KEY (word_id) REFERENCES word_mapping (word_id),
            FOREIGN KEY (page_id) REFERENCES url_mapping (page_id)
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS keyword_statistics (
            word_id INT NOT NULL,
            page_id INT NOT NULL,
            tf_idf FLOAT NOT NULL,
            PRIMARY KEY (word_id, page_id),
            FOREIGN KEY (word_id) REFERENCES word_mapping (word_id)
            FOREIGN KEY (page_id) REFERENCES url_mapping (page_id)
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS page_rank (
            page_id INT PRIMARY KEY,
            page_rank FLOAT NOT NULL,
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

def drop_table(table_name):
    """
    Drop a table from the database.

    Args:
        table_name (str): The name of the table to drop.

    Returns:
        None: This function does not return any value.
    """
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        connection.commit()
    except Exception as e:
        print("Failed to drop table:", e)

def drop_all_table():
    """
    Drop all tables from the database.

    Returns:
        None: This function does not return any value.
    """
    try:
        for sql in sql_statements:
            table_name = sql.split()[2]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        connection.commit()
    except Exception as e:
        print("Failed to drop tables:", e)

if __name__ == "__main__":
    create_tables()
    #print("Tables created successfully.")
    #drop_all_table()