from database.db import connection, cursor


def fetch_data():
    # Query to fetch all necessary data using CTEs
    query = """
    WITH keyword_data AS (
        SELECT 
            url, 
            GROUP_CONCAT(word || ' ' || term_frequency, '; ' ORDER BY term_frequency DESC) AS keywords
        FROM 
            inverted_index
        GROUP BY 
            url
    ),
    child_link_data AS (
        SELECT 
            parent_url, 
            GROUP_CONCAT(child_url, '; ' ORDER BY child_url) AS child_links
        FROM 
            page_relationships
        GROUP BY 
            parent_url
    )
    SELECT 
        fi.url, 
        fi.title, 
        fi.last_modified_date, 
        fi.size, 
        kd.keywords,
        cld.child_links
    FROM 
        forward_index fi
    LEFT JOIN 
        keyword_data kd ON fi.url = kd.url
    LEFT JOIN 
        child_link_data cld ON fi.url = cld.parent_url
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
        if child_links:
            entry += "\n".join(child_links) + "\n"
        entry += "\n" + "-" * 30 + "\n"  # Separator line
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
