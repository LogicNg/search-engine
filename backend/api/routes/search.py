from flask import Blueprint, jsonify, request
from collections import defaultdict
from nltk.stem import PorterStemmer
import sqlite3
import re
from collections import Counter
from database.db import connection, cursor

search_bp = Blueprint("search", __name__)

# sample data
"""
title: Dinosaur Planet (2003)
url: https://www.cse.ust.hk/~kwtleung/COMP4321/Movie/1.html
last_mod_date: 2023-05-16 05:03:16
size: 3605
keywords: dinosaur 28; titl 15; search 15; planet 12; movi 9; tv 7; match 7; result 6; imdb 5; episod 5
"""

# Sample data
pages = [
    {
        "score": 0.99999,
        "title": "Home Move (2001) sfasdfasdfsadfasdfasdfas",
        "link": "https://www.cse.hk.hk/alumni/2016-06-08",
        "last_modification_date": "2016-06-16T00:00:00Z",
        "file_size": "5931B",
        "keywords": {"CSE": "3", "MOV": "5", "TEST": "4"},
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
        "keywords": {"AI": "8", "Machine Learning": "6", "Neural Networks": "5"},
        "children_links": [
            "https://ai-research.org/references/1",
            "https://ai-research.org/references/2",
        ],
        "parent_links": ["https://ai-research.org/main"],
    },
    {
        "score": 0.25,
        "title": "Cooking Recipes Collection",
        "link": "https://food-blog.com/recipes",
        "last_modification_date": "2022-09-22T08:15:00Z",
        "file_size": "1.2MB",
        "keywords": {"Recipes": "10", "Cooking": "7", "Food": "5"},
        "children_links": [
            "https://food-blog.com/italian",
            "https://food-blog.com/asian",
            "https://food-blog.com/desserts",
        ],
        "parent_links": ["https://food-blog.com"],
    },
    {
        "score": 0.55,
        "title": "Cooking Recipes Collection",
        "link": "https://food-blog.com/recipes",
        "last_modification_date": "2022-09-22T08:15:00Z",
        "file_size": "1.2MB",
        "keywords": {"Recipes": "10", "Cooking": "7", "Food": "5"},
        "children_links": [
            "https://food-blog.com/italian",
            "https://food-blog.com/asian",
            "https://food-blog.com/desserts",
        ],
        "parent_links": ["https://food-blog.com"],
    },
    {
        "score": 0.98765,
        "title": "Home Annual Financial Report 2022",
        "link": "https://company.com/financials/2022",
        "last_modification_date": "2023-03-01T09:00:00Z",
        "file_size": "5.7MB",
        "keywords": {"Finance": "12", "Report": "8", "2022": "5"},
        "children_links": [],
        "parent_links": ["https://company.com/financials"],
    },
    {
        "score": 0.01,
        "title": "Travel Guide: Japan 2021",
        "link": "https://travel-site.com/japan-guide",
        "last_modification_date": "2021-05-10T16:45:00Z",
        "file_size": "3.1MB",
        "keywords": {"Japan": "15", "Travel": "10", "Guide": "7"},
        "children_links": [
            "https://travel-site.com/japan/hotels",
            "https://travel-site.com/japan/transport",
        ],
        "parent_links": [
            "https://travel-site.com/guides",
            "https://travel-site.com/asia",
        ],
    },
]

title_match_weight = 0.7
keyword_match_weight = 0.3


stop_words = []
with open("./database/stopwords.txt", "r") as f:
    stop_words = set(f.read().split())
    
stemmer = PorterStemmer()
title_index = defaultdict(list)
body_index = defaultdict(list)

def parse_query(query):
    """
    Parse query into single word and phrases, the remove stop words and stem the keywords.
    """
    
    word_list = []
    phrase_list = []
    
    # Handle single words
    for word in query.split():
        processed_word = re.sub(r"[^a-zA-Z-]+", "", word.lower())
        if processed_word in stop_words:
            continue
        stemmed_word = stemmer.stem(word)
        word_list.append(stemmed_word)
        
    # Remove double quotation for words in word_list
    word_list = [word.replace('"', "") for word in word_list]   
    
    # Handle phrases
    phrase_pattern = re.compile(r'"([^"]*)"')
    phrases = phrase_pattern.findall(query)
    for phrase in phrases:
        phrase_word = phrase.split()
        processed_phrase_word = []
        for word in phrase_word:
            word = word.lower()
            if word not in stop_words:
                stemmed_word = stemmer.stem(word)
                processed_phrase_word.append(stemmed_word)
                
        processed_phrase_word = " ".join(processed_phrase_word)        
        processed_stemmed_phrase = r"(?<!\S){}(?!\S)".format(processed_phrase_word)
        phrase_list.append(processed_stemmed_phrase)
    
    return [word_list, phrase_list]
    
def get_tf_score(query):
    word_tf = Counter(query)
    vector = {}
    #output as {"word": tf, ...}
    for word, tf in list(word_tf.items()): 
        vector[word] = tf
        
    return vector



