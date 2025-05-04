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

CREATE TABLE IF NOT EXISTS titles (
  title TEXT PRIMARY KEY
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

CREATE TABLE IF NOT EXISTS title_forward_index (
  url TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  FOREIGN KEY (url) REFERENCES urls (url)
);

CREATE TABLE IF NOT EXISTS title_inverted_index (
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  term_frequency INT NOT NULL,
  PRIMARY KEY (title, url),
  FOREIGN KEY (title) REFERENCES titles (title),
  FOREIGN KEY (url) REFERENCES urls (url)
);

CREATE TABLE IF NOT EXISTS word_statistics (
  word TEXT NOT NULL,
  url TEXT NOT NULL,
  tf_idf FLOAT NOT NULL,
  PRIMARY KEY (word, url),
  FOREIGN KEY (word) REFERENCES words (word),
  FOREIGN KEY (url) REFERENCES urls (url)
);

CREATE TABLE IF NOT EXISTS title_statistics (
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  tf_idf FLOAT NOT NULL,
  PRIMARY KEY (title, url),
  FOREIGN KEY (title) REFERENCES titles (title),
  FOREIGN KEY (url) REFERENCES urls (url)
);

CREATE TABLE IF NOT EXISTS page_rank (
  url TEXT PRIMARY KEY,
  rank FLOAT NOT NULL,
  FOREIGN KEY (url) REFERENCES urls (url)
);

CREATE TABLE IF NOT EXISTS page_stemmed_word (
  url TEXT NOT NULL,
  stemmed_word TEXT NOT NULL,
  PRIMARY KEY (url, stemmed_word),
  FOREIGN KEY (url) REFERENCES urls (url)
);

CREATE TABLE IF NOT EXISTS page_stemmed_title (
  url TEXT NOT NULL,
  stemmed_title TEXT NOT NULL,
  PRIMARY KEY (url, stemmed_title),
  FOREIGN KEY (url) REFERENCES urls (url)
);