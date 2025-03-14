from crawler.webpage import fetch_and_save_pages
from database.create_tables import create_tables

create_tables()
fetch_and_save_pages("https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm")
