import os
import sqlite3

# Global variables for easy access
connection = sqlite3.connect("documents.db", check_same_thread=False)
cursor = connection.cursor()
