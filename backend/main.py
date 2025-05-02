from api.app import app
from crawler.fetch_and_save_pages import fetch_and_save_pages
from database.create_tables import create_tables
from make_spider_result_txt import make_spider_result_txt

create_tables()
fetch_and_save_pages("https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm")
# make_spider_result_txt()
#app.run(debug=True)