def checkIfInDocument(url, query_vector):
    title = cursor.execute(
        """SELECT stemmed_title FROM page_stemmed_title WHERE url = ?""",
        (url,),
    ).fetchone()[0]
    
    content = cursor.execute(
        """SELECT stemmed_word FROM page_stemmed_word WHERE url = ?""",
        (url,),
    ).fetchone()[0]
    
    # Turn to a list
    title = title.split()
    content = content.split()
    
    for word in query_vector:
        # Check if the word is in the title 
        if word in title or word in content: 
            return True
    
    return False

def checkIfPhraseInDocument(url, phrase_vector): 
    title = cursor.execute(
        """SELECT stemmed_title FROM page_stemmed_title WHERE url = ?""",
        (url,),
    ).fetchone()[0]
    
    content = cursor.execute(
        """SELECT stemmed_word FROM page_stemmed_word WHERE url = ?""",
        (url,),
    ).fetchone()[0]
     
    
    # Turn to a list
    #title = title.split()
    #content = content.split()
    
    for phrase in phrase_vector:
        # Check if the word is in the title 
        if re.search(phrase, title):
            #print(f"Found phrase: {phrase} in {url}")
            return True
        if re.search(phrase, content):
            #print(f"Found phrase: {phrase} in {url}")
            return True
    
    return False
    
def computeCosineSimilarity(document_vector, query_vector):
    # both document_vector and query_vector are dict
    
    if len(document_vector) == 0 or len(query_vector) == 0:
        return 0.0
    
    # Remove unmatched words
    mathced_document_vector = {}
    for key, value in document_vector.items():
        if key in query_vector:
            mathced_document_vector[key] = value
    
    matched_query_vector = {}
    for key, value in query_vector.items():
        if key in document_vector:
            matched_query_vector[key] = value
    
    # Compute cosine similarity
    dot_product = sum(mathced_document_vector[word] * matched_query_vector[word] for word in matched_query_vector)
    magnitude_document = sum(value ** 2 for value in document_vector.values()) ** 0.5
    
    # IDK there will be divide by 0 
    if magnitude_document == 0:
        return 0.0
    
    return dot_product / magnitude_document

def getDocumentContentVector(url):
    document_vector = {}
    # Get all words and their tf_idf
    word_and_tfidf = cursor.execute(
                        """SELECT word, tf_idf FROM word_statistics WHERE url = ?""",
                        (url,),
                    )

    for word, tf_idf in word_and_tfidf:
        document_vector[word] = tf_idf
    
    return document_vector

def getDocumentTitleVector(url):
    document_vector = {}
    # Get all words and their tf_idf
    word_and_tfidf = cursor.execute(
                        """SELECT title, tf_idf FROM title_statistics WHERE url = ?""",
                        (url,),
                    )

    for word, tf_idf in word_and_tfidf:
        document_vector[word] = tf_idf
    
    return document_vector



@search_bp.route("/search")
def search():
    query = request.args.get("query", "").lower()
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    parsed_query = parse_query(query)
    #print(f"Parsed query: {parsed_query}")
    
    # Count tf of each query word
    query_vector = get_tf_score(parsed_query[0])
    #print(f"Query vector: {query_vector}")
    
    all_documents = cursor.execute("""SELECT url FROM urls""").fetchall()
    
    # Store each document's title and body similarity score for retrieval
    title_similarity = {}
    content_similarity = {}
    
    for document in all_documents:
        url = document[0]
        #print(f"Processing {url}")
        
        if (parsed_query[1]): #have phrase
            # Check if the phrase is in the document
            if not checkIfPhraseInDocument(url, parsed_query[1]):
                continue
        else:
            if not checkIfInDocument(url, parsed_query[0]): 
                continue
        
        #compute cosine similarity
        
        #Get document vector
        document_title_vector = getDocumentTitleVector(url)
        document_content_vector = getDocumentContentVector(url)
        
        title_similarity[url] = computeCosineSimilarity(document_title_vector, query_vector)
        content_similarity[url] = computeCosineSimilarity(document_content_vector, query_vector)
        
        #print(f"Title similarity for {url}: {title_similarity[url]}")
        #print(f"Content similarity for {url}: {content_similarity[url]}")
        #print("=" * 20)
        
    # Sort the 2 dict
    title_similarity = dict(sorted(title_similarity.items(), key=lambda item: item[1], reverse=True))
    content_similarity = dict(sorted(content_similarity.items(), key=lambda item: item[1], reverse=True))
    
    
    # Combine the two similarity scores
    combined_similarity = {}
    
    for url in title_similarity:
        if url in combined_similarity:
            combined_similarity[url] += title_match_weight * title_similarity[url] 
        else:
            combined_similarity[url] = title_match_weight * title_similarity[url]
            
    for url in content_similarity:
        if url not in combined_similarity:
            combined_similarity[url] = keyword_match_weight * content_similarity[url]
        else:
            combined_similarity[url] += keyword_match_weight * content_similarity[url]
        
        
        
    combined_similarity = dict(sorted(combined_similarity.items(), key=lambda item: item[1], reverse=True)) 
    
    # Get the top 10 results
    top_results = list(combined_similarity.items())[:10] 
    #Show the top result, and the score should be in float with 10 decimal places
    result = []
    for url, score in top_results:
        # Get the page details
        print(f"{url}: {score:.10f}")
            # Add keywords, children links, and parent links
    

    # Parse the query into keywords
    return jsonify([])
