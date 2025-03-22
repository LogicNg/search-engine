import re
from collections import defaultdict

#from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


class Indexer:
    def __init__(self):
        """Initialize the Indexer with stopwords and a stemmer."""

        self.stop_words = None
        with open('database/stopwords.txt', 'r') as file:
            self.stop_words = file.read().split()

        #self.stop_words = set(stopwords.words("english"))
        self.stemmer = PorterStemmer()
        self.body_index = defaultdict(list)
        self.title_index = defaultdict(list)

    def tokenize(self, text):
        """
        Tokenize the input text by removing punctuation, splitting by whitespace,
        and filtering out stopwords.

        Args:
            text (str): The input text to tokenize.

        Returns:
            list: A list of tokens.
        """
        tokens = re.findall(r"\b\w+\b", text.lower())
        return [token for token in tokens if token not in self.stop_words]

    def stem(self, tokens):
        """
        Stem a list of tokens using the Porter Stemmer.

        Args:
            tokens (list): A list of tokens to stem.

        Returns:
            list: A list of stemmed tokens.
        """
        return [self.stemmer.stem(token) for token in tokens]

    def index_page(self, page_id, title, body):
        """
        Index a webpage by tokenizing and stemming its title and body text.

        Args:
            page_id (str): The unique identifier (URL) of the page.
            title (str): The title of the page.
            body (str): The body text of the page.
        """
        title_tokens = self.tokenize(title)
        body_tokens = self.tokenize(body)

        title_stems = self.stem(title_tokens)
        body_stems = self.stem(body_tokens)

        # Index title stems
        for stem in title_stems:
            self.title_index[stem].append(page_id)

        # Index body stems
        for stem in body_stems:
            self.body_index[stem].append(page_id)
