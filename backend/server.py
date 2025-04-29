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
pages = [
    {
        "score": 0.99999,
        "title": "Home Move (2001) sfasdfasdfsadfasdfasdfas",
        "link": "https://www.cse.hk.hk/alumni/2016-06-08",
        "last_modification_date": "2016-06-16T00:00:00Z",
        "file_size": "5931B",
        "keywords": { "CSE": "3", "MOV": "5", "TEST": "4" },
        "children_links": [
            "http://childlink1.com",
            "http://childlink2.com",
            "http://childlink3.com",
            "http://childlink1.com",
            "http://childlink2.com",
            "http://childlink3.com",
            "http://childlink1.com",
            "http://childlink2.com",
            "http://childlink3.com",
        ],
        "parent_links": [
            "http://parentlink1.com",
            "http://parentlink2.com",
            "http://parentlink3.com",
        ],
    },
    {
        "score": 0.87654,
        "title": "Home Research Paper on AI (2023)",
        "link": "https://ai-research.org/papers/2023",
        "last_modification_date": "2023-11-15T14:30:00Z",
        "file_size": "2.4MB",
        "keywords": { "AI": "8", "Machine Learning": "6", "Neural Networks": "5" },
        "children_links": [
            "https://ai-research.org/references/1",
            "https://ai-research.org/references/2"
        ],
        "parent_links": [
            "https://ai-research.org/main"
        ]
    },
    {
        "score": 0.25,
        "title": "Cooking Recipes Collection",
        "link": "https://food-blog.com/recipes",
        "last_modification_date": "2022-09-22T08:15:00Z",
        "file_size": "1.2MB",
        "keywords": { "Recipes": "10", "Cooking": "7", "Food": "5" },
        "children_links": [
            "https://food-blog.com/italian",
            "https://food-blog.com/asian",
            "https://food-blog.com/desserts"
        ],
        "parent_links": [
            "https://food-blog.com"
        ]
    },
    {
        "score": 0.55,
        "title": "Cooking Recipes Collection",
        "link": "https://food-blog.com/recipes",
        "last_modification_date": "2022-09-22T08:15:00Z",
        "file_size": "1.2MB",
        "keywords": { "Recipes": "10", "Cooking": "7", "Food": "5" },
        "children_links": [
            "https://food-blog.com/italian",
            "https://food-blog.com/asian",
            "https://food-blog.com/desserts"
        ],
        "parent_links": [
            "https://food-blog.com"
        ]
    },
    {
        "score": 0.98765,
        "title": "Home Annual Financial Report 2022",
        "link": "https://company.com/financials/2022",
        "last_modification_date": "2023-03-01T09:00:00Z",
        "file_size": "5.7MB",
        "keywords": { "Finance": "12", "Report": "8", "2022": "5" },
        "children_links": [],
        "parent_links": [
            "https://company.com/financials"
        ]
    },
    {
        "score": 0.01,
        "title": "Travel Guide: Japan 2021",
        "link": "https://travel-site.com/japan-guide",
        "last_modification_date": "2021-05-10T16:45:00Z",
        "file_size": "3.1MB",
        "keywords": { "Japan": "15", "Travel": "10", "Guide": "7" },
        "children_links": [
            "https://travel-site.com/japan/hotels",
            "https://travel-site.com/japan/transport"
        ],
        "parent_links": [
            "https://travel-site.com/guides",
            "https://travel-site.com/asia"
        ]
    }

]

suggestion_list = ["Movie", "Move", "Movement", "Movvvy", "Move", "Movement", "Movvvy"]

history_list = [
    {
        "query": "Dinosaur Planet",
        "timestamp": "2023-05-16T05:03:16Z"
    },
    {
        "query": "Research",
        "timestamp": "2023-11-15T14:30:00Z"
    },
    {
        "query": "Cooking Recipes",
        "timestamp": "2022-09-22T08:15:00Z"
    }
]

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    print(f"Received search query: {query}")
    filtered_pages = []
    for page in pages:
        if query in page['title'].lower() or query in page['link'].lower():
            filtered_pages.append(page)
    return jsonify(filtered_pages)

@app.route('/suggestions')
def suggestions():  
    return jsonify(suggestion_list)

@app.route('/history')
def history():  
    return jsonify(history_list)


if __name__ == '__main__':
    app.run(debug=True)