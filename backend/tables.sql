CREATE TABLE IF NOT EXISTS urls (
  url TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS page_relationships (
  parent_url TEXT NOT NULL,
  child_url TEXT NOT NULL,
  PRIMARY KEY (parent_url, child_url),
  FOREIGN KEY (parent_url) REFERENCES urls (url),
  FOREIGN KEY (child_url) REFERENCES urls (url)
);

--- This table stores the tokens (words) and their n-gram sizes.
CREATE TABLE IF NOT EXISTS tokens (
  word TEXT PRIMARY KEY,
  ngram_size INT
);

CREATE TABLE IF NOT EXISTS forward_index (
  url TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  last_modified_date TIMESTAMP NOT NULL,
  size INT NOT NULL,
  FOREIGN KEY (url) REFERENCES urls (url)
);

CREATE TABLE IF NOT EXISTS inverted_index (
  word TEXT NOT NULL,
  url TEXT NOT NULL,
  term_frequency INT NOT NULL,
  PRIMARY KEY (word, url),
  FOREIGN KEY (word) REFERENCES tokens (word),
  FOREIGN KEY (url) REFERENCES urls (url)
);

CREATE TABLE IF NOT EXISTS keyword_statistics (
  word TEXT NOT NULL,
  url TEXT NOT NULL,
  tf_idf FLOAT NOT NULL,
  PRIMARY KEY (word, url),
  FOREIGN KEY (word) REFERENCES tokens (word),
  FOREIGN KEY (url) REFERENCES urls (url)
);

CREATE TABLE IF NOT EXISTS page_rank (
  url TEXT PRIMARY KEY,
  rank FLOAT NOT NULL,
  FOREIGN KEY (url) REFERENCES urls (url)
);