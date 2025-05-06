import math
import re
from collections import Counter, defaultdict

from flask import Blueprint, jsonify, request
from nltk.stem import PorterStemmer

from api.utils.get_cursor import get_cursor
from api.utils.levenshtein_distance import levenshtein_distance
from database.db import connection, cursor


get_stemmed_word_bp = Blueprint("get_stemmed_word", __name__)


@get_stemmed_word_bp.route("/get_stemmed_word")
def suggestions():
    '''
        Return a list of ALL stemmed word from the database inverted_index table.
    '''
    
    all_stemmed_words = cursor.execute("SELECT word FROM words").fetchall()
    
    
    # Convert the list of tuples to a list of strings
    all_stemmed_words = [word[0] for word in all_stemmed_words]
    
    
    
    return jsonify(all_stemmed_words)