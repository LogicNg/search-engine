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

CREATE TABLE IF NOT EXISTS words (
  word TEXT PRIMARY KEY
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
  FOREIGN KEY (word) REFERENCES words (word),
  FOREIGN KEY (url) REFERENCES urls (url)
);

CREATE TABLE IF NOT EXISTS keyword_statistics (
  word TEXT NOT NULL,
  url TEXT NOT NULL,
  tf_idf FLOAT NOT NULL,
  PRIMARY KEY (word, url),
  FOREIGN KEY (word) REFERENCES words (word),
  FOREIGN KEY (url) REFERENCES urls (url)
);