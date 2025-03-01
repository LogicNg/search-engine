import sqlite3

# Global variables for easy access
connection = sqlite3.connect("documents.db")
cursor = connection.cursor()
