from database.db import connection, cursor


def fetch_data():
    # Query to fetch all necessary data
    query = """
    SELECT 
        fi.url, 
        fi.title, 
        fi.last_modified_date, 
        fi.size, 
        GROUP_CONCAT(ii.word || ' ' || ii.term_frequency, '; ') AS keywords,
        GROUP_CONCAT(pr.child_url, '; ') AS child_links
    FROM 
        forward_index fi
    LEFT JOIN 
        inverted_index ii ON fi.url = ii.url
    LEFT JOIN 
        page_relationships pr ON fi.url = pr.parent_url
    GROUP BY 
        fi.url
    """
    cursor.execute(query)
    return cursor.fetchall()


def format_data(data):
    formatted_data = []
    for row in data:
        url, title, last_modified_date, size, keywords, child_links = row
        # Format the keywords and child links
        keywords = keywords.split("; ")[:10] if keywords else []
        child_links = child_links.split("; ")[:10] if child_links else []

        # Format the entry
        entry = f"{title}\n{url}\n{last_modified_date}, {size}\n"
        entry += "; ".join(keywords) + "\n"
        entry += "\n".join(child_links) + "\n"
        entry += "-" * 30  # Separator line
        formatted_data.append(entry)
    return formatted_data


def write_to_file(formatted_data):
    with open("spider_result.txt", "w") as file:
        for entry in formatted_data:
            file.write(entry + "\n")


def make_spider_result_txt():
    data = fetch_data()
    formatted_data = format_data(data)
    write_to_file(formatted_data)
