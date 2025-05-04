import os
import sqlite3

# if os.path.exists("documents.db"):
#     os.remove("documents.db")

# Global variables for easy access
connection = sqlite3.connect("documents.db", check_same_thread=False)
cursor = connection.cursor()
