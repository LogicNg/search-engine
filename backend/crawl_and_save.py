import os

"""
This script is used to crawl a webpage and save the content to a database.
It first creates the necessary database tables, then fetches and saves the pages,
and finally calculates the PageRank scores for the pages.
Usage:
    python/python3 crawl_and_save.py
"""


if os.path.exists("documents.db"):
    os.remove("documents.db")

from crawler.fetch_and_save_pages import fetch_and_save_pages
from database.create_tables import create_tables
from database.page_rank import calculate_page_rank

create_tables()
fetch_and_save_pages("https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm")
calculate_page_rank()
