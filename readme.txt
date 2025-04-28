# Search Engine

## Installation


Require Python >= 3.10

Create a virtual environment:

```sh
python -m venv venv
```

Activate the vm:


- Windows: `venv\Scripts\activate`
- Mac/Linus: `source venv/bin/activate`

Install the required dependencies from `requirements.txt`:

```sh
pip install -r requirements.txt
```

# Phase 2
Open 2 terminals

# Start backend server on one
`cd backend`
`python3 server.py`

# Start frontend on the other
`cd frontend`
`npm i`
`npm run dev`

# View the app
Open your browser and navigate to `http://localhost:5173/` to view the app.

////////////////////////////////////////////////////////////////////////////////////////////////////////
## Main Script

Run the main script:

```sh
python main.py
```

The script does the following things:

1. Creates the necessary database tables in `documents.db`.
2. Fetches and saves web pages starting from a specified base URL.
3. Generates a `spider_result.txt` file containing the fetched and indexed data.

## Clean up

Deactivate the vm:


```sh
deactivate
```


## DB design

Take a look at tables.sql for the database schema. Here is a brief overview of the tables:

| Table              | Purpose                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------ |
| urls               | Stores unique URLs                                                                         |
| page_relationships | Captures the relationships between pages                                                   |
| words              | Stores unique words                                                                        |
| forward_index      | Stores metadata about each URL, such as the title, last modified date, and size            |
| inverted_index     | Maps words to URLs, along with the term frequency of each word in the URL                  |
| keyword_statistics | Stores the TF-IDF (Term Frequency-Inverse Document Frequency) score for each word-URL pair |

