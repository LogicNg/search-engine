import math
from flask import Blueprint, jsonify, request
from nltk.stem import PorterStemmer
from collections import Counter, defaultdict
import re

from api.utils.get_cursor import get_cursor
from api.utils.levenshtein_distance import levenshtein_distance

# For some reason i cannot use get_cursor
#cursor = get_cursor()

from database.db import connection, cursor


search_bp = Blueprint("search", __name__)

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
        #remove any double quotation
        word = word.replace('"', "")
        
        processed_word = re.sub(r"[^a-zA-Z-]+", "", word.lower())
        if processed_word in stop_words:
            continue
        stemmed_word = stemmer.stem(word)
        print(f"input word: {word}, stemmed word: {stemmed_word}")
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

def getPageDetails(url, score):
    # Get the page details
    '''
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
    }
    '''
    #5 decimal places
    score = "{:.5f}".format(score)
    page_details = cursor.execute(
        """SELECT title, last_modified_date, size FROM forward_index WHERE url = ?""",
        (url,),
    ).fetchone()
    
    #Get top 5 stemmed keyword from the page (from inverted_index and title_inverted_index)
    content_keywords = cursor.execute(
        """SELECT word, term_frequency FROM inverted_index WHERE url = ? ORDER BY term_frequency DESC""",
        (url,),
    ).fetchall()
    
    title_keywords = cursor.execute(
        """SELECT title, term_frequency FROM title_inverted_index WHERE url = ? ORDER BY term_frequency DESC""",
        (url,),
    ).fetchall()
    
    
    #print(f"Content keywords: {content_keywords}")
    #print(f"Title keywords: {title_keywords}")
    # Combine 2 lists and form a dict, then extract the top 5
    keywords = {}
    for word, tf in content_keywords:
        keywords[word] = tf
    for title, tf in title_keywords:
        if title in keywords:
            keywords[title] += tf
        else:
            keywords[title] = tf 
            
    sorted_keywords = sorted(keywords.items(), key=lambda item: item[1], reverse=True) 
    top_keywords = sorted_keywords[:5]
    
    dictkeyword = {word: str(tf) for word, tf in top_keywords} 
    
    # Get parent and children links
    children_links = cursor.execute(
        """SELECT child_url FROM page_relationships WHERE parent_url = ?""",
        (url,),
    ).fetchall()
    
    parent_links = cursor.execute(
        """SELECT parent_url FROM page_relationships WHERE child_url = ?""",
        (url,),
    ).fetchall()
    
    children_links = [child[0] for child in children_links]
    parent_links = [parent[0] for parent in parent_links]
    
    if page_details:
        title, last_modified_date, size = page_details
        return {
            "score": score,  # Placeholder for score
            "title": title,
            "link": url,
            "last_modification_date": last_modified_date,
            "file_size": f"{size}B",
            "keywords": dictkeyword,
            "children_links": children_links,
            "parent_links": parent_links,
        }
    else:
        return None

@search_bp.route("/search")
def search():
    #print(f"Received search request")
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
    top_results = list(combined_similarity.items())[:50] 
    #Show the top result, and the score should be in float with 10 decimal places
    result = []
    for url, score in top_results:
        # Get the page details
        print(f"{url}: {score:.10f}")
            # Add keywords, children links, and parent links
    
        result.append(getPageDetails(url, score))
        
    
    return jsonify(result)