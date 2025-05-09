# Search Engine

## Introduction

This is a web-based search engine based on the Vector Space Model, built with Python 3.10, and React for the frontend

For more deails, please visit our report.

## Installation

Require Python >= 3.10 and nvm = 22

1. Download or clone this repo to your local device and cd into the directory
2. Create a virtual environment:

   - For Windows
     ```sh
     python -m venv venv
     ```
   - For Unix
     ```sh
     python3 -m venv venv
     ```

3. Activate the vm:
   - For Windows
     ```sh
     venv\Scripts\activate
     ```
   - For Unix
     ```sh
     source venv/bin/activate
     ```
4. Setup for backend server (Ensure there are not other server running on port 5000)
   - cd into `backend/`
   - Install the required dependencies from `requirements.txt`:
     ```sh
     pip install -r requirements.txt
     ```
   - Run the `craw_and_save.py`, it will crawl the webpages, perform indexing, and store them to database. This may takes 1-2 mins.
     - For Windows
       ```sh
       python crawl_and_save.py
       ```
     - For Unix
       ```sh
       python3 crawl_and_save.py
       ```
   - After that, run the `start_server.py`, to start the backend server powered by Flask
     - For Windows
       ```sh
       python start_server.py
       ```
     - For Unix
       ```sh
       python3 start_server.py
       ```
   - The server should be running on `http://127.0.0.1:5000/`
5. Now open another terminal for the frontend setup (Need not to be in the vm, and ensure no other server running on 5173)
   - cd into `frontend/`
   - If you don't have node js in your environment, you can install it here https://nodejs.org/en/download. In the download settings, choose version 22, your os, using nvm, and with npm
   - Confirm you have the right nvm version (22) by
     ```sh
        nvm use 22
     ```
     ```sh
        node -v #This should give v22.XX.XX
        nvm current #This should be same as above
        npm -v #This should be v10.9.2
     ```
   - Install the required packages by
     ```sh
         npm i
     ```
   - If there are no any dependencies issues, run
     ```sh
         npm run dev
     ```
   - The frontend server should be hosted at `http://localhost:5173/`
   - You can use the search engine there

## Clean up

Deactivate the python vm:

```sh
deactivate
```

## File Descriptions

### Frontend

- [main.tsx](./frontend/src/main.tsx)
  - Main file for React server
- [App.tsx](./frontend/src/App.tsx)
  - Web interface, basically all UI elements are implemented here

### Backend

- [/api](./backend/api/)
  - Contains the Flask API implementation, including routes and logic for handling search queries and other backend functionalities.
- [/crawler](./backend/crawler/)
  - Includes scripts for crawling web pages and saving the data for indexing.
- [/database](./backend/database/)
  - Manages database operations, including creating tables, inserting data, and computing statistics for search functionality.
- [/start_server](./backend/start_server/)
  - Script to start the Flask backend server.
- [/crawl_and_save](./backend/crawl_and_save/)
  - Orchestrates the crawling, indexing, and saving of web pages into the database.
