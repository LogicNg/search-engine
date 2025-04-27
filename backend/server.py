from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

#sample data
'''
title: Dinosaur Planet (2003)
url: https://www.cse.ust.hk/~kwtleung/COMP4321/Movie/1.html
last_mod_date: 2023-05-16 05:03:16
size: 3605
keywords: dinosaur 28; titl 15; search 15; planet 12; movi 9; tv 7; match 7; result 6; imdb 5; episod 5
'''

# Sample data
page = [
    {
        "title": "Dinosaur Planet (2003)",
        "url": "https://www.cse.ust.hk/~kwtleung/COMP4321/Movie/1.html",
        "last_mod_date": "2023-05-16 05:03:16",
        "size": 3605,
        "keywords": {
            "dinosaur": 28,
            "title": 15,
            "search": 15,
            "planet": 12,
            "movie": 9,
            "tv": 7,
            "match": 7,
            "result": 6,
            "imdb": 5,
            "episode": 5
        }
    },
    # Add more movie data as needed
]

@app.route('/search')
def search():
    print("Sending data:", page)  # Debug log
    
    return jsonify(page)


if __name__ == '__main__':
    app.run(debug=True)